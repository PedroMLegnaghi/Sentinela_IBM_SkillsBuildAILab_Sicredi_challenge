"""Fila de demonstração do Sentinela: todas as fraudes de março e uma amostra de legítimas.

Usada pela API (ESPECIFICACAO, seção 12; ADR-007).
"""

from __future__ import annotations

from collections.abc import Callable

import pandas as pd

from src.config import FIM_TESTE, INICIO_TESTE, SEMENTE, TAMANHO_AMOSTRA_LEGITIMAS

ORDEM_DECISOES = ("BLOQUEAR", "PEDIR_CONFIRMACAO", "APROVAR")


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


def contar_por_decisao(fila: pd.DataFrame) -> dict[str, int]:
    """Conta transações por decisão, retornando zero para decisões ausentes.

    Args:
        fila: DataFrame com coluna "decisao".

    Returns:
        Dicionário com uma chave por decisão em ORDEM_DECISOES, valor zero quando ausente.
    """
    contagens = fila["decisao"].value_counts().to_dict()
    return {decisao: contagens.get(decisao, 0) for decisao in ORDEM_DECISOES}
