"""Página Desempenho do Sentinela.

Exibe os indicadores comparando o Sentinela com o sistema atual,
gráfico de barras, tabela de comparação e detalhes do modelo.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.config import CAMINHO_AVALIACAO, CAMINHO_METRICAS
from src.interface import textos
from src.interface.dados import carregar_json
from src.interface.formatacao import formatar_decimal, formatar_inteiro, formatar_percentual
from src.interface.tema import ICONE_ERRO


def _carregar_metricas() -> tuple[dict, dict] | None:
    """Carrega os dois arquivos JSON de métricas.

    Returns:
        Tupla (metricas, avaliacao) ou None se algum arquivo estiver ausente.
    """
    metricas = carregar_json(CAMINHO_METRICAS)
    avaliacao = carregar_json(CAMINHO_AVALIACAO)
    if metricas is None or avaliacao is None:
        st.error(textos.ERRO_SEM_METRICAS, icon=ICONE_ERRO)
        return None
    return metricas, avaliacao


def _renderizar_indicadores(avaliacao: dict) -> None:
    """Renderiza os cinco indicadores da avaliação em colunas.

    Args:
        avaliacao: Dicionário com os dados de avaliacao_agente.json.
    """
    fraudes_total = avaliacao["fraudes_total"]
    transacoes = avaliacao["transacoes"]
    sentinela = avaliacao["sentinela"]
    sistema = avaliacao["sistema_atual"]

    s_bloqueadas = sentinela["bloqueadas"]
    s_fraudes = sentinela["fraudes_bloqueadas"]
    a_fraudes = sistema["fraudes_bloqueadas"]
    confirmacoes = sentinela["confirmacoes"]
    legitimas_bloqueadas = s_bloqueadas - s_fraudes
    percentual_conf = formatar_percentual(confirmacoes / transacoes)

    cols = st.columns(5)
    cols[0].metric("Fraudes em março", formatar_inteiro(fraudes_total))
    cols[1].metric(
        "Bloqueadas pelo Sentinela",
        f"{formatar_inteiro(s_fraudes)} de {formatar_inteiro(fraudes_total)}",
        delta=textos.DELTA_SENTINELA.format(diferenca=s_fraudes - a_fraudes),
    )
    cols[2].metric(
        "Bloqueadas pelo sistema atual",
        f"{formatar_inteiro(a_fraudes)} de {formatar_inteiro(fraudes_total)}",
    )
    cols[3].metric(
        "Compras legítimas bloqueadas",
        formatar_inteiro(legitimas_bloqueadas),
        help=textos.AJUDA_LEGITIMAS_BLOQUEADAS,
    )
    cols[4].metric(
        "Pedidos de confirmação",
        formatar_inteiro(confirmacoes),
        help=textos.AJUDA_CONFIRMACOES.format(percentual=percentual_conf),
    )


def _renderizar_grafico(avaliacao: dict) -> None:
    """Renderiza o gráfico de barras horizontal de fraudes bloqueadas.

    Args:
        avaliacao: Dicionário com os dados de avaliacao_agente.json.
    """
    st.header(textos.TITULO_GRAFICO)
    s_fraudes = avaliacao["sentinela"]["fraudes_bloqueadas"]
    a_fraudes = avaliacao["sistema_atual"]["fraudes_bloqueadas"]

    dados_grafico = pd.DataFrame(
        {"Fraudes bloqueadas": [a_fraudes, s_fraudes]},
        index=["Sistema atual", "Sentinela"],
    )
    st.bar_chart(dados_grafico, horizontal=True)


def _renderizar_tabela_comparacao(avaliacao: dict) -> None:
    """Renderiza a tabela comparativa de indicadores.

    Args:
        avaliacao: Dicionário com os dados de avaliacao_agente.json.
    """
    st.header(textos.TITULO_COMPARACAO)
    fraudes_total = avaliacao["fraudes_total"]
    sentinela = avaliacao["sentinela"]
    sistema = avaliacao["sistema_atual"]

    s_fraudes = sentinela["fraudes_bloqueadas"]
    a_fraudes = sistema["fraudes_bloqueadas"]
    s_legitimas = sentinela["bloqueadas"] - sentinela["fraudes_bloqueadas"]

    tabela = pd.DataFrame(
        {
            "Indicador": [
                "Fraudes bloqueadas",
                "Fraudes não bloqueadas",
                "Percentual das fraudes bloqueadas",
                "Compras legítimas bloqueadas",
            ],
            "Sistema atual": [
                f"{a_fraudes} de {fraudes_total}",
                str(fraudes_total - a_fraudes),
                formatar_percentual(a_fraudes / fraudes_total),
                "—",
            ],
            "Sentinela": [
                f"{s_fraudes} de {fraudes_total}",
                str(fraudes_total - s_fraudes),
                formatar_percentual(s_fraudes / fraudes_total),
                str(s_legitimas),
            ],
        }
    )
    st.table(tabela)


def _renderizar_detalhes_modelo(metricas: dict) -> None:
    """Renderiza o expander com PR-AUC, ROC-AUC e tabela dos limiares.

    Args:
        metricas: Dicionário com os dados de metricas.json.
    """
    with st.expander(textos.TITULO_DETALHES_MODELO):
        cols = st.columns(2)
        cols[0].metric("PR-AUC", formatar_decimal(metricas["pr_auc"], 3))
        cols[1].metric("ROC-AUC", formatar_decimal(metricas["roc_auc"], 3))

        limiares = metricas.get("limiares", [])
        if limiares:
            tabela_limiares = pd.DataFrame(
                {
                    "Nota de corte": [lim["limiar"] for lim in limiares],
                    "Alertas": [lim["alertas"] for lim in limiares],
                    "Fraudes detectadas": [lim["fraudes_detectadas"] for lim in limiares],
                    "Precisão": [formatar_percentual(lim["precisao"]) for lim in limiares],
                    "Recall": [formatar_percentual(lim["recall"]) for lim in limiares],
                }
            )
            st.table(tabela_limiares)


def renderizar() -> None:
    """Renderiza a página Desempenho."""
    resultado = _carregar_metricas()
    if resultado is None:
        return
    metricas, avaliacao = resultado

    st.title(textos.TITULO_DESEMPENHO)
    st.caption(
        textos.LEGENDA_DESEMPENHO.format(transacoes=formatar_inteiro(avaliacao["transacoes"]))
    )

    _renderizar_indicadores(avaliacao)
    _renderizar_grafico(avaliacao)
    _renderizar_tabela_comparacao(avaliacao)
    _renderizar_detalhes_modelo(metricas)
    st.info(textos.AVISO_SINTETICO)
