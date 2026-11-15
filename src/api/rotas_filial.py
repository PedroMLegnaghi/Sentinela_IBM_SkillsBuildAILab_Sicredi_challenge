"""Rotas da filial (ESPECIFICACAO, seção 17.4; Issue #96): fila do auditor e detalhe da compra.

Auditor e gerente veem só a carteira da própria filial. A fila de demonstração é registrada
como compras na primeira chamada; análise, auditoria e histórico vêm de ``servicos``.
"""

from __future__ import annotations

import math
import threading
from datetime import timedelta
from typing import Annotated, Any

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from src.api import auditorias as auditoria_mem
from src.api import servicos
from src.api.esquemas_refatoracao import (
    DetalheFilialSchema,
    FilaFilialSchema,
    MetricasFilialSchema,
)
from src.api.sessao import obter_repositorios, sessao_com_papel
from src.aplicacao import associado as associado_app
from src.aplicacao import filial as filial_app
from src.aplicacao import metricas_filial
from src.associado import notificacoes
from src.config import FIM_TESTE, INICIO_TESTE
from src.dominio.entidades import Compra, Perfil
from src.dominio.regras import filial_da_posicao as regras_filial_da_posicao
from src.portas.repositorios import Repositorios

router = APIRouter(prefix="/api/filial", tags=["filial"])
Equipe = Annotated[Perfil, Depends(sessao_com_papel("auditor", "gerente"))]
Gerente = Annotated[Perfil, Depends(sessao_com_papel("gerente"))]
Auditor = Annotated[Perfil, Depends(sessao_com_papel("auditor"))]
MAXIMO_NOTA = 300
DIAS_DO_HISTORICO = 90
_lock = threading.Lock()
_ids_fila: set[int] | None = None
_resumo_marco: dict[str, metricas_filial.ResumoFilial] | None = None


def _valor(valor: Any) -> Any:
    """NaN vira None; Timestamp vira texto ISO; o resto passa."""
    if isinstance(valor, pd.Timestamp):
        return None if pd.isna(valor) else valor.strftime("%Y-%m-%dT%H:%M:%S")
    if isinstance(valor, float) and (math.isnan(valor) or math.isinf(valor)):
        return None
    return valor


def _linhas_da_fila() -> list[dict[str, Any]]:
    """Linhas da fila de demonstração, só com as colunas que a carteira usa."""
    fila = servicos._estado.fila  # noqa: SLF001 (fila montada na subida da API)
    if fila is None:
        return []
    colunas = [
        "id_transacao",
        "id_cliente",
        "id_cartao",
        "nota",
        "decisao",
        "valor",
        "data_hora",
        "tipo_transacao",
        "modalidade_transacao",
    ]
    presentes = [c for c in colunas if c in fila.columns]
    return [
        {chave: _valor(valor) for chave, valor in linha.items()}
        for linha in fila[presentes].to_dict("records")
    ]


def _repositorios_com_fila() -> tuple[Repositorios, set[int]]:
    """Repositórios com a fila de demonstração já registrada (uma vez por processo)."""
    global _ids_fila  # noqa: PLW0603 (cache de processo, como os demais estados da API)
    repos = obter_repositorios()
    with _lock:
        if _ids_fila is None:
            linhas = _linhas_da_fila()
            filial_app.registrar_fila_de_marco(repos, linhas)
            _ids_fila = {int(linha["id_transacao"]) for linha in linhas}
        return repos, _ids_fila


def _auditoria_de(compra: Compra) -> dict[str, Any] | None:
    """Auditoria da compra: a da fila (``trans_<id>``) ou a disparada na simulação."""
    if compra.simulada:
        id_auditoria = (compra.analise or {}).get("id_auditoria")
        return auditoria_mem.obter_auditoria(id_auditoria) if id_auditoria else None
    return auditoria_mem.obter_auditoria(f"trans_{compra.id_transacao_base}")


def _analise_da_base(id_transacao: int) -> dict[str, Any]:
    """Analise de uma transação de março: pela fila de demonstração ou, fora dela, pela base."""
    try:
        return servicos.obter_transacao(id_transacao)["analise"]
    except KeyError:
        return servicos.analisar_transacao(servicos.transacao_para_auditoria(id_transacao))


def _analise_de(compra: Compra) -> dict[str, Any]:
    """Analise (seção 12) da compra; para as de março, dispara a auditoria se ainda não existe."""
    if compra.simulada:
        return {k: v for k, v in (compra.analise or {}).items() if k != "id_auditoria"}
    id_transacao = -1 if compra.id_transacao_base is None else int(compra.id_transacao_base)
    try:
        analise = _analise_da_base(id_transacao)
    except (KeyError, RuntimeError) as erro:
        raise HTTPException(
            status_code=503, detail="Dados não carregados. Rode: python -m src.preparar_dados"
        ) from erro
    id_auditoria = f"trans_{id_transacao}"
    if auditoria_mem.obter_auditoria(id_auditoria) is None:
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
        auditoria_mem.disparar_auditoria_em_segundo_plano(
            id_auditoria, servicos.transacao_para_auditoria(id_transacao), analise
        )
    return analise


def _historico_de(repos: Repositorios, compra: Compra) -> tuple[int, float | None]:
    """Compras do cliente nos 90 dias antes desta e a mediana de valor delas, pela base."""
    base = servicos._estado.base  # noqa: SLF001
    associado = repos.associados.obter(compra.id_associado)
    momento = pd.to_datetime(compra.data_hora, errors="coerce")
    if base is None or associado is None or associado.id_cliente_base is None or pd.isna(momento):
        return 0, None
    do_cliente = base[base["id_cliente"] == associado.id_cliente_base]
    janela = do_cliente[
        (do_cliente["data_hora"] >= momento - timedelta(days=DIAS_DO_HISTORICO))
        & (do_cliente["data_hora"] < momento)
    ]
    mediana = janela["valor"].median()
    return int(len(janela)), None if pd.isna(mediana) else round(float(mediana), 2)


@router.get("/fila", response_model=FilaFilialSchema)
def fila(
    perfil: Equipe,
    situacao: str | None = Query(default=None, description="Situações separadas por vírgula."),
) -> dict[str, Any]:
    """Fila da filial: só a carteira da agência da sessão, por nota decrescente."""
    repos, ids_fila = _repositorios_com_fila()
    try:
        return filial_app.ver_fila(repos, perfil.id_filial, situacao, ids_fila, _auditoria_de)
    except ValueError as erro:
        raise HTTPException(status_code=422, detail=str(erro)) from erro


@router.get("/compras/{id_compra}", response_model=DetalheFilialSchema)
def compra(id_compra: str, perfil: Equipe) -> dict[str, Any]:
    """Detalhe técnico da compra; de outra filial → 403; inexistente → 404."""
    repos, _ = _repositorios_com_fila()
    try:
        return filial_app.ver_compra(
            repos,
            perfil.id_filial,
            id_compra,
            _analise_de,
            _auditoria_de,
            lambda c: _historico_de(repos, c),
        )
    except associado_app.NaoEncontrado as erro:
        raise HTTPException(status_code=404, detail=str(erro)) from erro
    except filial_app.AcessoNegado as erro:
        raise HTTPException(status_code=403, detail=str(erro)) from erro


def _filial_por_cliente(repos: Repositorios) -> dict[str, str]:
    """``id_cliente`` da base → filial da carteira (login pela alternação; demais pela posição)."""
    return {
        associado.id_cliente_base: associado.id_filial
        for id_filial in filial_app.FILIAIS
        for associado in repos.associados.listar_por_filial(id_filial)
        if associado.id_cliente_base
    }


def _linhas_de_marco(repos: Repositorios) -> list[dict[str, Any]]:
    """Todas as transações de março com a decisão do modelo e a filial da carteira.

    As poucas linhas sem cliente vão para uma filial pela paridade do ``id_transacao``, para a
    soma das duas filiais dar os números da seção 11.
    """
    base = servicos._estado.base  # noqa: SLF001
    agente = servicos._estado.agente  # noqa: SLF001
    if base is None or agente is None:
        return []
    marco = base[(base["data_hora"] >= INICIO_TESTE) & (base["data_hora"] < FIM_TESTE)]
    decididas = agente.analisar_lote(marco)
    por_cliente = _filial_por_cliente(repos)
    clientes = decididas["id_cliente"].astype("string")
    paridade = decididas["id_transacao"].astype(int).map(regras_filial_da_posicao)
    filiais = clientes.map(por_cliente).fillna(paridade)
    colunas = ["decisao", "valor", "tipo_transacao", "modalidade_transacao"]
    return [
        {"id_filial": id_filial, **{k: _valor(v) for k, v in linha.items()}}
        for id_filial, linha in zip(filiais, decididas[colunas].to_dict("records"), strict=True)
    ]


def _resumos_de_marco(repos: Repositorios) -> dict[str, metricas_filial.ResumoFilial]:
    """Resumo de março por filial, calculado uma vez por processo."""
    global _resumo_marco  # noqa: PLW0603 (cache de processo, como os demais estados da API)
    with _lock:
        if _resumo_marco is None:
            _resumo_marco = metricas_filial.resumir_marco(_linhas_de_marco(repos))
        return _resumo_marco


@router.get("/metricas", response_model=MetricasFilialSchema)
def metricas(perfil: Gerente) -> dict[str, Any]:
    """Painel do gerente: março da carteira mais as compras e respostas ao vivo."""
    repos, _ = _repositorios_com_fila()
    resumo = _resumos_de_marco(repos).get(perfil.id_filial, metricas_filial.ResumoFilial())
    return metricas_filial.calcular_metricas(repos, perfil.id_filial, resumo, notificacoes.obter)


class EntradaBloqueio(BaseModel):
    """Entrada de ``POST /api/filial/compras/{id_compra}/bloqueio`` (seção 17.5)."""

    nota: str | None = Field(default=None, max_length=MAXIMO_NOTA)


@router.post("/compras/{id_compra}/bloqueio", status_code=201, response_model=DetalheFilialSchema)
def bloquear(id_compra: str, entrada: EntradaBloqueio, perfil: Auditor) -> dict[str, Any]:
    """Auditor bloqueia uma compra que aguarda o associado; devolve o detalhe atualizado."""
    repos, _ = _repositorios_com_fila()
    try:
        filial_app.bloquear_compra(
            repos,
            perfil,
            id_compra,
            entrada.nota,
            _analise_de,
            _auditoria_de,
        )
    except associado_app.NaoEncontrado as erro:
        raise HTTPException(status_code=404, detail=str(erro)) from erro
    except filial_app.AcessoNegado as erro:
        raise HTTPException(status_code=403, detail=str(erro)) from erro
    except associado_app.Conflito as erro:
        raise HTTPException(status_code=409, detail=str(erro)) from erro
    return compra(id_compra, perfil)
