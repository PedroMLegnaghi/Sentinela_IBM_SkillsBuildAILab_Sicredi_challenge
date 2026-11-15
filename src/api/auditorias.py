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


def _registrar_resultado(
    id_auditoria: str,
    *,
    status: str,
    relatorio: dict[str, Any] | None,
    latencia_ms: float,
    mensagem: str | None,
) -> None:
    """Persiste o resultado final de uma auditoria no dicionário em memória.

    Args:
        id_auditoria: Identificador da auditoria.
        status: "concluida" ou "erro".
        relatorio: Relatório produzido por ``auditar``, ou None.
        latencia_ms: Tempo total de execução em milissegundos.
        mensagem: Mensagem de erro, ou None.
    """
    registrar_auditoria(
        id_auditoria,
        {
            "id_auditoria": id_auditoria,
            "status": status,
            "relatorio": relatorio,
            "latencia_ms": round(latencia_ms, 1),
            "mensagem": mensagem,
        },
    )


def _executar_auditoria(
    id_auditoria: str,
    transacao: dict[str, Any],
    analise: dict[str, Any],
) -> None:
    """Executa a auditoria e persiste o resultado (chamada dentro de thread daemon).

    Tenta importar ``src.auditoria.auditar``; captura ``ImportError`` quando o módulo
    não existe ainda, e ``ValueError``, ``KeyError``, ``TypeError`` e ``OSError`` para
    dados inválidos ou falhas de I/O.

    Args:
        id_auditoria: Identificador da auditoria já criada como "pendente".
        transacao: Dicionário da transação a auditar.
        analise: Dicionário de Analise já calculada.
    """
    import time  # noqa: PLC0415

    inicio = time.perf_counter()
    try:
        from src.auditoria import auditar  # noqa: PLC0415

        relatorio = auditar(transacao, analise)
        _registrar_resultado(
            id_auditoria,
            status="concluida",
            relatorio=relatorio,
            latencia_ms=(time.perf_counter() - inicio) * 1000,
            mensagem=None,
        )
    except ImportError:
        _registrar_resultado(
            id_auditoria,
            status="erro",
            relatorio=None,
            latencia_ms=(time.perf_counter() - inicio) * 1000,
            mensagem="Auditoria por IA ainda não instalada.",
        )
    except (ValueError, KeyError, TypeError, OSError) as erro:
        logger.error("Falha na auditoria %s: %s", id_auditoria, erro)
        _registrar_resultado(
            id_auditoria,
            status="erro",
            relatorio=None,
            latencia_ms=(time.perf_counter() - inicio) * 1000,
            mensagem="Erro interno na auditoria.",
        )


def disparar_auditoria_em_segundo_plano(
    id_auditoria: str,
    transacao: dict[str, Any],
    analise: dict[str, Any],
) -> None:
    """Inicia a auditoria em segundo plano (thread daemon).

    Args:
        id_auditoria: Identificador da auditoria já criada como "pendente".
        transacao: Dicionário da transação a auditar.
        analise: Dicionário de Analise já calculada.
    """
    thread = threading.Thread(
        target=_executar_auditoria,
        args=(id_auditoria, transacao, analise),
        daemon=True,
    )
    thread.start()
