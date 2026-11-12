"""Testes do módulo de feedback (design, seção 13.2).

Todos os testes usam tmp_path para não tocar o data/feedback.csv da pessoa.
"""

import csv
from datetime import datetime

import pandas as pd
import pytest

from src.interface.feedback import (
    COLUNAS_FEEDBACK,
    RespostaAnalista,
    ler_ultima_resposta,
    registrar_resposta,
)


def _resposta(id_transacao: int, resposta: str, segundo: int = 0) -> RespostaAnalista:
    return RespostaAnalista(
        id_transacao=id_transacao,
        nota=97.3,
        decisao="BLOQUEAR",
        resposta_analista=resposta,
        registrado_em=datetime(2026, 11, 13, 10, 0, segundo),
    )


def test_feedback_grava_e_le_criando_pasta(tmp_path):
    """Grava uma resposta e lê de volta, criando a pasta se necessário."""
    caminho = tmp_path / "nova" / "feedback.csv"

    registrar_resposta(caminho, _resposta(7, "fraude"))
    lida = ler_ultima_resposta(caminho, 7)

    assert lida is not None
    assert int(lida.id_transacao) == 7
    assert lida.resposta_analista == "fraude"
    assert lida.decisao == "BLOQUEAR"
    assert float(lida.nota) == pytest.approx(97.3)
    assert pd.Timestamp(lida.registrado_em) == pd.Timestamp("2026-11-13 10:00:00")


def test_feedback_arquivo_ausente_retorna_none(tmp_path):
    """Arquivo ausente devolve None sem erro."""
    caminho = tmp_path / "feedback.csv"

    assert ler_ultima_resposta(caminho, 7) is None


def test_feedback_vale_a_ultima_resposta(tmp_path):
    """Vale a última resposta de cada transação."""
    caminho = tmp_path / "feedback.csv"

    registrar_resposta(caminho, _resposta(7, "fraude", 0))
    registrar_resposta(caminho, _resposta(8, "fraude", 1))
    registrar_resposta(caminho, _resposta(7, "legitima", 2))

    assert ler_ultima_resposta(caminho, 7).resposta_analista == "legitima"


def test_feedback_cabecalho_aparece_uma_vez(tmp_path):
    """O cabeçalho é escrito só no início do arquivo."""
    caminho = tmp_path / "feedback.csv"

    registrar_resposta(caminho, _resposta(7, "fraude", 0))
    registrar_resposta(caminho, _resposta(8, "fraude", 1))
    registrar_resposta(caminho, _resposta(7, "legitima", 2))

    with caminho.open(encoding="utf-8", newline="") as arquivo:
        linhas = list(csv.reader(arquivo))

    assert linhas[0] == COLUNAS_FEEDBACK
    assert len(linhas) == 4
    assert linhas[1][0] == "2026-11-13T10:00:00"


def test_feedback_sem_resposta_para_id_retorna_none(tmp_path):
    """Arquivo presente mas sem resposta para o id devolve None."""
    caminho = tmp_path / "feedback.csv"

    registrar_resposta(caminho, _resposta(8, "fraude"))
    assert ler_ultima_resposta(caminho, 7) is None


def test_feedback_resposta_invalida_nao_cria_arquivo(tmp_path):
    """Resposta inválida levanta ValueError sem criar o arquivo."""
    caminho = tmp_path / "feedback.csv"

    with pytest.raises(ValueError):
        registrar_resposta(caminho, _resposta(7, "talvez"))

    assert not caminho.exists()


def test_feedback_cabecalho_invalido_levanta_value_error(tmp_path):
    """Arquivo com cabeçalho diferente levanta ValueError."""
    caminho = tmp_path / "feedback.csv"
    caminho.write_text("id,resposta\n7,fraude\n", encoding="utf-8")

    with pytest.raises(ValueError):
        ler_ultima_resposta(caminho, 7)
