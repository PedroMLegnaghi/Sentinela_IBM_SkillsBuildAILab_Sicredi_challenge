"""Seção de análise exploratória dos dados da página Como funciona.

Exibe estatísticas descritivas, distribuições e qualidade dos dados
a partir do JSON gerado pelo script de análise exploratória.
Implementado na Issue #31.
"""

import streamlit as st


def renderizar() -> None:
    """Renderiza a seção de análise exploratória e qualidade dos dados.

    Se o JSON de EDA não existir, exibe instrução para gerá-lo.
    """
    # TODO(#31, 2026-11-13): implementar a seção com estatísticas descritivas,
    # distribuições e qualidade dos dados (Issue #31)
    from src.config import CAMINHO_EDA  # noqa: PLC0415

    if not CAMINHO_EDA.exists():
        st.info(
            "Análise exploratória não encontrada. " "Rode no terminal: python -m src.analisar_dados"
        )
