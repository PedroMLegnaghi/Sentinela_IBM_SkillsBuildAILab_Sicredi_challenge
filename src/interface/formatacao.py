"""Funções de formatação pt-BR para a interface do Sentinela.

Todas as funções são puras e testadas em tests/test_formatacao.py.
"""

from __future__ import annotations

import math

import pandas as pd

from src.interface import textos


def formatar_moeda(valor: float | None) -> str:
    """Formata um valor monetário em reais no padrão pt-BR.

    Args:
        valor: Valor numérico em reais, ou None/NaN para indisponível.

    Returns:
        String no formato "R$ 1.234,50" ou "valor indisponível".
    """
    if valor is None or (isinstance(valor, float) and math.isnan(valor)):
        return "valor indisponível"
    partes = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {partes}"


def formatar_nota(nota: float) -> str:
    """Formata a nota de risco com uma casa decimal no padrão pt-BR.

    Args:
        nota: Nota de 0 a 100.

    Returns:
        String no formato "97,3".
    """
    return f"{nota:.1f}".replace(".", ",")


def formatar_inteiro(n: int) -> str:
    """Formata um inteiro com separador de milhar pt-BR.

    Args:
        n: Número inteiro.

    Returns:
        String no formato "2.054".
    """
    return f"{n:,}".replace(",", ".")


def formatar_decimal(valor: float, casas: int) -> str:
    """Formata um decimal com número fixo de casas no padrão pt-BR.

    Args:
        valor: Número decimal.
        casas: Quantidade de casas decimais.

    Returns:
        String no formato "0,998".
    """
    return f"{valor:.{casas}f}".replace(".", ",")


def formatar_percentual(fracao: float) -> str:
    """Formata uma fração como percentual com uma casa decimal pt-BR.

    Args:
        fracao: Valor entre 0 e 1.

    Returns:
        String no formato "48,1%".
    """
    return f"{fracao * 100:.1f}%".replace(".", ",")


def formatar_data_hora(momento: pd.Timestamp | None) -> str:
    """Formata uma data e hora no padrão pt-BR.

    Args:
        momento: Timestamp pandas, ou None/NaT para indisponível.

    Returns:
        String no formato "15/03/2025 03:12" ou "data indisponível".
    """
    if momento is None or pd.isna(momento):
        return "data indisponível"
    return pd.Timestamp(momento).strftime("%d/%m/%Y %H:%M")


def formatar_tipo(tipo: str) -> str:
    """Formata o tipo de transação para exibição.

    Args:
        tipo: "credito", "debito" ou qualquer outro valor.

    Returns:
        Rótulo legível ou o valor original se não reconhecido.
    """
    return textos.ROTULOS_TIPO.get(tipo, tipo)


def formatar_modalidade(modalidade: str) -> str:
    """Formata a modalidade da transação para exibição.

    Args:
        modalidade: "cartao_presente", "cartao_nao_presente" ou outro valor.

    Returns:
        Rótulo legível ou o valor original se não reconhecido.
    """
    return textos.ROTULOS_MODALIDADE.get(modalidade, modalidade)


def rotulo_resposta(resposta: str) -> str:
    """Converte a resposta do analista em rótulo legível.

    Args:
        resposta: "fraude" ou "legitima".

    Returns:
        Rótulo legível conforme textos.ROTULOS_RESPOSTA.
    """
    return textos.ROTULOS_RESPOSTA.get(resposta, resposta)


def escapar_markdown(texto: str) -> str:
    r"""Escapa o cifrão para evitar interpretação como fórmula matemática.

    Args:
        texto: Texto que pode conter "R$".

    Returns:
        Texto com "$" escapados como "\$".
    """
    return texto.replace("$", "\\$")
