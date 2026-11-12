"""Página de respostas do analista do Sentinela.

Exibe um resumo das respostas registradas pelo analista: concordância com
o agente, tabela de respostas e exportação em CSV.
Implementado na Issue #25.
"""

import streamlit as st

from src.interface import textos


def renderizar() -> None:
    """Renderiza a página de respostas do analista."""
    # TODO(#25, 2026-11-13): implementar a página de respostas com concordância,
    # tabela e exportação CSV (Issue #25)
    st.title(textos.TITULO_RESPOSTAS)
    st.caption(textos.LEGENDA_RESPOSTAS_PROVISORIA)
