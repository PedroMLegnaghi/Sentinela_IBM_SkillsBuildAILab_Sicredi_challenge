"""Redação e validação da mensagem ao associado (ESPECIFICACAO, seção 15; ADR-015).

A mensagem avisa o associado de uma compra suspeita sem pedir dado sigiloso. Com credenciais,
o IBM Granite no watsonx.ai redige o texto (``redigir_com_ia``, Issue #65); sem elas, ou se a
IA falhar, valem os dois modelos fixos. Toda mensagem, de qualquer fonte, passa por
``validar_mensagem`` antes de ser usada.
"""

from __future__ import annotations

import logging
import math
import re
from datetime import datetime
from typing import Any

from src.auditoria import watsonx
from src.config import (
    MENSAGEM_MAX_CARACTERES,
    MENSAGEM_MAX_DIGITOS_SEGUIDOS,
    MENSAGEM_PREFIXO,
    MENSAGEM_TERMOS_PROIBIDOS,
)

logger = logging.getLogger(__name__)

MENSAGEM_IA_TIMEOUT_S = 15
MENSAGEM_IA_MAX_TOKENS = 120
INSTRUCOES_MENSAGEM = (
    "Você escreve avisos curtos da Sicredi para o celular do associado sobre uma compra com "
    "cartão que o sistema antifraude considerou suspeita. Escreva em português do Brasil, em "
    "tom calmo e acolhedor, numa única linha. Regras obrigatórias: comece exatamente com "
    '"Sicredi:" e termine exatamente com "Foi você? Responda no app."; use no máximo 130 '
    "caracteres no total, numa ou duas frases curtas; cite o valor, a data e a hora exatamente "
    "como recebidos e nunca invente data, hora ou valor que não estejam no pedido; se a "
    "situação disser que a compra foi bloqueada, diga claramente que ela foi bloqueada por "
    "segurança; não inclua links, telefones nem outros números; não mencione senha, código, "
    "token nem dados do cartão. Responda somente com o texto da mensagem, sem aspas."
)
_SITUACAO_POR_TIPO = {
    "CONFIRMACAO": "a compra está em análise e precisamos que o associado confirme se a fez",
    "AVISO_BLOQUEIO": "a compra foi bloqueada por segurança e o cartão está protegido",
}
_PADRAO_DATA = re.compile(r"\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b")
_PADRAO_HORA = re.compile(r"\b\d{1,2}(?::|h)\d{2}\b")

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


def _pedido_para_ia(transacao: dict[str, Any], tipo: str) -> str:
    """Monta o pedido ao modelo só com valor, data, hora e tipo do cartão (nunca ids)."""
    partes = [f"Situação: {_SITUACAO_POR_TIPO[tipo]}."]
    valor = _trecho_do_valor(transacao.get("valor"))
    if valor:
        partes.append(f"Valor:{valor.removeprefix(' de')}.")
    quando = _trecho_de_quando(transacao.get("data_hora"))
    if quando:
        data, hora = quando.removeprefix(" em ").split(" às ")
        partes.append(f"Data: {data}. Hora: {hora}.")
    cartao = _trecho_do_cartao(transacao.get("tipo_transacao"))
    if cartao:
        partes.append(f"Cartão:{cartao.removeprefix(' de')}.")
    return " ".join(partes)


def redigir_com_ia(transacao: dict[str, Any], analise: dict[str, Any], tipo: str) -> str | None:
    """Pede ao IBM Granite, no watsonx.ai, o texto do aviso ao associado.

    O modelo recebe só valor, data, hora, tipo do cartão e a situação; nunca identificadores
    nem a análise. A resposta ainda passa por ``validar_mensagem`` em quem chama; recusada,
    o modelo fixo assume.

    Args:
        transacao: Campos públicos da transação, sem identificadores.
        analise: Analise do modelo (não é enviada ao watsonx.ai).
        tipo: "CONFIRMACAO" ou "AVISO_BLOQUEIO".

    Returns:
        Texto redigido pela IA, ou None sem credenciais ou se a chamada falhar.
    """
    if not watsonx.credenciais_disponiveis():
        return None
    try:
        texto = watsonx.redigir_texto(
            INSTRUCOES_MENSAGEM,
            _pedido_para_ia(transacao, tipo),
            MENSAGEM_IA_MAX_TOKENS,
            MENSAGEM_IA_TIMEOUT_S,
        )
    except watsonx.FalhaWatsonx as erro:
        logger.warning("Mensagem pela IA indisponível; usando o modelo fixo: %s", erro)
        return None
    # Uma linha só, sem aspas em volta: o SMS não tem quebra de linha
    return " ".join(texto.split()).strip("\"'“”")


def fiel_aos_dados(texto: str, transacao: dict[str, Any], tipo: str) -> bool:
    """Confere que o texto da IA não inventa valor, data ou hora e diz o que aconteceu.

    Args:
        texto: Mensagem candidata redigida pela IA.
        transacao: Campos públicos da transação.
        tipo: "CONFIRMACAO" ou "AVISO_BLOQUEIO".

    Returns:
        True se todo valor, data e hora citados são os da compra e, num aviso de bloqueio,
        o texto diz que a compra foi bloqueada.
    """
    valor = _trecho_do_valor(transacao.get("valor")).removeprefix(" de ")
    quando = _trecho_de_quando(transacao.get("data_hora")).removeprefix(" em ")
    data, hora = quando.split(" às ") if quando else ("", "")
    valores = {v.rstrip(".,") for v in _PADRAO_VALOR.findall(texto)}
    if valores - {valor}:
        return False
    if set(_PADRAO_DATA.findall(texto)) - {data}:
        return False
    if set(_PADRAO_HORA.findall(texto)) - {hora}:
        return False
    return tipo != "AVISO_BLOQUEIO" or "bloque" in texto.lower()


def redigir_com_ia_validada(transacao: dict[str, Any], analise: dict[str, Any]) -> str | None:
    """Texto da IA já aprovado pelas regras contra golpe, ou None.

    Args:
        transacao: Campos públicos da transação, sem identificadores.
        analise: Analise do modelo, com ``decisao``.

    Returns:
        A mensagem redigida pela IA, se ela existir e passar em ``validar_mensagem``.
    """
    tipo = tipo_por_decisao(str(analise.get("decisao")))
    if tipo is None:
        return None
    texto = redigir_com_ia(transacao, analise, tipo)
    if texto is None:
        return None
    if not validar_mensagem(texto):
        logger.warning("Mensagem da IA recusada pelas regras contra golpe; usando o modelo fixo.")
        return None
    if not fiel_aos_dados(texto, transacao, tipo):
        logger.warning("Mensagem da IA não confere com os dados da compra; usando o modelo fixo.")
        return None
    return texto


def redigir_mensagem(
    transacao: dict[str, Any], analise: dict[str, Any], usar_ia: bool = True
) -> tuple[str, str]:
    """Redige a mensagem ao associado e informa de onde ela veio.

    Args:
        transacao: Campos públicos da transação (``valor``, ``data_hora``, ``tipo_transacao``).
        analise: Analise do modelo, com ``decisao``.
        usar_ia: False pula o watsonx.ai e devolve o modelo fixo na hora (as notificações
            usam assim e trocam o texto pela versão da IA em segundo plano).

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
    texto_ia = redigir_com_ia_validada(transacao, analise) if usar_ia else None
    if texto_ia is not None:
        return texto_ia, "watsonx"
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
