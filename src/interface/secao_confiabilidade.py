"""Seção de confiabilidade da página Desempenho.

Exibe o recall e a precisão com intervalo de confiança por bootstrap,
a tabela de comparação de modelos e o gráfico de ablação.
Implementado na Issue #28.
"""

import streamlit as st


def renderizar() -> None:
    """Renderiza a seção de confiabilidade do resultado.

    Se o JSON de avaliação rigorosa não existir, exibe instrução para gerá-lo.
    """
    # TODO(#28, 2026-11-13): implementar a seção de confiabilidade com bootstrap,
    # comparação de modelos, ablação e calibração (Issue #28)
    from src.config import CAMINHO_AVALIACAO_RIGOROSA  # noqa: PLC0415

    if not CAMINHO_AVALIACAO_RIGOROSA.exists():
        st.info(
            "Avaliação rigorosa não encontrada. " "Rode no terminal: python -m src.avaliar_rigor"
        )
