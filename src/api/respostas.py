"""Gravação e listagem de respostas do analista, e métricas do modelo.

Separado de ``servicos.py`` para manter cada módulo com uma responsabilidade.
"""

from __future__ import annotations

import csv
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from src.config import (
    CAMINHO_AVALIACAO,
    CAMINHO_AVALIACAO_RIGOROSA,
    CAMINHO_CUSTOS,
    CAMINHO_FEEDBACK,
    CAMINHO_METRICAS,
)
from src.interface.feedback import RespostaAnalista, registrar_resposta

logger = logging.getLogger(__name__)


def _ler_resposta(id_transacao: int) -> dict[str, Any] | None:
    """Lê a última resposta do analista para a transação, ou None."""
    from src.interface.feedback import ler_ultima_resposta  # noqa: PLC0415

    try:
        resp = ler_ultima_resposta(CAMINHO_FEEDBACK, id_transacao)
        if resp is None:
            return None
        return {
            "id_transacao": resp.id_transacao,
            "resposta": resp.resposta_analista,
            "registrado_em": resp.registrado_em.strftime("%Y-%m-%dT%H:%M:%S"),
        }
    except (ValueError, OSError) as erro:
        logger.warning("Falha ao ler resposta do analista para %d: %s", id_transacao, erro)
        return None


def gravar_resposta(id_transacao: int, resposta: str, nota: float, decisao: str) -> dict[str, Any]:
    """Grava a resposta do analista e retorna o objeto Resposta.

    Args:
        id_transacao: Identificador da transação.
        resposta: "fraude" ou "legitima".
        nota: Nota de risco da transação na fila.
        decisao: Decisão do agente para a transação.

    Returns:
        Dicionário com ``id_transacao``, ``resposta`` e ``registrado_em``.

    Raises:
        ValueError: Se resposta não for "fraude" ou "legitima".
        OSError: Se falhar ao gravar o arquivo.
    """
    agora = datetime.now()
    obj = RespostaAnalista(
        id_transacao=id_transacao,
        nota=nota,
        decisao=decisao,
        resposta_analista=resposta,
        registrado_em=agora,
    )
    registrar_resposta(CAMINHO_FEEDBACK, obj)
    return {
        "id_transacao": id_transacao,
        "resposta": resposta,
        "registrado_em": agora.strftime("%Y-%m-%dT%H:%M:%S"),
    }


def _ler_ultimas_do_csv() -> dict[int, dict[str, str]]:
    """Lê o CSV de feedback e devolve a última linha por id_transacao.

    Returns:
        Dicionário ``{id_transacao: linha_csv}``; vazio se o arquivo não existir.
    """
    if not CAMINHO_FEEDBACK.exists():
        return {}
    try:
        with CAMINHO_FEEDBACK.open(encoding="utf-8", newline="") as arq:
            ultimas: dict[int, dict[str, str]] = {}
            for linha in csv.DictReader(arq):
                ultimas[int(linha["id_transacao"])] = linha
        return ultimas
    except (OSError, ValueError) as erro:
        logger.warning("Falha ao ler feedback: %s", erro)
        return {}


def _montar_itens_respostas(ultimas: dict[int, dict[str, str]]) -> tuple[list[dict[str, Any]], int]:
    """Converte as linhas do CSV em itens e conta as concordantes.

    Args:
        ultimas: Dicionário retornado por ``_ler_ultimas_do_csv``.

    Returns:
        Tupla ``(itens, concordantes)`` onde ``concordantes`` é o número de respostas
        em que a decisão do analista coincide com a decisão do agente.
    """
    itens: list[dict[str, Any]] = []
    concordantes = 0
    for tid, linha in ultimas.items():
        resp = linha["resposta_analista"]
        decisao = linha["decisao"]
        eh_concordante = (resp == "fraude" and decisao == "BLOQUEAR") or (
            resp == "legitima" and decisao in ("APROVAR", "PEDIR_CONFIRMACAO")
        )
        if eh_concordante:
            concordantes += 1
        itens.append(
            {
                "id_transacao": tid,
                "resposta": resp,
                "registrado_em": linha["registrado_em"],
                "decisao": decisao,
                "nota": float(linha["nota"]),
            }
        )
    return itens, concordantes


def listar_respostas() -> dict[str, Any]:
    """Lista todas as respostas do analista (última por transação).

    Returns:
        Dicionário com ``total``, ``fraudes``, ``legitimas``, ``concordancia`` e ``itens``.
    """
    ultimas = _ler_ultimas_do_csv()
    if not ultimas:
        return {"total": 0, "fraudes": 0, "legitimas": 0, "concordancia": None, "itens": []}

    itens, concordantes = _montar_itens_respostas(ultimas)
    total = len(itens)
    fraudes = sum(1 for i in itens if i["resposta"] == "fraude")
    concordancia = round(concordantes / total * 100, 1) if total > 0 else None
    return {
        "total": total,
        "fraudes": fraudes,
        "legitimas": total - fraudes,
        "concordancia": concordancia,
        "itens": itens,
    }


def _carregar_json_opcional(caminho: Path) -> dict[str, Any] | None:
    """Carrega um JSON, retornando None se não existir."""
    if not caminho.exists():
        return None
    try:
        with caminho.open(encoding="utf-8") as arq:
            return json.load(arq)
    except (OSError, ValueError) as erro:
        logger.warning("Falha ao carregar %s: %s", caminho, erro)
        return None


def obter_metricas() -> dict[str, Any]:
    """Monta a resposta do GET /api/metricas.

    Returns:
        Dicionário com ``metricas``, ``avaliacao`` e ``extras``.

    Raises:
        RuntimeError: Se metricas.json ou avaliacao_agente.json não existirem.
    """
    metricas = _carregar_json_opcional(CAMINHO_METRICAS)
    avaliacao = _carregar_json_opcional(CAMINHO_AVALIACAO)
    if metricas is None or avaliacao is None:
        raise RuntimeError(
            "Arquivos de métricas não encontrados. "
            "Rode: python -m src.treinar_modelo e python -m src.avaliar_agente"
        )
    extras = {
        "avaliacao_rigorosa": _carregar_json_opcional(CAMINHO_AVALIACAO_RIGOROSA),
        "custos": _carregar_json_opcional(CAMINHO_CUSTOS),
        "eda": None,
        "ia_contra_modelo": None,
    }
    return {"metricas": metricas, "avaliacao": avaliacao, "extras": extras}
