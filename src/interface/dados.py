"""Carga e cache dos dados e do agente para a interface do Sentinela."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

import pandas as pd
import streamlit as st

from src import agente as modulo_agente
from src.agente import AgenteSentinela
from src.config import (
    CAMINHO_MODELO,
    CAMINHO_PREPARADO,
    FIM_TESTE,
    INICIO_TESTE,
    SEMENTE,
    TAMANHO_AMOSTRA_LEGITIMAS,
)
from src.interface import textos
from src.interface.tema import ORDEM_DECISOES as _ORDEM


def verificar_arquivos(
    caminho_dados: Path = CAMINHO_PREPARADO,
    caminho_modelo: Path = CAMINHO_MODELO,
) -> list[str]:
    """Lista mensagens de erro para arquivos ausentes.

    Args:
        caminho_dados: Caminho do parquet de dados preparados.
        caminho_modelo: Caminho do modelo salvo.

    Returns:
        Lista de textos de erro, na ordem dados e modelo; vazia se ambos existirem.
    """
    erros: list[str] = []
    if not Path(caminho_dados).exists():
        erros.append(textos.ERRO_SEM_DADOS)
    if not Path(caminho_modelo).exists():
        erros.append(textos.ERRO_SEM_MODELO)
    return erros


@st.cache_data(show_spinner=False)
def carregar_base() -> pd.DataFrame:
    """Carrega o parquet de dados preparados.

    Returns:
        DataFrame com todas as transações preparadas.
    """
    return pd.read_parquet(CAMINHO_PREPARADO)


@st.cache_resource(show_spinner=False)
def carregar_agente() -> AgenteSentinela:
    """Carrega o agente Sentinela com a base de dados.

    Returns:
        Instância de AgenteSentinela pronta para uso.
    """
    return AgenteSentinela(base=carregar_base())


def montar_fila(
    base: pd.DataFrame,
    analisar_lote: Callable[[pd.DataFrame], pd.DataFrame],
    tamanho_amostra: int = TAMANHO_AMOSTRA_LEGITIMAS,
    semente: int = SEMENTE,
) -> pd.DataFrame:
    """Monta a fila de demonstração com fraudes e amostra de legítimas de março.

    Filtra março (INICIO_TESTE <= data < FIM_TESTE), junta todas as fraudes e
    uma amostra de legítimas, aplica analisar_lote, ordena por nota decrescente
    e remove colunas sensíveis.

    Args:
        base: DataFrame completo de transações preparadas.
        analisar_lote: Função que pontua e classifica um DataFrame de transações.
        tamanho_amostra: Número máximo de legítimas a sortear.
        semente: Semente para reprodutibilidade da amostra.

    Returns:
        DataFrame da fila, ordenado por nota decrescente e id_transacao crescente,
        sem as colunas fraude e decisao_sistema_atual.
    """
    inicio = pd.Timestamp(INICIO_TESTE)
    fim = pd.Timestamp(FIM_TESTE)
    marco = base[(base["data_hora"] >= inicio) & (base["data_hora"] < fim)].copy()

    fraudes = marco[marco["fraude"] == 1]
    legitimas = marco[marco["fraude"] == 0]

    n = min(tamanho_amostra, len(legitimas))
    amostra = legitimas.sample(n=n, random_state=semente)

    fila_bruta = pd.concat([fraudes, amostra], ignore_index=True)
    fila_pontuada = analisar_lote(fila_bruta)

    fila_pontuada = fila_pontuada.sort_values(
        ["nota", "id_transacao"], ascending=[False, True]
    ).reset_index(drop=True)

    fila_pontuada = fila_pontuada.drop(
        columns=[c for c in ("fraude", "decisao_sistema_atual") if c in fila_pontuada.columns]
    )

    return fila_pontuada


@st.cache_data(show_spinner=textos.CARREGANDO_FILA)
def carregar_fila() -> pd.DataFrame:
    """Carrega e monta a fila de alertas com cache de sessão.

    Returns:
        DataFrame da fila de demonstração.
    """
    return montar_fila(carregar_base(), carregar_agente().analisar_lote)


def contar_por_decisao(fila: pd.DataFrame) -> dict[str, int]:
    """Conta transações por decisão, retornando zero para decisões ausentes.

    Args:
        fila: DataFrame com coluna "decisao".

    Returns:
        Dicionário com uma chave por decisão em ORDEM_DECISOES, valor zero quando ausente.
    """
    contagens = fila["decisao"].value_counts().to_dict()
    return {decisao: contagens.get(decisao, 0) for decisao in _ORDEM}


@st.cache_data(show_spinner=False)
def carregar_json(caminho: Path) -> dict | None:
    """Carrega um arquivo JSON, devolvendo None se não existir.

    Args:
        caminho: Caminho do arquivo JSON.

    Returns:
        Dicionário com o conteúdo do JSON, ou None se o arquivo não existir.
    """
    caminho_p = Path(caminho)
    if not caminho_p.exists():
        return None
    with caminho_p.open(encoding="utf-8") as arquivo:
        return json.load(arquivo)


@st.cache_data(ttl=30, show_spinner=False)
def granite_esta_disponivel() -> bool:
    """Verifica se o Ollama está respondendo (TTL de 30 segundos).

    Returns:
        True se o Granite estiver disponível, False caso contrário.
    """
    return modulo_agente.granite_disponivel()
