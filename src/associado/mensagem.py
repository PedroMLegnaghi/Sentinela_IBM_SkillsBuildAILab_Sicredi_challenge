"""Redação e validação da mensagem ao associado (ESPECIFICACAO, seção 15; ADR-015).

A mensagem avisa o associado de uma compra suspeita sem pedir dado sigiloso. Hoje ela sai de
dois modelos fixos; a Issue #65 pluga o watsonx.ai em ``redigir_com_ia``. Toda mensagem, de
qualquer fonte, passa por ``validar_mensagem`` antes de ser usada.
"""

from __future__ import annotations

import logging
import math
import re
from datetime import datetime
from typing import Any

from src.config import (
    MENSAGEM_MAX_CARACTERES,
    MENSAGEM_MAX_DIGITOS_SEGUIDOS,
    MENSAGEM_PREFIXO,
    MENSAGEM_TERMOS_PROIBIDOS,
)

logger = logging.getLogger(__name__)

# Decisão do modelo → tipo da notificação; APROVAR não avisa o associado
TIPO_POR_DECISAO = {"PEDIR_CONFIRMACAO": "CONFIRMACAO", "BLOQUEAR": "AVISO_BLOQUEIO"}
_NOME_DO_CARTAO = {"credito": "crédito", "debito": "débito"}
# O valor em reais é o único lugar onde dígitos seguidos são esperados
_PADRAO_VALOR = re.compile(r"R\$ ?[\d.,]+")
_PADRAO_DIGITOS_SEGUIDOS = re.compile(rf"\d{{{MENSAGEM_MAX_DIGITOS_SEGUIDOS + 1},}}")


def tipo_por_decisao(decisao: str) -> str | None:
    """Tipo de notificação que a decisão gera; None quando ela não avisa o associado.

    Args:
        decisao: APROVAR, PEDIR_CONFIRMACAO ou BLOQUEAR.

    Returns:
        "CONFIRMACAO", "AVISO_BLOQUEIO" ou None.
    """
    return TIPO_POR_DECISAO.get(decisao)


def formatar_moeda(valor: float) -> str:
    """Formata um valor em reais no padrão pt-BR.

    Args:
        valor: Valor em reais.

    Returns:
        Texto como "R$ 341,79" ou "R$ 1.234,50".
    """
    texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def _trecho_do_valor(valor: Any) -> str:
    """Devolve " de R$ 341,79", ou vazio quando o valor falta ou não é numérico."""
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        return ""
    if math.isnan(numero):
        return ""
    return f" de {formatar_moeda(numero)}"


def _trecho_de_quando(data_hora: Any) -> str:
    """Devolve " em 03/03 às 00:17", ou vazio quando a data falta ou é inválida."""
    try:
        momento = datetime.fromisoformat(str(data_hora))
    except ValueError:
        return ""
    return f" em {momento.strftime('%d/%m')} às {momento.strftime('%H:%M')}"


def _trecho_do_cartao(tipo_transacao: Any) -> str:
    """Devolve " de crédito" ou " de débito", ou vazio quando o tipo falta."""
    nome = _NOME_DO_CARTAO.get(str(tipo_transacao))
    return f" de {nome}" if nome else ""


def redigir_pelo_modelo(transacao: dict[str, Any], tipo: str) -> str:
    """Redige a mensagem pelo modelo fixo do tipo (fonte "modelo").

    Args:
        transacao: Campos públicos da transação (``valor``, ``data_hora``, ``tipo_transacao``).
        tipo: "CONFIRMACAO" ou "AVISO_BLOQUEIO".

    Returns:
        Texto da mensagem; sem data, omite "em … às …".
    """
    valor = _trecho_do_valor(transacao.get("valor"))
    quando = _trecho_de_quando(transacao.get("data_hora"))
    if tipo == "AVISO_BLOQUEIO":
        return (
            f"{MENSAGEM_PREFIXO} bloqueamos uma compra{valor}{quando} por segurança. "
            "Seu cartão está protegido. Foi você? Responda no app."
        )
    cartao = _trecho_do_cartao(transacao.get("tipo_transacao"))
    return (
        f"{MENSAGEM_PREFIXO} compra{valor}{quando} no seu cartão{cartao}. "
        "Foi você? Responda no app."
    )


def redigir_com_ia(transacao: dict[str, Any], analise: dict[str, Any], tipo: str) -> str | None:
    """Ponto único em que a Issue #65 pluga a redação pelo watsonx.ai.

    Até lá, não há redator por IA: devolve None e o modelo fixo assume. Quando existir, a
    resposta ainda passa por ``validar_mensagem``; recusada, o modelo fixo assume do mesmo jeito.

    Args:
        transacao: Campos públicos da transação, sem identificadores.
        analise: Analise do modelo, com ``decisao`` e ``sinais``.
        tipo: "CONFIRMACAO" ou "AVISO_BLOQUEIO".

    Returns:
        Texto redigido pela IA, ou None quando ela não está disponível.
    """
    return None


def redigir_mensagem(transacao: dict[str, Any], analise: dict[str, Any]) -> tuple[str, str]:
    """Redige a mensagem ao associado e informa de onde ela veio.

    Args:
        transacao: Campos públicos da transação (``valor``, ``data_hora``, ``tipo_transacao``).
        analise: Analise do modelo, com ``decisao``.

    Returns:
        Tupla ``(texto, fonte)``, com fonte "watsonx" ou "modelo".

    Raises:
        ValueError: Se a decisão não gera mensagem (APROVAR ou valor desconhecido).
    """
    decisao = str(analise.get("decisao"))
    tipo = tipo_por_decisao(decisao)
    if tipo is None:
        raise ValueError(
            f"A decisão {decisao} não avisa o associado; só PEDIR_CONFIRMACAO e BLOQUEAR geram "
            "notificação."
        )
    texto_ia = redigir_com_ia(transacao, analise, tipo)
    if texto_ia is not None:
        if validar_mensagem(texto_ia):
            return texto_ia, "watsonx"
        logger.warning("Mensagem da IA recusada pelas regras contra golpe; usando o modelo fixo.")
    texto = redigir_pelo_modelo(transacao, tipo)
    if not validar_mensagem(texto):
        # Não deve acontecer: se acontecer, o defeito está no modelo fixo e precisa aparecer.
        logger.error("O modelo fixo quebrou uma regra contra golpe (%d caracteres).", len(texto))
    return texto, "modelo"


def validar_mensagem(texto: str) -> bool:
    """Aplica as regras contra golpe da seção 15 a uma mensagem.

    Começa com "Sicredi:"; até 160 caracteres; sem link; sem pedir senha, código, token ou
    dados do cartão; sem sequência de 4 dígitos ou mais fora do valor.

    Args:
        texto: Mensagem candidata, de qualquer fonte.

    Returns:
        True se a mensagem respeita todas as regras.
    """
    if not texto.startswith(MENSAGEM_PREFIXO) or len(texto) > MENSAGEM_MAX_CARACTERES:
        return False
    minusculas = texto.lower()
    if any(termo in minusculas for termo in MENSAGEM_TERMOS_PROIBIDOS):
        return False
    sem_valor = _PADRAO_VALOR.sub("", texto)
    return _PADRAO_DIGITOS_SEGUIDOS.search(sem_valor) is None
