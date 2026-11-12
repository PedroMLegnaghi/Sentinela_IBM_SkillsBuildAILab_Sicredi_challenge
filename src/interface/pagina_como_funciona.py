"""Página Como funciona do Sentinela.

Implementação na Issue #5.
"""

import streamlit as st

from src.interface import textos


def renderizar() -> None:
    """Renderiza a página Como funciona."""
    st.title(textos.TITULO_COMO)
    st.caption("Página em construção na Issue #5.")
