"""Configuração comum dos testes.

Os testes nunca gravam na base de retreino de verdade (`data/rotulos_retreino.csv`, Issue #127):
durante a sessão inteira, a API grava os rótulos num arquivo temporário.
"""

import pytest


@pytest.fixture(scope="session", autouse=True)
def rotulos_em_arquivo_temporario(tmp_path_factory):
    """Troca o caminho dos rótulos antes de qualquer teste subir a API."""
    from src import composicao  # noqa: PLC0415

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(
            composicao,
            "CAMINHO_ROTULOS",
            tmp_path_factory.mktemp("rotulos") / "rotulos_retreino.csv",
        )
        yield
