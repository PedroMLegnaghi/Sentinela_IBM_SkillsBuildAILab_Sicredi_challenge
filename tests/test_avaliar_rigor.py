"""Testes para src/avaliar_rigor.py com dados inventados."""

import numpy as np
import pandas as pd

from src.avaliar_rigor import (
    _bootstrap_ic,
    _calibracao,
    calcular_avaliacao_rigorosa,
)
from src.config import NOTA_CONFIRMAR, SEMENTE, VARIAVEIS_MODELO


def _df_minimo() -> pd.DataFrame:
    """DataFrame sintético com 3 meses e 2 fraudes claras por período.

    As fraudes têm nota alta (todos os sinais) e as legítimas têm nota baixa.
    """
    n_total = 120  # 40 por mês: 2 fraudes + 38 legítimas
    # Data hora distribuída nos meses
    datas = (
        [f"2025-01-{(i % 28) + 1:02d} 10:00:00" for i in range(40)]
        + [f"2025-02-{(i % 28) + 1:02d} 10:00:00" for i in range(40)]
        + [f"2025-03-{(i % 28) + 1:02d} 10:00:00" for i in range(40)]
    )
    # Rótulos: primeiras 2 de cada mês são fraude
    fraude = [1, 1] + [0] * 38 + [1, 1] + [0] * 38 + [1, 1] + [0] * 38

    # Variáveis: fraudes têm valores altos, legítimas têm valores baixos
    def _valores(is_fraude: bool) -> dict:
        if is_fraude:
            return {
                "valor": 400.0,
                "hora": 3.0,
                "madrugada": 1,
                "credito": 1,
                "nao_presente": 1,
                "ip_pais_desconhecido": 0,
                "vel_cartao_terminal_1h": 45.0,
                "qtd_transacoes_cartao_1min": 20.0,
                "qtd_token_carteira_3m": 80.0,
                "dist_terminal_anterior_km": 300.0,
                "risco_estabelecimento": 45.0,
            }
        return {
            "valor": 30.0,
            "hora": 14.0,
            "madrugada": 0,
            "credito": 0,
            "nao_presente": 0,
            "ip_pais_desconhecido": 0,
            "vel_cartao_terminal_1h": 2.0,
            "qtd_transacoes_cartao_1min": 1.0,
            "qtd_token_carteira_3m": 7.0,
            "dist_terminal_anterior_km": 10.0,
            "risco_estabelecimento": 18.0,
        }

    linhas = []
    for i in range(n_total):
        is_fr = fraude[i] == 1
        row = {
            "data_hora": datas[i],
            "fraude": fraude[i],
            "decisao_sistema_atual": "deny" if is_fr else "approve",
        }
        row.update(_valores(is_fr))
        linhas.append(row)

    df = pd.DataFrame(linhas)
    df["data_hora"] = pd.to_datetime(df["data_hora"])
    return df


# ---------------------------------------------------------------------------
# Testes de _bootstrap_ic
# ---------------------------------------------------------------------------


def test_bootstrap_ic_devolve_par_de_listas():
    """_bootstrap_ic retorna dict com recall_ic95 e precisao_ic95, cada uma com 2 valores."""
    y_true = np.array([1, 0, 1, 0, 1, 0, 0, 0, 1, 0])
    y_prob = np.array([80.0, 20.0, 90.0, 10.0, 70.0, 15.0, 5.0, 25.0, 85.0, 30.0])
    ic = _bootstrap_ic(y_true, y_prob, corte=NOTA_CONFIRMAR, n=200, semente=SEMENTE)

    assert "recall_ic95" in ic
    assert "precisao_ic95" in ic
    assert len(ic["recall_ic95"]) == 2
    assert len(ic["precisao_ic95"]) == 2


def test_bootstrap_ic_intervalo_ordenado():
    """O limite inferior do IC é menor ou igual ao superior."""
    y_true = np.array([1, 0, 1, 0, 1, 0, 0, 0, 1, 0])
    y_prob = np.array([80.0, 20.0, 90.0, 10.0, 70.0, 15.0, 5.0, 25.0, 85.0, 30.0])
    ic = _bootstrap_ic(y_true, y_prob, corte=NOTA_CONFIRMAR, n=200, semente=SEMENTE)

    assert ic["recall_ic95"][0] <= ic["recall_ic95"][1]
    assert ic["precisao_ic95"][0] <= ic["precisao_ic95"][1]


def test_bootstrap_ic_valores_entre_zero_e_um():
    """Os limites do IC ficam no intervalo [0, 1]."""
    y_true = np.array([1, 0, 1, 0, 1, 0, 0, 0, 1, 0])
    y_prob = np.array([80.0, 20.0, 90.0, 10.0, 70.0, 15.0, 5.0, 25.0, 85.0, 30.0])
    ic = _bootstrap_ic(y_true, y_prob, corte=NOTA_CONFIRMAR, n=200, semente=SEMENTE)

    for val in ic["recall_ic95"] + ic["precisao_ic95"]:
        assert 0.0 <= val <= 1.0


# ---------------------------------------------------------------------------
# Testes de _calibracao
# ---------------------------------------------------------------------------


def test_calibracao_brier_entre_zero_e_um():
    """Brier score fica no intervalo [0, 1]."""
    y_true = np.array([1, 0, 1, 0, 1, 0, 0, 0, 1, 0])
    y_prob = np.array([90.0, 10.0, 85.0, 5.0, 80.0, 15.0, 20.0, 25.0, 95.0, 30.0])
    cal = _calibracao(y_true, y_prob)

    assert 0.0 <= cal["brier"] <= 1.0


def test_calibracao_dez_faixas():
    """_calibracao retorna exatamente 10 faixas."""
    y_true = np.array([1, 0, 1, 0, 1, 0, 0, 0, 1, 0])
    y_prob = np.array([90.0, 10.0, 85.0, 5.0, 80.0, 15.0, 20.0, 25.0, 95.0, 30.0])
    cal = _calibracao(y_true, y_prob)

    assert len(cal["faixas"]) == 10


def test_calibracao_soma_n_igual_total():
    """A soma de n em todas as faixas é igual ao total de observações."""
    n = 100
    rng = np.random.default_rng(SEMENTE)
    y_true = rng.integers(0, 2, size=n)
    y_prob = rng.uniform(0, 100, size=n)
    cal = _calibracao(y_true, y_prob)

    assert sum(f["n"] for f in cal["faixas"]) == n


# ---------------------------------------------------------------------------
# Testes de calcular_avaliacao_rigorosa
# ---------------------------------------------------------------------------


def test_avaliacao_rigorosa_chaves_presentes():
    """calcular_avaliacao_rigorosa retorna todas as seções esperadas."""
    df = _df_minimo()
    resultado = calcular_avaliacao_rigorosa(df)

    chaves = {"janelas_temporais", "bootstrap_ic95", "baselines", "ablacao", "calibracao"}
    assert chaves.issubset(resultado.keys())


def test_janelas_temporais_tem_duas_entradas():
    """janelas_temporais contém 2 janelas."""
    df = _df_minimo()
    resultado = calcular_avaliacao_rigorosa(df)

    assert len(resultado["janelas_temporais"]) == 2


def test_ablacao_tem_entrada_por_variavel_mais_velocidade():
    """ablacao tem n_variaveis + 1 entradas (cada variável + as 3 de velocidade juntas)."""
    df = _df_minimo()
    resultado = calcular_avaliacao_rigorosa(df)

    assert len(resultado["ablacao"]) == len(VARIAVEIS_MODELO) + 1


def test_ablacao_sem_velocidade_pr_auc_menor():
    """PR-AUC sem as 3 variáveis de velocidade é menor que o valor com todas."""
    df = _df_minimo()
    resultado = calcular_avaliacao_rigorosa(df)

    pr_auc_sem_vel = next(
        e["pr_auc"]
        for e in resultado["ablacao"]
        if "velocidade" in e["variavel_removida"].lower()
        or "COLUNAS_VELOCIDADE" in e["variavel_removida"]
    )
    pr_auc_modelo = resultado["baselines"]["so_modelo"]["pr_auc"]

    assert pr_auc_sem_vel <= pr_auc_modelo


def test_baselines_contem_abordagens_esperadas():
    """baselines contém so_regras_3_sinais, so_regras_4_sinais, so_modelo, sentinela e hgb."""
    df = _df_minimo()
    resultado = calcular_avaliacao_rigorosa(df)

    chaves = {"so_regras_3_sinais", "so_regras_4_sinais", "so_modelo", "sentinela", "hgb"}
    assert chaves.issubset(resultado["baselines"].keys())
