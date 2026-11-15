"""Pergunte à IA sobre este caso (ESPECIFICACAO, seção 16; Issue #66).

O analista faz uma pergunta livre sobre a compra aberta no painel. Com credenciais, o Granite
responde usando as mesmas 5 ferramentas da auditoria. Sem elas, ou se o watsonx.ai falhar, a
resposta lista o resumo de cada ferramenta e avisa que a IA está indisponível.

Nada aqui devolve identificadores, rótulo ou a decisão do sistema atual: o modelo só vê os
campos da compra e o resultado das ferramentas. O texto da pergunta nunca vai para o log.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any

import pandas as pd

from src.auditoria import watsonx
from src.auditoria.ferramentas import CaixaDeFerramentas
from src.auditoria.watsonx import FalhaWatsonx, credenciais_disponiveis
from src.config import AUDITORIA_MAX_ITERACOES, AUDITORIA_TIMEOUT_S

logger = logging.getLogger(__name__)

MAX_TOKENS_RESPOSTA = 600
LIMITE_RESPOSTA = 1200
TEXTO_INDISPONIVEL = (
    "A IA está indisponível no momento, então não consigo responder à pergunta. "
    "Resumo do que as ferramentas mostraram: "
)

INSTRUCOES_PERGUNTA = (
    "Você é auditor de prevenção a fraudes de uma cooperativa de crédito. Um analista humano "
    "está olhando uma compra com cartão e faz uma pergunta sobre ela. Responda em português do "
    "Brasil, em até 4 frases curtas. Use as ferramentas antes de responder. Só afirme o que as "
    "ferramentas mostraram; se faltar dado para responder, diga o que faltou. Nunca invente "
    "números, nunca cite identificadores e nunca recomende bloquear ou liberar a compra."
)


def _dados_da_compra(caixa: CaixaDeFerramentas) -> str:
    """Campos da compra para o modelo: só variáveis, nunca identificadores."""
    campos = {campo: caixa.transacao.get(campo) for campo in watsonx.CAMPOS_TRANSACAO}
    return json.dumps(campos, default=str)


def _responder_local(caixa: CaixaDeFerramentas) -> str:
    """Sem a IA: roda as 5 ferramentas e lista o resumo de cada uma."""
    caixa.usadas = []
    for nome in caixa.nomes():
        caixa.executar(nome)
    resumos = "; ".join(f"{item['nome']}: {item['resumo']}" for item in caixa.usadas)
    return f"{TEXTO_INDISPONIVEL}{resumos}."


def _responder_com_watsonx(pergunta: str, caixa: CaixaDeFerramentas) -> str:
    """Conversa com o Granite, que chama as ferramentas, até ele responder em texto.

    Raises:
        FalhaWatsonx: Sem resposta dentro dos limites de iterações e de tempo.
    """
    prazo = time.monotonic() + AUDITORIA_TIMEOUT_S
    mensagens: list[dict[str, Any]] = [
        {"role": "system", "content": INSTRUCOES_PERGUNTA},
        {
            "role": "user",
            "content": f"Dados da compra: {_dados_da_compra(caixa)}\n"
            f"Pergunta do analista: {pergunta}",
        },
    ]
    for _ in range(AUDITORIA_MAX_ITERACOES):
        mensagem = watsonx._chamar_chat(  # noqa: SLF001
            mensagens, caixa.definicoes(), prazo, MAX_TOKENS_RESPOSTA
        )
        mensagens.append(
            {k: v for k, v in mensagem.items() if k in ("role", "content", "tool_calls")}
        )
        if mensagem.get("tool_calls"):
            mensagens.extend(watsonx._executar_chamadas(caixa, mensagem))  # noqa: SLF001
            continue
        texto = str(mensagem.get("content") or "").strip()
        if not texto:
            raise FalhaWatsonx("Resposta vazia.")
        return texto[:LIMITE_RESPOSTA]
    raise FalhaWatsonx("Limite de iterações atingido.")


def responder_pergunta(
    pergunta: str,
    transacao: dict[str, Any],
    analise: dict[str, Any],
    base: pd.DataFrame | None,
) -> dict[str, Any]:
    """Responde a uma pergunta do analista sobre uma compra da fila.

    Args:
        pergunta: Texto já validado (1 a 300 caracteres).
        transacao: Linha completa da base; os identificadores ficam só no servidor.
        analise: Análise do modelo (sinais e contribuições).
        base: DataFrame preparado, ou None quando os dados não foram carregados.

    Returns:
        Dicionário com resposta, ferramentas_usadas, fonte ("watsonx" ou "local") e latencia_ms.
    """
    inicio = time.perf_counter()
    caixa = CaixaDeFerramentas(transacao, analise, base)
    texto: str | None = None
    fonte = "local"
    if credenciais_disponiveis():
        try:
            texto = _responder_com_watsonx(pergunta, caixa)
            fonte = "watsonx"
        except FalhaWatsonx:
            logger.warning("watsonx.ai indisponível; pergunta respondida em modo local.")
    if texto is None:
        texto = _responder_local(caixa)
    return {
        "resposta": texto,
        "ferramentas_usadas": list(caixa.usadas),
        "fonte": fonte,
        "latencia_ms": round((time.perf_counter() - inicio) * 1000, 1),
    }