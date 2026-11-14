"""Notificações ao associado guardadas em memória (ESPECIFICACAO, seção 15; ADR-015).

Dicionário ``id_notificacao → Notificacao`` protegido por ``threading.Lock``, como as
auditorias em ``src/api/auditorias.py``; reiniciar a API apaga tudo, o que é aceitável no
protótipo.
"""

from __future__ import annotations

import threading
from datetime import datetime
from typing import Any
from uuid import uuid4

from src.associado.mensagem import TIPO_POR_DECISAO, redigir_mensagem

RESPOSTAS_VALIDAS = ("sim", "nao")
# (tipo, resposta) → (status, resultado): as regras de negócio da seção 15
RESULTADO_POR_RESPOSTA: dict[tuple[str, str], tuple[str, str]] = {
    ("CONFIRMACAO", "sim"): ("confirmada", "Compra liberada pelo associado."),
    ("CONFIRMACAO", "nao"): (
        "negada",
        "Compra bloqueada e cartão protegido. O caso foi para o analista.",
    ),
    ("AVISO_BLOQUEIO", "sim"): (
        "confirmada",
        "O associado diz que fez a compra; a liberação depende do analista.",
    ),
    ("AVISO_BLOQUEIO", "nao"): ("negada", "O associado não reconhece a compra: fraude provável."),
}

_notificacoes: dict[str, dict[str, Any]] = {}
_lock = threading.Lock()


class NotificacaoJaRespondida(Exception):  # noqa: N818 (nome em português, ADR-001)
    """Levantada quando o associado tenta responder de novo à mesma notificação."""


def _agora() -> str:
    """Momento atual em ISO 8601 sem fuso, como o resto da API."""
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def criar_notificacao(
    transacao: dict[str, Any], analise: dict[str, Any], id_transacao: int | None = None
) -> dict[str, Any]:
    """Cria a notificação de uma decisão PEDIR_CONFIRMACAO ou BLOQUEAR.

    Args:
        transacao: Campos públicos da transação, sem identificadores.
        analise: Analise do modelo, com ``decisao``.
        id_transacao: Id da transação da fila, ou None para uma análise avulsa.

    Returns:
        Notificacao criada, com ``status`` "aguardando".

    Raises:
        ValueError: Se a decisão não gera notificação (APROVAR).
    """
    mensagem, fonte = redigir_mensagem(transacao, analise)
    notificacao = {
        "id_notificacao": uuid4().hex,
        "id_transacao": id_transacao,
        "tipo": TIPO_POR_DECISAO[str(analise["decisao"])],
        "mensagem": mensagem,
        "fonte_mensagem": fonte,
        "criada_em": _agora(),
        "status": "aguardando",
        "respondida_em": None,
        "resultado": None,
    }
    with _lock:
        _notificacoes[notificacao["id_notificacao"]] = notificacao
    return dict(notificacao)


def obter(id_notificacao: str) -> dict[str, Any] | None:
    """Devolve a notificação pelo id, ou None se não existir.

    Args:
        id_notificacao: Identificador gerado em ``uuid4().hex``.

    Returns:
        Cópia da Notificacao, ou None.
    """
    with _lock:
        notificacao = _notificacoes.get(id_notificacao)
    return dict(notificacao) if notificacao is not None else None


def obter_por_transacao(id_transacao: int) -> dict[str, Any] | None:
    """Devolve a notificação de uma transação da fila, ou None se ela não foi avisada.

    Args:
        id_transacao: Identificador da transação.

    Returns:
        Cópia da Notificacao, ou None.
    """
    with _lock:
        for notificacao in _notificacoes.values():
            if notificacao["id_transacao"] == id_transacao:
                return dict(notificacao)
    return None


def listar() -> list[dict[str, Any]]:
    """Lista todas as notificações, da mais recente para a mais antiga.

    Returns:
        Cópias das Notificacoes na ordem inversa de criação.
    """
    with _lock:
        return [dict(notificacao) for notificacao in reversed(_notificacoes.values())]


def responder(id_notificacao: str, resposta: str) -> dict[str, Any]:
    """Registra a resposta do associado e aplica a regra de status e resultado.

    Args:
        id_notificacao: Identificador da notificação.
        resposta: "sim" ou "nao".

    Returns:
        Notificacao atualizada, com ``status``, ``resultado`` e ``respondida_em``.

    Raises:
        ValueError: Se a resposta não é "sim" nem "nao".
        KeyError: Se a notificação não existe.
        NotificacaoJaRespondida: Se ela já foi respondida.
    """
    if resposta not in RESPOSTAS_VALIDAS:
        raise ValueError('A resposta do associado deve ser "sim" ou "nao".')
    with _lock:
        notificacao = _notificacoes.get(id_notificacao)
        if notificacao is None:
            raise KeyError(id_notificacao)
        if notificacao["status"] != "aguardando":
            raise NotificacaoJaRespondida(
                "Esta notificação já foi respondida pelo associado e não aceita nova resposta."
            )
        status, resultado = RESULTADO_POR_RESPOSTA[(notificacao["tipo"], resposta)]
        notificacao.update(status=status, resultado=resultado, respondida_em=_agora())
        return dict(notificacao)
