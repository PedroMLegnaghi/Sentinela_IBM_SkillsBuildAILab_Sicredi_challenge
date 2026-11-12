"""Execução em segundo plano e armazenamento em memória das auditorias.

As auditorias são guardadas num dicionário ``id_auditoria → Auditoria``; reiniciar a API
apaga tudo (comportamento aceitável no protótipo — ESPECIFICACAO, seção 12).
"""

from __future__ import annotations

import logging
import threading
from typing import Any

logger = logging.getLogger(__name__)

# Dicionário em memória: id_auditoria (str) → dict com os campos de Auditoria
_auditorias: dict[str, dict[str, Any]] = {}
_lock = threading.Lock()


def obter_auditoria(id_auditoria: str) -> dict[str, Any] | None:
    """Devolve a auditoria pelo id, ou None se não existir.

    Args:
        id_auditoria: Identificador hexadecimal gerado em uuid4().hex.

    Returns:
        Dicionário com os campos de Auditoria, ou None.
    """
    with _lock:
        return _auditorias.get(id_auditoria)


def registrar_auditoria(id_auditoria: str, estado: dict[str, Any]) -> None:
    """Insere ou atualiza uma auditoria no dicionário em memória.

    Args:
        id_auditoria: Identificador da auditoria.
        estado: Dicionário com os campos de Auditoria.
    """
    with _lock:
        _auditorias[id_auditoria] = estado


def disparar_auditoria_em_segundo_plano(
    id_auditoria: str,
    transacao: dict[str, Any],
    analise: dict[str, Any],
) -> None:
    """Inicia a auditoria em segundo plano (thread daemon).

    Tenta chamar ``src.auditoria.auditar``; se o módulo não existir, encerra
    com ``status="erro"`` e mensagem informativa.

    Args:
        id_auditoria: Identificador da auditoria já criada como "pendente".
        transacao: Dicionário da transação a auditar.
        analise: Dicionário de Analise já calculada.
    """

    def _executar() -> None:
        import time  # noqa: PLC0415

        inicio = time.perf_counter()
        try:
            from src.auditoria import auditar  # noqa: PLC0415

            relatorio = auditar(transacao, analise)
            latencia_ms = (time.perf_counter() - inicio) * 1000
            registrar_auditoria(
                id_auditoria,
                {
                    "id_auditoria": id_auditoria,
                    "status": "concluida",
                    "relatorio": relatorio,
                    "latencia_ms": round(latencia_ms, 1),
                    "mensagem": None,
                },
            )
        except ImportError:
            latencia_ms = (time.perf_counter() - inicio) * 1000
            registrar_auditoria(
                id_auditoria,
                {
                    "id_auditoria": id_auditoria,
                    "status": "erro",
                    "relatorio": None,
                    "latencia_ms": round(latencia_ms, 1),
                    "mensagem": "Auditoria por IA ainda não instalada.",
                },
            )
        except Exception as erro:  # noqa: BLE001
            latencia_ms = (time.perf_counter() - inicio) * 1000
            logger.error("Falha na auditoria %s: %s", id_auditoria, erro)
            registrar_auditoria(
                id_auditoria,
                {
                    "id_auditoria": id_auditoria,
                    "status": "erro",
                    "relatorio": None,
                    "latencia_ms": round(latencia_ms, 1),
                    "mensagem": "Erro interno na auditoria.",
                },
            )

    thread = threading.Thread(target=_executar, daemon=True)
    thread.start()
