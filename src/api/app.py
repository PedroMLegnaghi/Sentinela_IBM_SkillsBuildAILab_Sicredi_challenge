"""Aplicação FastAPI do Sentinela (ESPECIFICACAO, seção 12).

Executar: uvicorn src.api.app:app --port 8000
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from src.api import auditorias as auditoria_mem
from src.api import servicos
from src.api.esquemas import (
    EntradaAnalise,
    EntradaResposta,
)
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
        analise (Analise) e id_auditoria (str ou null).
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

    return {"analise": analise, "id_auditoria": id_auditoria}


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
    transacao_dict = dados["transacao"]
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
    try:
        return servicos.gravar_resposta(entrada.id_transacao, entrada.resposta)
    except KeyError as erro:
        raise HTTPException(
            status_code=404,
            detail=f"Transação {entrada.id_transacao} não está na fila.",
        ) from erro
    except (ValueError, OSError) as erro:
        raise HTTPException(status_code=422, detail=str(erro)) from erro


# --- GET /api/respostas -----------------------------------------------------------------------


@app.get("/api/respostas")
def listar_respostas() -> dict[str, Any]:
    """Lista todas as respostas do analista (última por transação).

    Returns:
        total, fraudes, legitimas, concordancia e itens.
    """
    return servicos.listar_respostas()


# --- GET /api/metricas ------------------------------------------------------------------------


@app.get("/api/metricas")
def metricas() -> dict[str, Any]:
    """Retorna métricas do modelo e avaliação do agente.

    Returns:
        metricas, avaliacao e extras (avaliacao_rigorosa, custos, eda, ia_contra_modelo).
    """
    try:
        return servicos.obter_metricas()
    except RuntimeError as erro:
        raise HTTPException(status_code=503, detail=str(erro)) from erro
