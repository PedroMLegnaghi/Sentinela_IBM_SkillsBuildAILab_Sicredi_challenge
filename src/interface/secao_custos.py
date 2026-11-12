"""Seção de custo da fraude da página Desempenho.

Exibe o prejuízo evitado, o custo com o Sentinela, o custo com o sistema
atual e a curva de custo por nota de corte.
Implementado na Issue #20.
"""

import streamlit as st


def renderizar() -> None:
    """Renderiza a seção de custo da fraude em março.

    Se o JSON de custos não existir, exibe instrução para gerá-lo.
    """
    # TODO(#20, 2026-11-13): implementar a seção de custo com métricas financeiras
    # e gráfico da curva de custo por nota de corte (Issue #20)
    from src.config import CAMINHO_CUSTOS  # noqa: PLC0415

    if not CAMINHO_CUSTOS.exists():
        st.info(
            "Análise de custos não encontrada. " "Rode no terminal: python -m src.analisar_custos"
        )
