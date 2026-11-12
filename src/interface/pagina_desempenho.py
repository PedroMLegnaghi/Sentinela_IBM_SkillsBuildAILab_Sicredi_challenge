"""Página Desempenho do Sentinela.

Implementação na Issue #5.
"""

import streamlit as st

from src.interface import textos


def renderizar() -> None:
    """Renderiza a página Desempenho."""
    st.title(textos.TITULO_DESEMPENHO)
    st.caption("Página em construção na Issue #5.")
