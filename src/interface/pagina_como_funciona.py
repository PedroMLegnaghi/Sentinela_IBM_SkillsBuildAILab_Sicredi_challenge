"""Página Como funciona do Sentinela.

Explica os passos do agente, os sinais de alerta, as regras de decisão,
os dados da base e as limitações do sistema.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.config import (
    HORA_FIM_MADRUGADA,
    LIMIAR_DISTANCIA_KM,
    LIMIAR_RAJADA_1MIN,
    LIMIAR_RISCO_ESTABELECIMENTO,
    LIMIAR_TOKEN_CARTEIRA,
    LIMIAR_VALOR_ALTO,
    LIMIAR_VELOCIDADE_TERMINAL,
    MIN_SINAIS_CONFIRMAR,
    NOTA_BLOQUEAR,
    NOTA_CONFIRMAR,
    TAMANHO_AMOSTRA_LEGITIMAS,
)
from src.interface import textos
from src.interface.dados import carregar_base
from src.interface.formatacao import formatar_inteiro, formatar_percentual


def _renderizar_passos() -> None:
    """Renderiza a lista numerada dos passos do agente."""
    st.header(textos.TITULO_PASSOS)
    for passo in textos.PASSOS:
        st.markdown(f"- {passo}")


def _renderizar_sinais() -> None:
    """Renderiza a tabela dos 9 sinais de alerta com limiares de config."""
    st.header(textos.TITULO_SINAIS_COMO)
    constantes = {
        "LIMIAR_VELOCIDADE_TERMINAL": LIMIAR_VELOCIDADE_TERMINAL,
        "LIMIAR_RAJADA_1MIN": LIMIAR_RAJADA_1MIN,
        "LIMIAR_TOKEN_CARTEIRA": LIMIAR_TOKEN_CARTEIRA,
        "LIMIAR_DISTANCIA_KM": LIMIAR_DISTANCIA_KM,
        "HORA_FIM_MADRUGADA": HORA_FIM_MADRUGADA,
        "LIMIAR_VALOR_ALTO": LIMIAR_VALOR_ALTO,
        "LIMIAR_RISCO_ESTABELECIMENTO": LIMIAR_RISCO_ESTABELECIMENTO,
    }
    linhas = [
        (sinal, descricao.format(**constantes)) for sinal, descricao in textos.SINAIS_EXPLICADOS
    ]
    tabela = pd.DataFrame(linhas, columns=["Sinal", "Dispara quando"])
    st.table(tabela)


def _renderizar_decisao() -> None:
    """Renderiza as três regras de decisão com os limiares de config."""
    st.header(textos.TITULO_DECISAO)
    constantes = {
        "NOTA_BLOQUEAR": NOTA_BLOQUEAR,
        "NOTA_CONFIRMAR": NOTA_CONFIRMAR,
        "MIN_SINAIS_CONFIRMAR": MIN_SINAIS_CONFIRMAR,
    }
    for regra in textos.REGRAS_DECISAO:
        st.markdown(f"- {regra.format(**constantes)}")


def _renderizar_dados() -> None:
    """Renderiza a seção sobre os dados, com números calculados da base."""
    st.header(textos.TITULO_DADOS)
    base = carregar_base()
    linhas = len(base)
    fraudes = int(base["fraude"].sum())
    percentual = formatar_percentual(fraudes / linhas)
    st.markdown(
        textos.SOBRE_DADOS.format(
            linhas=formatar_inteiro(linhas),
            fraudes=formatar_inteiro(fraudes),
            percentual=percentual,
            amostra=formatar_inteiro(TAMANHO_AMOSTRA_LEGITIMAS),
        )
    )


def _renderizar_limitacoes() -> None:
    """Renderiza a lista de limitações do sistema."""
    st.header(textos.TITULO_LIMITACOES)
    for limitacao in textos.LIMITACOES:
        st.markdown(f"- {limitacao}")


def renderizar() -> None:
    """Renderiza a página Como funciona."""
    st.title(textos.TITULO_COMO)
    st.markdown(textos.LEAD_COMO)

    _renderizar_passos()
    _renderizar_sinais()
    _renderizar_decisao()
    _renderizar_dados()
    _renderizar_limitacoes()
