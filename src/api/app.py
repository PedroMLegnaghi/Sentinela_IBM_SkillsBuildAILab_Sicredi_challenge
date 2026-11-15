"""Aplicação FastAPI do Sentinela (ESPECIFICACAO, seção 12).

Executar: uvicorn src.api.app:app --port 8000
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware

from src.api import auditorias as auditoria_mem
from src.api import respostas as resp_mod
from src.api import rotas_associado, rotas_filial, rotas_matriz, servicos, sessao
from src.api.esquemas import (
    EntradaAnalise,
    EntradaResposta,
    EntradaRespostaAssociado,
    NotificacaoSchema,
)
from src.aplicacao import associado as associado_app
from src.associado import notificacoes as notificacao_mem
from src.associado.mensagem import tipo_por_decisao
from src.config import API_ORIGENS_PERMITIDAS

DECISOES_VALIDAS = {"APROVAR", "PEDIR_CONFIRMACAO", "BLOQUEAR"}
MENSAGEM_503 = (
    "Dados não carregados. Rode: python -m src.preparar_dados " "e python -m src.treinar_modelo"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Carrega parquet, agente e fila na subida; libera recursos no encerramento."""
    servicos.inicializar()
    yield


app = FastAPI(
    title="Sentinela API",
    description="API antifraude do Sentinela (ESPECIFICACAO, seção 12).",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=API_ORIGENS_PERMITIDAS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas da refatoração (ESPECIFICACAO, seção 17), em arquivos próprios
app.include_router(sessao.router)
app.include_router(rotas_associado.router)
app.include_router(rotas_filial.router)
app.include_router(rotas_matriz.router)


def _auditoria_ativa() -> str:
    """Retorna 'watsonx' se as credenciais estiverem definidas; senão 'local'."""
    apikey = os.environ.get("WATSONX_APIKEY", "")
    project_id = os.environ.get("WATSONX_PROJECT_ID", "")
    if apikey and project_id:
        return "watsonx"
    return "local"


# --- GET /api/saude ---------------------------------------------------------------------------


@app.get("/api/saude")
def saude() -> dict[str, Any]:
    """Verifica o estado da API.

    Returns:
        status, modelo_carregado, dados_carregados e auditoria (watsonx ou local).
    """
    return {
        "status": "ok",
        "modelo_carregado": servicos.modelo_carregado(),
        "dados_carregados": servicos.dados_carregados(),
        "auditoria": _auditoria_ativa(),
    }


# --- GET /api/fila ----------------------------------------------------------------------------


@app.get("/api/fila")
def fila(
    decisoes: str = Query(
        default="BLOQUEAR,PEDIR_CONFIRMACAO",
        description="Decisões a incluir, separadas por vírgula.",
    ),
) -> dict[str, Any]:
    """Lista os itens da fila de demonstração.

    Args:
        decisoes: Decisões para filtrar, separadas por vírgula.

    Returns:
        total_fila, contagens e itens filtrados por nota decrescente.
    """
    lista_decisoes = [d.strip() for d in decisoes.split(",")]
    invalidas = [d for d in lista_decisoes if d not in DECISOES_VALIDAS]
    if invalidas:
        raise HTTPException(
            status_code=422,
            detail=f"Decisão inválida: {invalidas}. Use APROVAR, PEDIR_CONFIRMACAO ou BLOQUEAR.",
        )
    if not servicos.dados_carregados():
        raise HTTPException(status_code=503, detail=MENSAGEM_503)
    try:
        return servicos.obter_fila(lista_decisoes)
    except RuntimeError as erro:
        raise HTTPException(status_code=503, detail=str(erro)) from erro


# --- GET /api/transacoes/{id_transacao} -------------------------------------------------------


@app.get("/api/transacoes/{id_transacao}")
def transacao(id_transacao: int) -> dict[str, Any]:
    """Retorna a transação, análise, histórico e última resposta do analista.

    Args:
        id_transacao: Identificador da transação.

    Returns:
        transacao, analise, historico e resposta_analista.
    """
    if not servicos.dados_carregados():
        raise HTTPException(status_code=503, detail=MENSAGEM_503)
    try:
        return servicos.obter_transacao(id_transacao)
    except KeyError as erro:
        raise HTTPException(status_code=404, detail=str(erro)) from erro
    except RuntimeError as erro:
        raise HTTPException(status_code=503, detail=str(erro)) from erro


# --- POST /api/analisar -----------------------------------------------------------------------


@app.post("/api/analisar")
def analisar(entrada: EntradaAnalise) -> dict[str, Any]:
    """Analisa uma transação e opcionalmente dispara auditoria em segundo plano.

    Args:
        entrada: Campos da transação (todos opcionais) e flag ``auditar``.

    Returns:
        analise (Analise), id_auditoria (str ou null) e id_notificacao (str ou null).
    """
    if not servicos.modelo_carregado():
        raise HTTPException(
            status_code=503,
            detail="Modelo não carregado. Rode: python -m src.treinar_modelo",
        )

    transacao_dict = {k: v for k, v in entrada.model_dump().items() if k != "auditar"}
    analise = servicos.analisar_transacao(transacao_dict)

    id_auditoria = None
    if entrada.auditar:
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
        auditoria_mem.disparar_auditoria_em_segundo_plano(id_auditoria, transacao_dict, analise)

    return {
        "analise": analise,
        "id_auditoria": id_auditoria,
        "id_notificacao": _avisar_associado(transacao_dict, analise),
    }


def _avisar_associado(transacao: dict[str, Any], analise: dict[str, Any]) -> str | None:
    """Cria a notificação de uma análise avulsa quando a decisão pede; devolve o id ou None."""
    if tipo_por_decisao(analise["decisao"]) is None:
        return None
    return notificacao_mem.criar_notificacao(transacao, analise)["id_notificacao"]


# --- POST /api/transacoes/{id_transacao}/auditoria --------------------------------------------


@app.post("/api/transacoes/{id_transacao}/auditoria", status_code=202)
def auditoria_transacao(id_transacao: int) -> dict[str, Any]:
    """Inicia auditoria de uma transação da fila (idempotente).

    Args:
        id_transacao: Identificador da transação.

    Returns:
        202 com id_auditoria e status.
    """
    if not servicos.dados_carregados():
        raise HTTPException(status_code=503, detail=MENSAGEM_503)

    # Verifica se a transação está na fila
    try:
        dados = servicos.obter_transacao(id_transacao)
    except KeyError as erro:
        raise HTTPException(status_code=404, detail=str(erro)) from erro
    except RuntimeError as erro:
        raise HTTPException(status_code=503, detail=str(erro)) from erro

    # Idempotência: retorna auditoria existente se já foi criada para este id_transacao
    # Usamos um id baseado na transação para garantir idempotência
    id_auditoria_fixa = f"trans_{id_transacao}"

    auditoria_existente = auditoria_mem.obter_auditoria(id_auditoria_fixa)
    if auditoria_existente is not None:
        return {"id_auditoria": id_auditoria_fixa, "status": auditoria_existente["status"]}

    auditoria_mem.registrar_auditoria(
        id_auditoria_fixa,
        {
            "id_auditoria": id_auditoria_fixa,
            "status": "pendente",
            "relatorio": None,
            "latencia_ms": None,
            "mensagem": None,
        },
    )
    analise = dados["analise"]
    transacao_dict = servicos.transacao_para_auditoria(id_transacao)
    auditoria_mem.disparar_auditoria_em_segundo_plano(id_auditoria_fixa, transacao_dict, analise)

    return {"id_auditoria": id_auditoria_fixa, "status": "pendente"}


# --- GET /api/auditorias/{id_auditoria} -------------------------------------------------------


@app.get("/api/auditorias/{id_auditoria}")
def obter_auditoria(id_auditoria: str) -> dict[str, Any]:
    """Retorna o estado de uma auditoria.

    Args:
        id_auditoria: Identificador da auditoria.

    Returns:
        Auditoria com id, status, relatorio, latencia_ms e mensagem.
    """
    aud = auditoria_mem.obter_auditoria(id_auditoria)
    if aud is None:
        raise HTTPException(
            status_code=404,
            detail=f"Auditoria '{id_auditoria}' não encontrada.",
        )
    return aud


# --- POST /api/respostas ----------------------------------------------------------------------


@app.post("/api/respostas", status_code=201)
def gravar_resposta(entrada: EntradaResposta) -> dict[str, Any]:
    """Grava a resposta do analista para uma transação.

    Args:
        entrada: id_transacao e resposta ("fraude" ou "legitima").

    Returns:
        201 com Resposta gravada.
    """
    if not servicos.dados_carregados():
        raise HTTPException(status_code=503, detail=MENSAGEM_503)
    dados_fila = servicos.dados_fila_para_resposta(entrada.id_transacao)
    if dados_fila is None:
        raise HTTPException(
            status_code=404,
            detail=f"Transação {entrada.id_transacao} não está na fila.",
        )
    nota, decisao = dados_fila
    try:
        return resp_mod.gravar_resposta(entrada.id_transacao, entrada.resposta, nota, decisao)
    except (ValueError, OSError) as erro:
        raise HTTPException(status_code=422, detail=str(erro)) from erro


# --- GET /api/respostas -----------------------------------------------------------------------


@app.get("/api/respostas")
def listar_respostas() -> dict[str, Any]:
    """Lista todas as respostas do analista (última por transação).

    Returns:
        total, fraudes, legitimas, concordancia e itens.
    """
    return resp_mod.listar_respostas()


# --- GET /api/metricas ------------------------------------------------------------------------


@app.get("/api/metricas")
def metricas() -> dict[str, Any]:
    """Retorna métricas do modelo e avaliação do agente.

    Returns:
        metricas, avaliacao e extras (avaliacao_rigorosa, custos, eda, ia_contra_modelo).
    """
    try:
        return resp_mod.obter_metricas()
    except RuntimeError as erro:
        raise HTTPException(status_code=503, detail=str(erro)) from erro


# --- Canal do associado (ESPECIFICACAO, seção 15) ---------------------------------------------


@app.post(
    "/api/transacoes/{id_transacao}/notificacao",
    status_code=201,
    response_model=NotificacaoSchema,
)
def notificar_associado(id_transacao: int, response: Response) -> dict[str, Any]:
    """Avisa o associado sobre uma transação da fila (idempotente).

    Args:
        id_transacao: Identificador da transação.
        response: Resposta HTTP, para devolver 200 quando a notificação já existia.

    Returns:
        201 com a Notificacao criada, ou 200 com a que já existia.
    """
    if not servicos.dados_carregados():
        raise HTTPException(status_code=503, detail=MENSAGEM_503)
    existente = notificacao_mem.obter_por_transacao(id_transacao)
    if existente is not None:
        response.status_code = 200
        return existente
    try:
        dados = servicos.obter_transacao(id_transacao)
    except KeyError as erro:
        raise HTTPException(status_code=404, detail=str(erro)) from erro
    except RuntimeError as erro:
        raise HTTPException(status_code=503, detail=str(erro)) from erro
    try:
        return notificacao_mem.criar_notificacao(dados["transacao"], dados["analise"], id_transacao)
    except ValueError as erro:
        raise HTTPException(status_code=422, detail=str(erro)) from erro


@app.get("/api/notificacoes")
def listar_notificacoes() -> dict[str, Any]:
    """Lista as notificações ao associado, da mais recente para a mais antiga.

    Returns:
        itens com as Notificacoes.
    """
    return {"itens": notificacao_mem.listar()}


@app.get("/api/notificacoes/{id_notificacao}", response_model=NotificacaoSchema)
def obter_notificacao(id_notificacao: str) -> dict[str, Any]:
    """Devolve uma notificação ao associado.

    Args:
        id_notificacao: Identificador da notificação.

    Returns:
        Notificacao; desconhecida → 404.
    """
    notificacao = notificacao_mem.obter(id_notificacao)
    if notificacao is None:
        raise HTTPException(
            status_code=404, detail=_mensagem_notificacao_desconhecida(id_notificacao)
        )
    return notificacao


@app.post("/api/notificacoes/{id_notificacao}/resposta", response_model=NotificacaoSchema)
def responder_notificacao(id_notificacao: str, entrada: EntradaRespostaAssociado) -> dict[str, Any]:
    """Registra a resposta do associado ("sim" ou "nao") a uma notificação.

    Args:
        id_notificacao: Identificador da notificação.
        entrada: Corpo com ``resposta``.

    Returns:
        Notificacao atualizada; já respondida → 409; desconhecida → 404; inválida → 422.
    """
    try:
        notificacao = notificacao_mem.responder(id_notificacao, entrada.resposta)
    except KeyError as erro:
        raise HTTPException(
            status_code=404, detail=_mensagem_notificacao_desconhecida(id_notificacao)
        ) from erro
    except notificacao_mem.NotificacaoJaRespondida as erro:
        raise HTTPException(status_code=409, detail=str(erro)) from erro
    except ValueError as erro:
        raise HTTPException(status_code=422, detail=str(erro)) from erro
    # A resposta ao aviso também muda a compra do associado (seção 17.1), sem mudar o corpo.
    associado_app.aplicar_resposta_do_aviso(
        sessao.obter_repositorios(), id_notificacao, entrada.resposta
    )
    return notificacao


def _mensagem_notificacao_desconhecida(id_notificacao: str) -> str:
    """Texto do 404 das rotas de notificação."""
    return f"Notificação '{id_notificacao}' não encontrada. Confira o id em GET /api/notificacoes."
