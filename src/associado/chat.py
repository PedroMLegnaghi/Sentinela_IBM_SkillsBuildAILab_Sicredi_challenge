"""Chat do associado com a IA (ESPECIFICACAO, seção 17.6; Issue #105).

A IA só informa: responde sobre os gastos e as compras do próprio associado, com o motivo
genérico das bloqueadas. O contexto nunca leva identificadores, sinais, nota ou parecer da IA.
Sem credenciais, em falha ou com uma resposta fora das regras, vale o resumo local.
"""

from __future__ import annotations

import logging
import unicodedata
from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

from src.associado.mensagem import formatar_moeda
from src.auditoria import watsonx
from src.config import MENSAGEM_TERMOS_PROIBIDOS

logger = logging.getLogger(__name__)

MAX_CARACTERES_RESPOSTA = 400
MAX_TOKENS = 220
TIMEOUT_S = 20
ULTIMAS_COMPRAS = 20
MAX_HISTORICO = 20
MOTIVO_GENERICO = "A compra fugiu do seu padrão de uso e foi bloqueada por segurança."
RECUSA_PADRAO = (
    "Posso ajudar só com as suas compras: gastos do mês, saldo, limite e compras pendentes "
    "ou bloqueadas. O que você quer saber sobre elas?"
)
# Palavras (sem acento) que mostram que a pergunta é sobre as compras do associado
ASSUNTOS = (
    "compr",
    "gast",
    "saldo",
    "cartao",
    "bloque",
    "limite",
    "extrato",
    "valor",
    "mes",
    "quanto",
    "debito",
    "credito",
    "aviso",
    "pendente",
    "confirm",
    "transac",
    "pague",
    "pagamento",
    "loja",
    "mercado",
    "estabelecimento",
    "dinheiro",
    "fatura",
    "resumo",
    "conta",
    "reconhe",
    "fui eu",
    "suspeit",
    "fraude",
)
PROMESSAS = (
    "vou liberar",
    "vamos liberar",
    "liberaremos",
    "vou bloquear",
    "vamos bloquear",
    "desbloque",
    "estornar",
    "estornaremos",
)
INSTRUCOES_CHAT = (
    "Você é o assistente do app do associado de uma cooperativa de crédito. Responda em "
    "português do Brasil, em até 400 caracteres, só com base nos dados enviados sobre as "
    "compras do próprio associado. Explique compras bloqueadas apenas com o motivo genérico "
    "enviado. Nunca peça senha, código, token ou dados do cartão. Nunca prometa liberar, "
    "bloquear ou estornar nada: você só informa. Se a pergunta não for sobre as compras, "
    "diga que só pode ajudar com as compras do associado."
)
NOMES_TIPO = {"debito": "débito", "credito": "crédito"}


def _sem_acento(texto: str) -> str:
    normal = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in normal if not unicodedata.combining(c))


def sobre_as_compras(mensagem: str) -> bool:
    """True se a pergunta trata das compras, gastos ou cartões do associado."""
    texto = _sem_acento(mensagem)
    return any(assunto in texto for assunto in ASSUNTOS)


def resposta_valida(texto: str) -> bool:
    """Regras da resposta da IA: curta, sem pedir dado sigiloso, sem link e sem prometer ação."""
    minusculas = texto.lower()
    if not texto or len(texto) > MAX_CARACTERES_RESPOSTA:
        return False
    if any(termo in minusculas for termo in MENSAGEM_TERMOS_PROIBIDOS):
        return False
    return not any(promessa in minusculas for promessa in PROMESSAS)


def _compras_publicas(compras: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Só estabelecimento, data, valor, tipo e situação; nada de ids, sinais ou nota."""
    return [
        {
            "estabelecimento": c.get("estabelecimento"),
            "data_hora": c.get("data_hora"),
            "valor": c.get("valor"),
            "tipo_transacao": c.get("tipo_transacao"),
            "situacao": c.get("situacao"),
        }
        for c in compras
    ]


def _mes_mais_recente(compras: Sequence[Mapping[str, Any]]) -> str | None:
    meses = [str(c["data_hora"])[:7] for c in compras if c.get("data_hora")]
    return max(meses) if meses else None


def resumir_gastos(contexto: Mapping[str, Any]) -> dict[str, Any]:
    """Totais do mês mais recente por tipo, e quantas compras aguardam ou estão bloqueadas."""
    compras = _compras_publicas(contexto.get("compras", []))
    mes = _mes_mais_recente(compras)
    do_mes = [c for c in compras if mes and str(c.get("data_hora") or "").startswith(mes)]
    aprovadas = [c for c in do_mes if c["situacao"] == "APROVADA" and c["valor"] is not None]
    por_tipo: Counter[str] = Counter()
    for compra in aprovadas:
        por_tipo[str(compra["tipo_transacao"])] += float(compra["valor"])
    situacoes = Counter(c["situacao"] for c in compras)
    return {
        "mes": mes,
        "quantidade": len(aprovadas),
        "total": round(sum(por_tipo.values()), 2),
        "por_tipo": {tipo: round(valor, 2) for tipo, valor in por_tipo.items()},
        "aguardando": situacoes.get("AGUARDANDO", 0),
        "bloqueadas": situacoes.get("BLOQUEADA", 0),
    }


def resposta_local(contexto: Mapping[str, Any]) -> str:
    """Resumo fixo dos gastos do mês e das compras pendentes ou bloqueadas."""
    resumo = resumir_gastos(contexto)
    if resumo["mes"] is None:
        return "Ainda não há compras no seu extrato. " + RECUSA_PADRAO
    mes = f"{resumo['mes'][5:7]}/{resumo['mes'][:4]}"
    tipos = ", ".join(
        f"{NOMES_TIPO.get(tipo, tipo)} {formatar_moeda(valor)}"
        for tipo, valor in sorted(resumo["por_tipo"].items())
    )
    texto = (
        f"Em {mes} você fez {resumo['quantidade']} compras aprovadas, somando "
        f"{formatar_moeda(resumo['total'])}" + (f" ({tipos})" if tipos else "") + ". "
    )
    texto += (
        f"{resumo['aguardando']} aguardam sua confirmação e {resumo['bloqueadas']} estão "
        f"bloqueadas. {MOTIVO_GENERICO}"
        if resumo["aguardando"] or resumo["bloqueadas"]
        else "Nenhuma compra aguarda confirmação ou está bloqueada."
    )
    return texto


def montar_pedido(
    mensagem: str, historico: Sequence[Mapping[str, str]], contexto: Mapping[str, Any]
) -> str:
    """Texto enviado ao watsonx.ai: resumo, últimas compras, histórico e a pergunta."""
    compras = _compras_publicas(contexto.get("compras", []))[:ULTIMAS_COMPRAS]
    linhas = [
        f"Saldo: {formatar_moeda(float(contexto.get('saldo') or 0))}. Limite disponível: "
        f"{formatar_moeda(float(contexto.get('limite_disponivel') or 0))}.",
        f"Resumo do mês: {resumir_gastos(contexto)}.",
        f"Motivo de toda compra bloqueada: {MOTIVO_GENERICO}",
        "Últimas compras:",
        *(
            f"- {c['data_hora']} | {c['estabelecimento']} | {c['valor']} | "
            f"{c['tipo_transacao']} | {c['situacao']}"
            for c in compras
        ),
        "Conversa até aqui:",
        *(f"{m.get('autor')}: {m.get('texto')}" for m in list(historico)[-MAX_HISTORICO:]),
        f"Pergunta do associado: {mensagem}",
    ]
    return "\n".join(linhas)


def responder(
    mensagem: str, historico: Sequence[Mapping[str, str]], contexto: Mapping[str, Any]
) -> dict[str, str]:
    """Responde à pergunta do associado.

    Args:
        mensagem: Pergunta do associado (1 a 500 caracteres).
        historico: Conversa até aqui, como o site guardou.
        contexto: ``saldo``, ``limite_disponivel`` e ``compras`` (CompraExtrato) do associado.

    Returns:
        ``{"resposta": str, "fonte": "watsonx" | "local"}``.
    """
    if not sobre_as_compras(mensagem):
        return {"resposta": RECUSA_PADRAO, "fonte": "local"}
    if watsonx.credenciais_disponiveis():
        try:
            texto = watsonx.redigir_texto(
                INSTRUCOES_CHAT, montar_pedido(mensagem, historico, contexto), MAX_TOKENS, TIMEOUT_S
            )
        except watsonx.FalhaWatsonx as erro:
            logger.warning("Chat pela IA indisponível; usando o resumo local: %s", erro)
        else:
            texto = " ".join(texto.split())
            if resposta_valida(texto):
                return {"resposta": texto, "fonte": "watsonx"}
            logger.warning("Resposta do chat fora das regras (%d caracteres).", len(texto))
    return {"resposta": resposta_local(contexto), "fonte": "local"}


def resumir_para_gerente(
    historico: Sequence[Mapping[str, str]], contexto: Mapping[str, Any]
) -> str:
    """Resumo da conversa até ali, para abrir o "conversar com gerente" (simulado)."""
    perguntas = [str(m.get("texto", ""))[:80] for m in historico if m.get("autor") == "associado"][
        -3:
    ]
    resumo = resumir_gastos(contexto)
    assuntos = "; ".join(f"“{p}”" for p in perguntas) if perguntas else "nenhuma pergunta ainda"
    return (
        f"Resumo da conversa: o associado perguntou {assuntos}. No extrato, "
        f"{resumo['aguardando']} compras aguardam confirmação e {resumo['bloqueadas']} estão "
        "bloqueadas."
    )
