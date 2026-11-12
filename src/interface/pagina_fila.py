"""Página Fila de alertas do Sentinela.

Implementação na Issue #4.
"""

import streamlit as st

from src.interface import textos


def renderizar() -> None:
    """Renderiza a página Fila de alertas."""
    st.title(textos.TITULO_FILA)
    st.caption("Página em construção na Issue #4.")
