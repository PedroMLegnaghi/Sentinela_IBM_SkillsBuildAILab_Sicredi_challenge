"""Seção de latência da página Desempenho.

Exibe o p50, p95 e as transações por segundo medidos pelo simulador de fluxo,
mostrando que o Sentinela está pronto para tempo real.
Implementado na Issue #27.
"""

import streamlit as st


def renderizar() -> None:
    """Renderiza a seção de latência em tempo real.

    Se o JSON de latência não existir, exibe instrução para gerá-lo.
    """
    # TODO(#27, 2026-11-13): implementar a seção de latência com p50, p95 e
    # transações por segundo (Issue #27)
    from src.config import CAMINHO_LATENCIA  # noqa: PLC0415

    if not CAMINHO_LATENCIA.exists():
        st.info(
            "Dados de latência não encontrados. " "Rode no terminal: python -m src.simular_fluxo"
        )
