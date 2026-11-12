"""Testes de fumaça da interface com AppTest (design, Issue #3, passo 5).

Pulados quando data/transacoes_preparadas.parquet ou modelos/sentinela.joblib não existirem.
"""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

RAIZ = Path(__file__).resolve().parents[1]

_pular_sem_dados_e_modelo = pytest.mark.skipif(
    not (
        (RAIZ / "data" / "transacoes_preparadas.parquet").exists()
        and (RAIZ / "modelos" / "sentinela.joblib").exists()
    ),
    reason="sem data/transacoes_preparadas.parquet ou modelos/sentinela.joblib",
)


@_pular_sem_dados_e_modelo
def test_app_abre_sem_excecao():
    """app.py carrega sem exceção."""
    app = AppTest.from_file(str(RAIZ / "app.py"), default_timeout=120)
    app.run()

    assert not app.exception, app.exception


@_pular_sem_dados_e_modelo
def test_pagina_fila_abre_sem_excecao():
    """pagina_fila.renderizar() carrega sem exceção."""

    def executar() -> None:
        import streamlit as st  # noqa: PLC0415

        from src.interface import pagina_fila  # noqa: PLC0415

        st.session_state["usar_granite"] = True
        pagina_fila.renderizar()

    app = AppTest.from_function(executar, default_timeout=120)
    app.run()

    assert not app.exception, app.exception


@_pular_sem_dados_e_modelo
def test_pagina_desempenho_abre_sem_excecao():
    """pagina_desempenho.renderizar() carrega sem exceção."""

    def executar() -> None:
        from src.interface import pagina_desempenho  # noqa: PLC0415

        pagina_desempenho.renderizar()

    app = AppTest.from_function(executar, default_timeout=120)
    app.run()

    assert not app.exception, app.exception


@_pular_sem_dados_e_modelo
def test_pagina_como_funciona_abre_sem_excecao():
    """pagina_como_funciona.renderizar() carrega sem exceção."""

    def executar() -> None:
        from src.interface import pagina_como_funciona  # noqa: PLC0415

        pagina_como_funciona.renderizar()

    app = AppTest.from_function(executar, default_timeout=120)
    app.run()

    assert not app.exception, app.exception


@_pular_sem_dados_e_modelo
def test_pagina_simulador_abre_sem_excecao():
    """pagina_simulador.renderizar() carrega sem exceção."""

    def executar() -> None:
        from src.interface import pagina_simulador  # noqa: PLC0415

        pagina_simulador.renderizar()

    app = AppTest.from_function(executar, default_timeout=120)
    app.run()

    assert not app.exception, app.exception


@_pular_sem_dados_e_modelo
def test_pagina_respostas_abre_sem_excecao():
    """pagina_respostas.renderizar() carrega sem exceção."""

    def executar() -> None:
        from src.interface import pagina_respostas  # noqa: PLC0415

        pagina_respostas.renderizar()

    app = AppTest.from_function(executar, default_timeout=120)
    app.run()

    assert not app.exception, app.exception
