"""Rotas do associado (ESPECIFICACAO, seção 17.4; Issue #94).

Início, extrato, detalhe, simular compra e contestação. Só o papel ``associado`` entra, e
nada técnico (sinais, nota, contribuições, parecer da IA) sai por aqui.
"""

from __future__ import annotations

from typing import Annotated, Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from src.api import auditorias as auditoria_mem
from src.api import servicos
from src.api.esquemas_refatoracao import (
    CompraSimuladaSchema,
    ContestacaoSchema,
    DetalheCompraSchema,
    EntradaCompraSimulada,
    ExtratoSchema,
    InicioSchema,
)
from src.api.sessao import obter_repositorios, sessao_com_papel
from src.aplicacao import associado as associado_app
from src.associado import chat
from src.dominio.entidades import Perfil

router = APIRouter(prefix="/api/associado", tags=["associado"])
Sessao = Annotated[Perfil, Depends(sessao_com_papel("associado"))]


def _erro_http(erro: Exception) -> HTTPException:
    """Traduz os erros dos casos de uso nos códigos do contrato."""
    if isinstance(erro, associado_app.NaoEncontrado):
        return HTTPException(status_code=404, detail=str(erro))
    if isinstance(erro, associado_app.Conflito):
        return HTTPException(status_code=409, detail=str(erro))
    return HTTPException(status_code=422, detail=str(erro))


@router.get("/inicio", response_model=InicioSchema)
def inicio(perfil: Sessao) -> dict[str, Any]:
    """Saldo, limites, cartões, avisos pendentes e últimas compras do associado."""
    try:
        return associado_app.ver_inicio(obter_repositorios(), perfil.id_perfil)
    except associado_app.NaoEncontrado as erro:
        raise _erro_http(erro) from erro


@router.get("/extrato", response_model=ExtratoSchema)
def extrato(
    perfil: Sessao,
    situacao: str | None = Query(default=None, description="Situações separadas por vírgula."),
) -> dict[str, Any]:
    """Extrato do associado, da compra mais recente para a mais antiga."""
    try:
        return associado_app.ver_extrato(obter_repositorios(), perfil.id_perfil, situacao)
    except (associado_app.NaoEncontrado, ValueError) as erro:
        raise _erro_http(erro) from erro


@router.get("/compras/{id_compra}", response_model=DetalheCompraSchema)
def detalhe_da_compra(id_compra: str, perfil: Sessao) -> dict[str, Any]:
    """Detalhe de uma compra do próprio associado; de outro associado → 404."""
    try:
        return associado_app.ver_compra(obter_repositorios(), perfil.id_perfil, id_compra)
    except associado_app.NaoEncontrado as erro:
        raise _erro_http(erro) from erro


def _iniciar_auditoria(transacao: dict[str, Any], analise: dict[str, Any]) -> str:
    """Registra a auditoria como pendente e dispara a IA em segundo plano; devolve o id."""
    id_auditoria = uuid4().hex
    auditoria_mem.registrar_auditoria(
        id_auditoria,
        {
            "id_auditoria": id_auditoria,
            "status": "pendente",
            "relatorio": None,
            "latencia_ms": None,
            "mensagem": None,
        },
    )
    auditoria_mem.disparar_auditoria_em_segundo_plano(id_auditoria, transacao, analise)
    return id_auditoria


@router.post("/compras", status_code=201, response_model=CompraSimuladaSchema)
def simular_compra(entrada: EntradaCompraSimulada, perfil: Sessao) -> dict[str, Any]:
    """Passa a compra pelo Sentinela: aprova, pede confirmação ou bloqueia na hora."""
    if not servicos.modelo_carregado():
        raise HTTPException(
            status_code=503, detail="Modelo não carregado. Rode: python -m src.treinar_modelo"
        )
    repos = obter_repositorios()
    try:
        compra, transacao, analise = associado_app.simular_compra(
            repos, perfil.id_perfil, entrada.model_dump(), servicos.analisar_transacao
        )
    except (associado_app.NaoEncontrado, associado_app.Conflito) as erro:
        raise _erro_http(erro) from erro
    # A filial consulta a auditoria desta compra pelo id guardado junto da análise.
    analise["id_auditoria"] = _iniciar_auditoria(transacao, analise)
    return {
        "compra": associado_app.compra_para_extrato(repos, compra),
        "id_notificacao": compra.id_notificacao,
    }


@router.post("/compras/{id_compra}/contestacao", status_code=201, response_model=ContestacaoSchema)
def contestar(id_compra: str, perfil: Sessao) -> dict[str, Any]:
    """Aplica "Não reconheço esta compra": bloqueia o cartão e devolve o valor; só numa APROVADA."""
    repos = obter_repositorios()
    try:
        compra, cartao = associado_app.contestar_compra(repos, perfil.id_perfil, id_compra)
    except (associado_app.NaoEncontrado, associado_app.Conflito) as erro:
        raise _erro_http(erro) from erro
    return {
        "compra": associado_app.compra_para_extrato(repos, compra),
        "cartao": associado_app.cartao_para_dict(cartao),
    }


# --- Chat do associado (seção 17.6; Issue #105) -----------------------------------------------


class MensagemChat(BaseModel):
    """Uma fala da conversa guardada pelo site."""

    autor: str = Field(pattern="^(associado|ia)$")
    texto: str = Field(max_length=2000)


class EntradaChat(BaseModel):
    """Entrada de ``POST /api/associado/chat``."""

    mensagem: str = Field(min_length=1, max_length=500)
    historico: list[MensagemChat] = Field(default_factory=list, max_length=chat.MAX_HISTORICO)


class EntradaChatGerente(BaseModel):
    """Entrada de ``POST /api/associado/chat/gerente``."""

    historico: list[MensagemChat] = Field(default_factory=list, max_length=chat.MAX_HISTORICO)


class RespostaChat(BaseModel):
    """Saída de ``POST /api/associado/chat``."""

    resposta: str
    fonte: str


class GerenteSchema(BaseModel):
    """Gerente da agência do associado."""

    nome: str


class RespostaChatGerente(BaseModel):
    """Saída de ``POST /api/associado/chat/gerente``."""

    gerente: GerenteSchema
    resumo: str


def _contexto_do_chat(id_associado: str) -> dict[str, Any]:
    """Só dados do próprio associado: saldo, limite e as compras do extrato."""
    repos = obter_repositorios()
    try:
        inicio = associado_app.ver_inicio(repos, id_associado)
        extrato = associado_app.ver_extrato(repos, id_associado, None)
    except associado_app.NaoEncontrado as erro:
        raise _erro_http(erro) from erro
    return {
        "saldo": inicio["saldo"],
        "limite_disponivel": inicio["limite_disponivel"],
        "compras": extrato["itens"],
    }


@router.post("/chat", response_model=RespostaChat)
def conversar(entrada: EntradaChat, perfil: Sessao) -> dict[str, str]:
    """A IA responde sobre os gastos e as compras do associado; só informa."""
    historico = [m.model_dump() for m in entrada.historico]
    return chat.responder(entrada.mensagem, historico, _contexto_do_chat(perfil.id_perfil))


@router.post("/chat/gerente", response_model=RespostaChatGerente)
def conversar_com_gerente(entrada: EntradaChatGerente, perfil: Sessao) -> dict[str, Any]:
    """Abre a conversa (simulada) com o gerente da agência, com o resumo até ali."""
    repos = obter_repositorios()
    gerente = next(
        (
            p
            for p in repos.perfis.listar()
            if p.papel == "gerente" and p.id_filial == perfil.id_filial
        ),
        None,
    )
    historico = [m.model_dump() for m in entrada.historico]
    return {
        "gerente": {"nome": gerente.nome if gerente else "Gerente da agência"},
        "resumo": chat.resumir_para_gerente(historico, _contexto_do_chat(perfil.id_perfil)),
    }
