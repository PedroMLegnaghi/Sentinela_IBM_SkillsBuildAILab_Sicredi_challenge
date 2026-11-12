"""Testes de formatação pt-BR (design, seção 12).

Cada caso de teste corresponde a um exemplo da tabela da seção 12.
"""

import pandas as pd

from src.interface.formatacao import (
    escapar_markdown,
    formatar_data_hora,
    formatar_decimal,
    formatar_inteiro,
    formatar_modalidade,
    formatar_moeda,
    formatar_nota,
    formatar_percentual,
    formatar_tipo,
    rotulo_resposta,
)


def test_formatar_moeda_valor_positivo():
    assert formatar_moeda(1234.5) == "R$ 1.234,50"


def test_formatar_moeda_none_retorna_indisponivel():
    assert formatar_moeda(None) == "valor indisponível"


def test_formatar_moeda_nan_retorna_indisponivel():
    assert formatar_moeda(float("nan")) == "valor indisponível"


def test_formatar_nota_decimal():
    assert formatar_nota(97.34) == "97,3"


def test_formatar_nota_inteiro():
    assert formatar_nota(100) == "100,0"


def test_formatar_inteiro_com_milhar():
    assert formatar_inteiro(2054) == "2.054"


def test_formatar_decimal_tres_casas():
    assert formatar_decimal(0.99812, 3) == "0,998"


def test_formatar_percentual_quatro_digitos():
    assert formatar_percentual(0.4815) == "48,1%"


def test_formatar_percentual_dois_digitos():
    assert formatar_percentual(0.0117) == "1,2%"


def test_formatar_data_hora_timestamp():
    assert formatar_data_hora(pd.Timestamp("2025-03-15 03:12:40")) == "15/03/2025 03:12"


def test_formatar_data_hora_nat_retorna_indisponivel():
    assert formatar_data_hora(pd.NaT) == "data indisponível"


def test_formatar_data_hora_none_retorna_indisponivel():
    assert formatar_data_hora(None) == "data indisponível"


def test_formatar_tipo_credito():
    assert formatar_tipo("credito") == "Crédito"


def test_formatar_tipo_desconhecido_retorna_original():
    assert formatar_tipo("xyz") == "xyz"


def test_formatar_modalidade_nao_presente():
    assert formatar_modalidade("cartao_nao_presente") == "Não presente"


def test_rotulo_resposta_legitima():
    assert rotulo_resposta("legitima") == "Transação legítima"


def test_escapar_markdown_com_dois_cifrao():
    assert escapar_markdown("R$ 10 e R$ 20") == "R\\$ 10 e R\\$ 20"
