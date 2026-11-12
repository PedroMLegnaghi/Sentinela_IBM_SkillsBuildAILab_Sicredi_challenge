"""Testes unitários da API do Sentinela (casos não cobertos pela conformidade).

Cobre: 503 sem dados (monkeypatch), conversão de NaN, concordância com dados inventados
e gravação de resposta inválida.
"""

from __future__ import annotations

from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
TEM_MODELO = (RAIZ / "modelos" / "sentinela.joblib").exists()

pytest.importorskip("fastapi")


@pytest.fixture(scope="module")
def cliente():
    """Cliente de teste com a aplicação FastAPI."""
    from fastapi.testclient import TestClient  # noqa: PLC0415

    from src.api.app import app  # noqa: PLC0415

    with TestClient(app) as c:
        yield c


# --- Saúde ------------------------------------------------------------------------------------


def test_saude_responde_200(cliente):
    resposta = cliente.get("/api/saude")

    assert resposta.status_code == 200
    assert resposta.json()["status"] == "ok"


# --- 503 sem dados (monkeypatch) --------------------------------------------------------------


def test_fila_sem_dados_retorna_503(monkeypatch, cliente):
    import src.api.servicos as sv  # noqa: PLC0415

    monkeypatch.setattr(sv._estado, "fila", None)
    monkeypatch.setattr(sv._estado, "base", None)

    resposta = cliente.get("/api/fila")

    assert resposta.status_code == 503
    assert isinstance(resposta.json()["detail"], str)


def test_transacao_sem_dados_retorna_503(monkeypatch, cliente):
    import src.api.servicos as sv  # noqa: PLC0415

    monkeypatch.setattr(sv._estado, "fila", None)
    monkeypatch.setattr(sv._estado, "base", None)

    resposta = cliente.get("/api/transacoes/0")

    assert resposta.status_code == 503


def test_respostas_post_sem_dados_retorna_503(monkeypatch, cliente):
    import src.api.servicos as sv  # noqa: PLC0415

    monkeypatch.setattr(sv._estado, "fila", None)
    monkeypatch.setattr(sv._estado, "base", None)

    resposta = cliente.post("/api/respostas", json={"id_transacao": 0, "resposta": "fraude"})

    assert resposta.status_code == 503


# --- Conversão de NaN -------------------------------------------------------------------------


@pytest.mark.skipif(not TEM_MODELO, reason="sem modelos/sentinela.joblib")
def test_analisar_sem_campos_nao_traz_nan(cliente):
    resposta = cliente.post("/api/analisar", json={"auditar": False})

    assert resposta.status_code == 200
    import math  # noqa: PLC0415

    def sem_nan(v):
        if isinstance(v, float):
            return not math.isnan(v) and not math.isinf(v)
        if isinstance(v, dict):
            return all(sem_nan(x) for x in v.values())
        if isinstance(v, list):
            return all(sem_nan(x) for x in v)
        return True

    assert sem_nan(resposta.json())


# --- Resposta inválida -------------------------------------------------------------------------


def test_resposta_invalida_retorna_422(cliente):
    resposta = cliente.post("/api/respostas", json={"id_transacao": 1, "resposta": "talvez"})

    assert resposta.status_code == 422


# --- Concordância com dados inventados --------------------------------------------------------


def test_listar_respostas_sem_arquivo_retorna_zeros(monkeypatch, tmp_path, cliente):
    """Sem feedback.csv, deve retornar total=0 e concordancia=None."""
    import src.api.servicos as sv  # noqa: PLC0415

    # Aponta o caminho do feedback para um arquivo inexistente
    caminho_vazio = tmp_path / "feedback_inexistente.csv"
    monkeypatch.setattr(sv, "CAMINHO_FEEDBACK", caminho_vazio)

    resposta = cliente.get("/api/respostas")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["total"] == 0
    assert corpo["concordancia"] is None


# --- Décision inválida na fila ----------------------------------------------------------------


def test_fila_decisao_invalida_retorna_422(cliente):
    resposta = cliente.get("/api/fila", params={"decisoes": "TALVEZ"})

    assert resposta.status_code == 422
