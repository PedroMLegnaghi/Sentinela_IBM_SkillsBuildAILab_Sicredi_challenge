"""Auditoria com o IBM watsonx.ai: chat com chamada de ferramentas (ESPECIFICACAO, seção 13).

Credenciais só por variáveis de ambiente (ADR-013). Toda falha levanta ``FalhaWatsonx``, e
quem chama cai no modo local. O log nunca registra a chave nem o texto do modelo.
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
from pathlib import Path
from typing import Any

import requests

from src.auditoria.ferramentas import CaixaDeFerramentas
from src.auditoria.relatorio import validar_parcial
from src.config import (
    AUDITORIA_MAX_ITERACOES,
    AUDITORIA_MODELO_PADRAO,
    AUDITORIA_TIMEOUT_S,
    CAMINHO_ENV,
    WATSONX_URL_IAM,
    WATSONX_URL_PADRAO,
    WATSONX_VERSAO_API,
)

logger = logging.getLogger(__name__)

MARGEM_TOKEN_S = 60
MAX_TOKENS_RESPOSTA = 900
CAMPOS_TRANSACAO = ("valor", "data_hora", "tipo_transacao", "modalidade_transacao")

INSTRUCOES = (
    "Você é auditor de prevenção a fraudes de uma cooperativa de crédito. Um modelo de "
    "machine learning já decidiu esta compra com cartão; você investiga de forma "
    "independente e dá uma segunda opinião ao analista humano. Escreva em português do "
    "Brasil. Use as ferramentas antes de concluir. Só afirme o que as ferramentas mostraram "
    "e liste o que faltou. Se a evidência for insuficiente ou contraditória, use risco_ia "
    "null ou confianca BAIXA. Nunca recomende bloquear ou liberar por conta própria.\n"
    'Responda no fim SOMENTE com um JSON com as chaves: risco_ia ("BAIXO", "SUSPEITO", '
    '"ALTO" ou null), confianca ("BAIXA", "MEDIA" ou "ALTA"), explicacao (até 600 '
    "caracteres), evidencias_a_favor, evidencias_contra e dados_ausentes (listas de frases)."
)


class FalhaWatsonx(Exception):  # noqa: N818 (nome em português, ADR-001)
    """O watsonx.ai não respondeu, respondeu com erro ou com um relatório inválido."""


_token: dict[str, Any] = {"valor": None, "expira": 0.0}


def carregar_env(caminho: Path = CAMINHO_ENV) -> None:
    """Lê ``KEY=VALOR`` do arquivo ``.env`` sem sobrescrever variáveis já definidas.

    Args:
        caminho: Caminho do arquivo; ausente não é erro.
    """
    if not caminho.exists():
        return
    for linha_bruta in caminho.read_text(encoding="utf-8").splitlines():
        linha = linha_bruta.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, valor = linha.split("=", 1)
        if valor.strip():
            os.environ.setdefault(chave.strip(), valor.strip().strip("\"'"))


def credenciais_disponiveis() -> bool:
    """True se WATSONX_APIKEY e WATSONX_PROJECT_ID estiverem definidas."""
    return bool(os.environ.get("WATSONX_APIKEY") and os.environ.get("WATSONX_PROJECT_ID"))


def _obter_token(prazo: float) -> str:
    """Token IAM, guardado até perto de expirar.

    Args:
        prazo: Instante (``time.monotonic``) em que a auditoria inteira precisa acabar.

    Returns:
        O token de acesso.

    Raises:
        FalhaWatsonx: Se o IAM não responder ou responder sem token.
    """
    if _token["valor"] and time.time() < _token["expira"] - MARGEM_TOKEN_S:
        return _token["valor"]
    try:
        resposta = requests.post(
            WATSONX_URL_IAM,
            data={
                "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                "apikey": os.environ["WATSONX_APIKEY"],
            },
            timeout=max(1.0, prazo - time.monotonic()),
        )
        resposta.raise_for_status()
        corpo = resposta.json()
        _token["valor"], _token["expira"] = corpo["access_token"], float(corpo["expiration"])
    except (requests.RequestException, ValueError, KeyError) as erro:
        raise FalhaWatsonx(f"IAM indisponível ({type(erro).__name__}).") from erro
    return _token["valor"]


def _chamar_chat(mensagens: list[dict[str, Any]], ferramentas: list[dict], prazo: float) -> dict:
    """Uma chamada ao endpoint de chat do watsonx.ai.

    Args:
        mensagens: Conversa até aqui.
        ferramentas: Definições das ferramentas.
        prazo: Instante (``time.monotonic``) limite da auditoria.

    Returns:
        A mensagem do assistente (com ``content`` e/ou ``tool_calls``).

    Raises:
        FalhaWatsonx: Em erro de rede, de HTTP ou de formato.
    """
    restante = prazo - time.monotonic()
    if restante <= 0:
        raise FalhaWatsonx("Tempo da auditoria esgotado.")
    url = os.environ.get("WATSONX_URL") or WATSONX_URL_PADRAO
    corpo = {
        "model_id": os.environ.get("WATSONX_MODELO") or AUDITORIA_MODELO_PADRAO,
        "project_id": os.environ["WATSONX_PROJECT_ID"],
        "messages": mensagens,
        "tools": ferramentas,
        "tool_choice_option": "auto",
        "max_tokens": MAX_TOKENS_RESPOSTA,
        "temperature": 0,
    }
    try:
        resposta = requests.post(
            f"{url}/ml/v1/text/chat?version={WATSONX_VERSAO_API}",
            headers={"Authorization": f"Bearer {_obter_token(prazo)}"},
            json=corpo,
            timeout=restante,
        )
        resposta.raise_for_status()
        return resposta.json()["choices"][0]["message"]
    except (requests.RequestException, ValueError, KeyError, IndexError) as erro:
        raise FalhaWatsonx(f"Chat indisponível ({type(erro).__name__}).") from erro


def _extrair_json(texto: str) -> dict[str, Any]:
    """Primeiro objeto JSON do texto do modelo.

    Raises:
        ValueError: Se não houver JSON válido.
    """
    achado = re.search(r"\{.*\}", texto or "", flags=re.DOTALL)
    if achado is None:
        raise ValueError("Resposta sem JSON.")
    return json.loads(achado.group(0))


def _mensagem_inicial(caixa: CaixaDeFerramentas) -> str:
    """Dados da compra para o modelo: só variáveis, nunca identificadores."""
    campos = {campo: caixa.transacao.get(campo) for campo in CAMPOS_TRANSACAO}
    return "Audite esta compra com cartão. Dados: " + json.dumps(campos, default=str)


def _executar_chamadas(caixa: CaixaDeFerramentas, mensagem: dict[str, Any]) -> list[dict]:
    """Executa as ferramentas pedidas e devolve as mensagens de resultado."""
    resultados = []
    for chamada in mensagem.get("tool_calls") or []:
        nome = chamada["function"]["name"]
        try:
            conteudo = caixa.executar(nome)
        except KeyError:
            conteudo = {"status": "erro", "dados": {}, "campos_ausentes": [], "erro": "inexistente"}
        resultados.append(
            {"role": "tool", "tool_call_id": chamada["id"], "content": json.dumps(conteudo)}
        )
    return resultados


def auditar_com_watsonx(caixa: CaixaDeFerramentas) -> tuple[dict[str, Any], str]:
    """Conduz a conversa com ferramentas até o relatório final validado.

    Args:
        caixa: Ferramentas ligadas à transação auditada.

    Returns:
        Tupla (parte validada do relatório, nome do modelo usado).

    Raises:
        FalhaWatsonx: Sem resposta válida dentro dos limites de iterações e de tempo.
    """
    prazo = time.monotonic() + AUDITORIA_TIMEOUT_S
    mensagens: list[dict[str, Any]] = [
        {"role": "system", "content": INSTRUCOES},
        {"role": "user", "content": _mensagem_inicial(caixa)},
    ]
    nova_tentativa_usada = False
    for _ in range(AUDITORIA_MAX_ITERACOES):
        mensagem = _chamar_chat(mensagens, caixa.definicoes(), prazo)
        mensagens.append(
            {k: v for k, v in mensagem.items() if k in ("role", "content", "tool_calls")}
        )
        if mensagem.get("tool_calls"):
            mensagens.extend(_executar_chamadas(caixa, mensagem))
            continue
        try:
            parcial = validar_parcial(_extrair_json(mensagem.get("content", "")))
        except ValueError:
            if nova_tentativa_usada:
                raise FalhaWatsonx("Relatório inválido duas vezes.") from None
            nova_tentativa_usada = True
            mensagens.append({"role": "user", "content": "Responda somente com o JSON pedido."})
            continue
        return parcial, os.environ.get("WATSONX_MODELO") or AUDITORIA_MODELO_PADRAO
    raise FalhaWatsonx("Limite de iterações atingido.")
