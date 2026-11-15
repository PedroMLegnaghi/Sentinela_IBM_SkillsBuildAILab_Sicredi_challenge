"""Testes para src/analisar_dados.py com dados inventados."""

import json

import numpy as np
import pandas as pd

from src.analisar_dados import calcular_eda


def _df_base() -> pd.DataFrame:
    """Cria um DataFrame mínimo com a estrutura do parquet preparado."""
    return pd.DataFrame(
        {
            "id_transacao": range(10),
            "data_hora": pd.to_datetime(
                [
                    "2025-01-05 10:00",
                    "2025-01-15 02:00",
                    "2025-02-10 14:00",
                    "2025-02-20 03:00",
                    "2025-03-05 11:00",
                    "2025-03-10 01:00",
                    "2025-03-15 15:00",
                    "2025-03-20 23:00",
                    "2025-03-25 09:00",
                    "2025-03-28 04:00",
                ]
            ),
            "id_cartao": ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10"],
            "id_cliente": ["U1"] * 10,
            "id_estabelecimento": ["E1"] * 10,
            "valor": [50.0, 200.0, 30.0, 300.0, 40.0, 500.0, 60.0, 180.0, 25.0, 450.0],
            "tipo_transacao": [
                "debito",
                "credito",
                "debito",
                "credito",
                "debito",
                "credito",
                "debito",
                "credito",
                "debito",
                "credito",
            ],
            "modalidade_transacao": [
                "cartao_presente",
                "cartao_nao_presente",
                "cartao_presente",
                "cartao_nao_presente",
                "cartao_presente",
                "cartao_nao_presente",
                "cartao_presente",
                "cartao_nao_presente",
                "cartao_presente",
                "cartao_nao_presente",
            ],
            "hora": [10.0, 2.0, 14.0, 3.0, 11.0, 1.0, 15.0, 23.0, 9.0, 4.0],
            "madrugada": [0, 1, 0, 1, 0, 1, 0, 0, 0, 1],
            "credito": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
            "nao_presente": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
            "ip_pais_desconhecido": [0, 1, 0, 1, 0, 1, 0, 0, 0, 1],
            "vel_cartao_terminal_1h": [1.0, 15.0, 2.0, 20.0, 1.0, 12.0, 3.0, 11.0, 2.0, 18.0],
            "qtd_transacoes_cartao_1min": [1.0, 6.0, 1.0, 8.0, 1.0, 7.0, 1.0, 5.0, 1.0, 9.0],
            "qtd_token_carteira_3m": [5.0, 35.0, 4.0, 40.0, 3.0, 32.0, 6.0, 31.0, 4.0, 38.0],
            "dist_terminal_anterior_km": [
                10.0,
                200.0,
                5.0,
                300.0,
                8.0,
                150.0,
                12.0,
                110.0,
                7.0,
                250.0,
            ],
            "risco_estabelecimento": [
                10.0,
                50.0,
                15.0,
                60.0,
                12.0,
                45.0,
                20.0,
                55.0,
                8.0,
                70.0,
            ],
            "mcc": [5411.0] * 10,
            "decisao_sistema_atual": ["approve"] * 5 + ["deny"] * 5,
            # 5 fraudes (linhas ímpares) e 5 legítimas (linhas pares)
            "fraude": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        }
    )


def test_total_linhas_e_fraudes_corretos():
    """calcular_eda retorna contagens exatas de linhas e fraudes."""
    df = _df_base()
    eda = calcular_eda(df)

    assert eda["total_linhas"] == 10
    assert eda["total_fraudes"] == 5


def test_percentual_fraude_correto():
    """Percentual de fraudes é calculado corretamente."""
    df = _df_base()
    eda = calcular_eda(df)

    assert abs(eda["percentual_fraude"] - 50.0) < 0.001


def test_contagem_por_mes():
    """por_mes agrupa transações corretamente por mês."""
    df = _df_base()
    eda = calcular_eda(df)

    meses = {r["mes"]: r for r in eda["por_mes"]}
    # 2 transações em janeiro, 2 em fevereiro, 6 em março
    assert meses["2025-01"]["linhas"] == 2
    assert meses["2025-02"]["linhas"] == 2
    assert meses["2025-03"]["linhas"] == 6
    # fraudes: 1 em janeiro, 1 em fevereiro, 3 em março
    assert meses["2025-01"]["fraudes"] == 1
    assert meses["2025-02"]["fraudes"] == 1
    assert meses["2025-03"]["fraudes"] == 3


def test_por_tipo_inclui_debito_e_credito():
    """por_tipo cobre os dois tipos de transação."""
    df = _df_base()
    eda = calcular_eda(df)

    tipos = {r["tipo_transacao"] for r in eda["por_tipo"]}
    assert "debito" in tipos
    assert "credito" in tipos


def test_percentis_das_variaveis_do_modelo():
    """variaveis contém p10, mediana e p90 para cada variável."""
    df = _df_base()
    eda = calcular_eda(df)

    nomes = {v["variavel"] for v in eda["variaveis"]}
    assert "valor" in nomes
    assert "vel_cartao_terminal_1h" in nomes
    assert "risco_estabelecimento" in nomes

    for entrada in eda["variaveis"]:
        for grupo in ("fraudes", "legitimas"):
            assert "mediana" in entrada[grupo]
            assert "p10" in entrada[grupo]
            assert "p90" in entrada[grupo]


def test_p10_menor_ou_igual_mediana_e_mediana_menor_ou_igual_p90():
    """p10 ≤ mediana ≤ p90 para todas as variáveis em fraudes e legítimas."""
    df = _df_base()
    eda = calcular_eda(df)

    for entrada in eda["variaveis"]:
        for grupo in ("fraudes", "legitimas"):
            stats = entrada[grupo]
            if stats["mediana"] is not None:
                assert stats["p10"] <= stats["mediana"]
                assert stats["mediana"] <= stats["p90"]


def test_sinais_cobre_todos_os_nove_sinais():
    """sinais contém entrada para cada um dos 9 sinais de alerta."""
    df = _df_base()
    eda = calcular_eda(df)

    ids_sinais = {s["sinal"] for s in eda["sinais"]}
    esperados = {
        "velocidade_terminal",
        "rajada_1min",
        "token_carteira",
        "salto_geografico",
        "madrugada",
        "valor_alto",
        "credito_nao_presente",
        "ip_desconhecido",
        "estabelecimento_risco",
    }
    assert ids_sinais == esperados


def test_por_hora_tem_24_entradas():
    """por_hora tem exatamente 24 entradas, uma por hora."""
    df = _df_base()
    eda = calcular_eda(df)

    assert len(eda["por_hora"]) == 24
    horas = [r["hora"] for r in eda["por_hora"]]
    assert horas == list(range(24))


def test_nenhum_identificador_na_saida():
    """O JSON não contém id_cartao, id_cliente nem id_estabelecimento."""
    df = _df_base()
    eda = calcular_eda(df)

    texto = json.dumps(eda)
    assert "id_cartao" not in texto
    assert "id_cliente" not in texto
    assert "id_estabelecimento" not in texto
    # Verifica que nenhum valor de cartão ou cliente aparece
    for id_val in ["C1", "C2", "U1", "E1"]:
        assert id_val not in texto


def test_auditoria_vazamento_contem_colunas_da_especificacao():
    """auditoria_vazamento lista as colunas proibidas da seção 5."""
    df = _df_base()
    eda = calcular_eda(df)

    nomes = {c["coluna"] for c in eda["auditoria_vazamento"]}
    # Colunas nomeadas individualmente
    for coluna in ["fraud", "fraud_score", "visa_fraud_score", "mc_fraud_score", "decision"]:
        assert coluna in nomes
    # Padrões com prefixo
    prefixos = {"dispute_*", "fdz_*", "oob_*"}
    assert prefixos.issubset(nomes)


def test_vazios_com_nan_nao_quebra_percentis():
    """calcular_eda trata colunas com NaN sem levantar exceção."""
    df = _df_base()
    df.loc[[1, 3], "vel_cartao_terminal_1h"] = np.nan
    eda = calcular_eda(df)

    var_vel = next(v for v in eda["variaveis"] if v["variavel"] == "vel_cartao_terminal_1h")
    # Legítimas têm valores; fraudes têm 2 NaN em 5 itens → 40% de vazios
    assert var_vel["pct_vazios"] > 0
    # Mediana de legítimas deve ser calculada normalmente
    assert var_vel["legitimas"]["mediana"] is not None


def test_df_sem_fraudes_retorna_zero_fraudes():
    """calcular_eda funciona com um DataFrame sem nenhuma fraude."""
    df = _df_base()
    df["fraude"] = 0
    eda = calcular_eda(df)

    assert eda["total_fraudes"] == 0
    assert eda["percentual_fraude"] == 0.0
