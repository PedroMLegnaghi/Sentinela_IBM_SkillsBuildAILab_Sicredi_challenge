"""Página Simulador do Sentinela.

Permite simular transações hipotéticas modificando os campos de uma transação
da fila e comparando a decisão original com a simulada.
Implementado na Issue #22.
"""

import streamlit as st

from src.interface import textos


def renderizar() -> None:
    """Renderiza a página Simulador."""
    # TODO(#22, 2026-11-13): implementar o simulador com selectbox de transação,
    # controles de edição e comparação lado a lado da decisão (Issue #22)
    st.title(textos.TITULO_SIMULADOR)
    st.caption(textos.LEGENDA_SIMULADOR_PROVISORIA)
