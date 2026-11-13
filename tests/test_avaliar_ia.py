"""Testes da comparação IA × modelo (Issue #46), com dados e auditoria inventados."""

from __future__ import annotations

import pandas as pd

from src.avaliar_ia import montar_amostra, resumir


def _registro(fraude, decisao, risco, parecer, ms_modelo=2.0, ms_ia=3000.0):
    return {
        "fraude": fraude,
        "decisao": decisao,
        "risco_ia": risco,
        "parecer": parecer,
        "fonte": "watsonx",
        "ms_modelo": ms_modelo,
        "ms_ia": ms_ia,
    }


def test_amostra_tem_todas_as_fraudes_de_marco_e_so_marco():
    datas = pd.to_datetime(["2025-02-10", "2025-03-05", "2025-03-06", "2025-03-07", "2025-04-02"])
    base = pd.DataFrame({"data_hora": datas, "fraude": [1, 1, 0, 0, 1], "id_transacao": range(5)})

    amostra = montar_amostra(base, tamanho_legitimas=1)

    assert len(amostra) == 2
    assert amostra["fraude"].sum() == 1
    assert amostra["data_hora"].dt.month.eq(3).all()


def test_resumo_calcula_concordancia_e_acerto_de_cada_lado():
    registros = [
        _registro(1, "BLOQUEAR", "ALTO", "CONFIRMA"),
        _registro(1, "BLOQUEAR", "BAIXO", "DIVERGE"),
        _registro(0, "APROVAR", "BAIXO", "CONFIRMA"),
        _registro(0, "APROVAR", "SUSPEITO", "DIVERGE"),
    ]

    resumo = resumir(registros)

    assert resumo["concordancia_por_decisao"] == {
        "APROVAR": 50.0,
        "PEDIR_CONFIRMACAO": None,
        "BLOQUEAR": 50.0,
    }
    assert resumo["modelo"] == {
        "alertas": 2,
        "fraudes_pegas": 2,
        "recall": 100.0,
        "precisao": 100.0,
    }
    assert resumo["ia_sozinha"] == {
        "alertas": 2,
        "fraudes_pegas": 1,
        "recall": 50.0,
        "precisao": 50.0,
    }


def test_resumo_nao_tem_identificadores_e_mede_as_latencias():
    resumo = resumir([_registro(0, "APROVAR", "BAIXO", "CONFIRMA", ms_modelo=2.0, ms_ia=4000.0)])

    assert resumo["latencia_modelo"]["p50_ms"] == 2.0
    assert resumo["latencia_ia"]["p95_ms"] == 4000.0
    assert "id_transacao" not in str(resumo)
