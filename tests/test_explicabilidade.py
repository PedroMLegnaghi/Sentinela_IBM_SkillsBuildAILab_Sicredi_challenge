"""Testes da explicabilidade (Issue #41) com um pipeline pequeno treinado em dados inventados."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.config import VARIAVEIS_MODELO
from src.explicabilidade import NOMES_LEGIVEIS, contribuicoes, importancia_global, nome_legivel

RAIZ = Path(__file__).resolve().parents[1]
TEM_MODELO = (RAIZ / "modelos" / "sentinela.joblib").exists()


@pytest.fixture(scope="module")
def pipeline() -> Pipeline:
    """Pipeline igual ao do projeto, treinado em 40 linhas inventadas; `valor` tem vazios."""
    geradora = np.random.default_rng(42)
    entradas = pd.DataFrame(
        {
            "valor": geradora.uniform(5, 500, 40),
            "hora": geradora.integers(0, 24, 40).astype(float),
            "x": geradora.normal(0, 1, 40),
        }
    )
    entradas.loc[::5, "valor"] = np.nan
    alvo = ((entradas["valor"].fillna(0) > 250) | (entradas["x"] > 1.2)).astype(int)
    modelo = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median", add_indicator=True)),
            ("scaler", StandardScaler()),
            ("modelo", LogisticRegression(class_weight="balanced", max_iter=2000, random_state=42)),
        ]
    )
    return modelo.fit(entradas, alvo)


TRANSACAO = {"valor": 420.0, "hora": 3.0, "x": -0.4}


def test_soma_das_contribuicoes_mais_o_intercepto_e_o_log_odds(pipeline):
    itens = contribuicoes(pipeline, TRANSACAO)

    soma = sum(item["contribuicao"] for item in itens)
    intercepto = float(pipeline.named_steps["modelo"].intercept_[0])
    log_odds = float(pipeline.decision_function(pd.DataFrame([TRANSACAO]))[0])

    assert soma + intercepto == pytest.approx(log_odds)


def test_contribuicoes_vem_em_ordem_de_valor_absoluto_decrescente(pipeline):
    valores = [abs(item["contribuicao"]) for item in contribuicoes(pipeline, TRANSACAO)]

    assert valores == sorted(valores, reverse=True)


def test_ha_uma_contribuicao_por_coluna_da_regressao_com_nome_para_todas(pipeline):
    itens = contribuicoes(pipeline, TRANSACAO)

    assert {item["variavel"] for item in itens} == {"valor", "hora", "x", "faltante_valor"}
    assert all(item["nome"] for item in itens)
    assert all(set(item) == {"variavel", "nome", "contribuicao"} for item in itens)


def test_transacao_sem_valor_e_imputada_e_o_indicador_de_vazio_pesa(pipeline):
    itens = {i["variavel"]: i["contribuicao"] for i in contribuicoes(pipeline, {"hora": 3.0})}

    assert all(np.isfinite(valor) for valor in itens.values())
    assert itens["faltante_valor"] != 0.0


def test_indicador_de_vazio_ganha_o_sufixo_ausente():
    assert nome_legivel("faltante_valor") == "Valor da compra ausente"
    assert nome_legivel("valor") == "Valor da compra"
    assert nome_legivel("faltante_x") == "x ausente"


def test_nomes_legiveis_cobrem_todas_as_variaveis_do_modelo():
    assert set(NOMES_LEGIVEIS) == set(VARIAVEIS_MODELO)


def test_importancia_global_ordena_pelo_coeficiente_absoluto(pipeline):
    itens = importancia_global(pipeline)

    coeficientes = [abs(item["coeficiente"]) for item in itens]
    assert coeficientes == sorted(coeficientes, reverse=True)
    assert [item["variavel"] for item in itens][0] in {"valor", "x"}
    assert all(item["nome"] for item in itens)


@pytest.mark.skipif(not TEM_MODELO, reason="sem modelos/sentinela.joblib")
def test_transacao_de_alto_risco_tem_a_maior_contribuicao_positiva():
    import joblib  # noqa: PLC0415

    modelo_real = joblib.load(RAIZ / "modelos" / "sentinela.joblib")
    alto_risco = {
        "valor": 980.0,
        "hora": 3,
        "madrugada": 1,
        "credito": 1,
        "nao_presente": 1,
        "ip_pais_desconhecido": 1,
        "vel_cartao_terminal_1h": 40,
        "qtd_transacoes_cartao_1min": 15,
        "qtd_token_carteira_3m": 90,
        "dist_terminal_anterior_km": 400.0,
        "risco_estabelecimento": 70,
    }

    itens = contribuicoes(modelo_real, alto_risco)

    assert len(itens) == len(modelo_real.named_steps["modelo"].coef_[0])
    assert itens[0]["contribuicao"] > 0
