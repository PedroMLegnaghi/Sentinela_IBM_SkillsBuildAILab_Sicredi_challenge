"""Testes para src/analisar_custos.py com dados inventados."""

import pandas as pd

from src.analisar_custos import calcular_custos
from src.config import CUSTO_PEDIDO_CONFIRMACAO


def _df_custos(n: int = 20) -> pd.DataFrame:
    """Cria um DataFrame mínimo com as colunas esperadas por calcular_custos.

    10 transações são fraudes (valor 200), 10 são legítimas (valor 50).
    5 fraudes são bloqueadas; 5 estão em confirmação; as 10 legítimas são aprovadas.
    O sistema atual bloqueou apenas as 5 fraudes com 'deny'.
    """
    linhas = []
    for _i in range(10):
        linhas.append(
            {
                "nota": 90.0,
                "decisao": "BLOQUEAR",
                "decisao_sistema_atual": "deny",
                "valor": 200.0,
                "fraude": 1,
            }
        )
    for _i in range(5):
        linhas.append(
            {
                "nota": 40.0,
                "decisao": "PEDIR_CONFIRMACAO",
                "decisao_sistema_atual": "approve",
                "valor": 150.0,
                "fraude": 1,
            }
        )
    for _i in range(5):
        linhas.append(
            {
                "nota": 10.0,
                "decisao": "APROVAR",
                "decisao_sistema_atual": "approve",
                "valor": 50.0,
                "fraude": 0,
            }
        )
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------------------
# Testes de calcular_custos
# ---------------------------------------------------------------------------


def test_sentinela_fraudes_bloqueadas_correto():
    """Sentinela contabiliza corretamente as fraudes bloqueadas."""
    df = _df_custos()
    resultado = calcular_custos(df, CUSTO_PEDIDO_CONFIRMACAO)

    assert resultado["sentinela"]["fraudes_bloqueadas"] == 10


def test_sentinela_valor_fraudes_bloqueadas_correto():
    """Valor das fraudes bloqueadas pelo Sentinela é a soma dos valores das 10 fraudes."""
    df = _df_custos()
    resultado = calcular_custos(df, CUSTO_PEDIDO_CONFIRMACAO)

    assert abs(resultado["sentinela"]["valor_fraudes_bloqueadas"] - 2000.0) < 0.01


def test_sentinela_confirmacoes_correto():
    """Número de confirmações é exatamente 5 (as fraudes em PEDIR_CONFIRMACAO)."""
    df = _df_custos()
    resultado = calcular_custos(df, CUSTO_PEDIDO_CONFIRMACAO)

    assert resultado["sentinela"]["confirmacoes"] == 5


def test_custo_confirmacoes_e_produto_unitario():
    """Custo total de confirmações é n_confirmacoes * custo_unitario."""
    df = _df_custos()
    custo_unit = 2.5
    resultado = calcular_custos(df, custo_unit)

    esperado = resultado["sentinela"]["confirmacoes"] * custo_unit
    assert abs(resultado["sentinela"]["custo_confirmacoes"] - esperado) < 0.001


def test_nao_compara_com_a_coluna_decision():
    """A coluna decision da base não é documentada como sistema real: não entra no resultado."""
    resultado = calcular_custos(_df_custos(), CUSTO_PEDIDO_CONFIRMACAO)

    assert "sistema_atual" not in resultado
    assert "comparacao" not in resultado


def test_valor_liquido_protegido_desconta_as_confirmacoes():
    """Valor líquido = valor das fraudes bloqueadas menos o custo das confirmações."""
    resultado = calcular_custos(_df_custos(), 1.0)

    s = resultado["sentinela"]
    esperado = round(s["valor_fraudes_bloqueadas"] - s["custo_confirmacoes"], 2)
    assert abs(resultado["valor_liquido_protegido"] - esperado) < 0.01


def test_curva_custo_tem_21_pontos():
    """curva_custo tem exatamente 21 pontos (0 a 100, de 5 em 5)."""
    df = _df_custos()
    resultado = calcular_custos(df, CUSTO_PEDIDO_CONFIRMACAO)

    assert len(resultado["curva_custo"]) == 21


def test_curva_custo_primeiro_e_ultimo_corte():
    """O primeiro ponto da curva tem corte 0 e o último tem corte 100."""
    df = _df_custos()
    resultado = calcular_custos(df, CUSTO_PEDIDO_CONFIRMACAO)

    assert resultado["curva_custo"][0]["corte"] == 0
    assert resultado["curva_custo"][-1]["corte"] == 100


def test_curva_custo_confirmacoes_monotonicamente_decrescente():
    """Mais confirmações em corte baixo; menos em corte alto."""
    df = _df_custos()
    resultado = calcular_custos(df, CUSTO_PEDIDO_CONFIRMACAO)

    confs = [p["confirmacoes"] for p in resultado["curva_custo"]]
    # Em corte 0 todos viram alerta; em corte 100 ninguém vira alerta
    assert confs[0] >= confs[-1]


def test_valor_vazio_conta_como_zero():
    """Transação com valor NaN entra em valores_vazios e conta como 0 no cálculo."""
    df = _df_custos()
    df.loc[0, "valor"] = float("nan")
    resultado = calcular_custos(df, CUSTO_PEDIDO_CONFIRMACAO)

    assert resultado["sentinela"]["valores_vazios"] == 1
    # O valor da fraude 0 (NaN → 0) não deve levantar exceção e o total cai
    assert resultado["sentinela"]["valor_fraudes_bloqueadas"] < 2000.0
