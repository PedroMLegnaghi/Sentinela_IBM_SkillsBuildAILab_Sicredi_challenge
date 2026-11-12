"""Carga de dados, fila, análise, respostas e métricas para a API do Sentinela.

Responsabilidades: carregar parquet e agente na subida; montar a fila;
executar análise imediata; gravar e ler respostas do analista; servir métricas.
"""

from __future__ import annotations

import csv
import json
import logging
import math
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from src.agente import AgenteSentinela, calcular_sinais, decidir
from src.config import (
    CAMINHO_AVALIACAO,
    CAMINHO_AVALIACAO_RIGOROSA,
    CAMINHO_CUSTOS,
    CAMINHO_FEEDBACK,
    CAMINHO_METRICAS,
    CAMINHO_MODELO,
    CAMINHO_PREPARADO,
    ROTULOS_DECISAO,
)
from src.explicabilidade import contribuicoes
from src.interface.dados import montar_fila
from src.interface.feedback import RespostaAnalista, registrar_resposta

logger = logging.getLogger(__name__)


@dataclass
class _Estado:
    """Estado carregado na subida da API; mutável via atributos (sem global)."""

    base: pd.DataFrame | None = field(default=None)
    agente: AgenteSentinela | None = field(default=None)
    fila: pd.DataFrame | None = field(default=None)


# Instância única — atualizada dentro de inicializar()
_estado = _Estado()


def inicializar() -> None:
    """Carrega parquet, agente e fila na subida da API.

    Falhas de arquivo são registradas em log; a API sobe mesmo assim e informa
    o problema em ``/api/saude`` e 503 nas rotas de dados.
    """
    if CAMINHO_PREPARADO.exists() and CAMINHO_MODELO.exists():
        try:
            base = pd.read_parquet(CAMINHO_PREPARADO)
            agente = AgenteSentinela(base=base)
            fila = montar_fila(base, agente.analisar_lote)
            _estado.base = base
            _estado.agente = agente
            _estado.fila = fila
            logger.info("API inicializada: %d transações na fila.", len(fila))
        except (FileNotFoundError, OSError, ValueError) as erro:
            logger.error("Falha ao inicializar dados ou agente: %s", erro)
            _estado.base = None
            _estado.agente = None
            _estado.fila = None
    elif not CAMINHO_PREPARADO.exists():
        logger.warning("Parquet não encontrado: %s", CAMINHO_PREPARADO)
    elif not CAMINHO_MODELO.exists():
        logger.warning("Modelo não encontrado: %s", CAMINHO_MODELO)


def modelo_carregado() -> bool:
    """Retorna True se o agente foi carregado com sucesso."""
    return _estado.agente is not None


def dados_carregados() -> bool:
    """Retorna True se parquet e fila foram carregados com sucesso."""
    return _estado.base is not None and _estado.fila is not None


def _nan_para_none(valor: Any) -> Any:
    """Converte NaN e Inf em None; deixa os demais valores inalterados."""
    if isinstance(valor, float) and (math.isnan(valor) or math.isinf(valor)):
        return None
    return valor


def _data_hora_para_str(dt: Any) -> str | None:
    """Converte datetime ou Timestamp para ISO 8601 sem fuso, ou None se inválido."""
    if dt is None:
        return None
    if isinstance(dt, float) and math.isnan(dt):
        return None
    try:
        ts = pd.Timestamp(dt)
        if pd.isna(ts):
            return None
        return ts.strftime("%Y-%m-%dT%H:%M:%S")
    except (ValueError, TypeError):
        return None


def obter_fila(decisoes: list[str] | None = None) -> dict[str, Any]:
    """Monta a resposta do GET /api/fila.

    Args:
        decisoes: Lista de decisões para filtrar os itens; None usa padrão
            BLOQUEAR e PEDIR_CONFIRMACAO.

    Returns:
        Dicionário com ``total_fila``, ``contagens`` e ``itens``.

    Raises:
        RuntimeError: Se os dados não estiverem carregados.
    """
    if _estado.fila is None:
        raise RuntimeError("Dados não carregados.")

    fila = _estado.fila
    filtro = decisoes if decisoes is not None else ["BLOQUEAR", "PEDIR_CONFIRMACAO"]
    contagens = {
        decisao: int((fila["decisao"] == decisao).sum())
        for decisao in ["BLOQUEAR", "PEDIR_CONFIRMACAO", "APROVAR"]
    }
    total_fila = len(fila)
    itens_filtrados = fila[fila["decisao"].isin(filtro)].copy()

    itens = []
    for _, row in itens_filtrados.iterrows():
        itens.append(
            {
                "id_transacao": int(row["id_transacao"]),
                "nota": float(row["nota"]),
                "decisao": str(row["decisao"]),
                "valor": _nan_para_none(row.get("valor")),
                "data_hora": _data_hora_para_str(row.get("data_hora")),
                "tipo_transacao": str(row.get("tipo_transacao", "")),
                "modalidade_transacao": str(row.get("modalidade_transacao", "")),
                "n_sinais": int(row["n_sinais"]),
            }
        )

    return {"total_fila": total_fila, "contagens": contagens, "itens": itens}


def _id_esta_na_fila(id_transacao: int) -> bool:
    """Verifica se um id_transacao está na fila."""
    if _estado.fila is None:
        return False
    return bool((_estado.fila["id_transacao"] == id_transacao).any())


def _linha_da_fila(id_transacao: int) -> pd.Series | None:
    """Retorna a linha da fila para o id_transacao, ou None."""
    if _estado.fila is None:
        return None
    mask = _estado.fila["id_transacao"] == id_transacao
    if not mask.any():
        return None
    return _estado.fila[mask].iloc[0]


def analisar_transacao(transacao_dict: dict[str, Any]) -> dict[str, Any]:
    """Executa a análise imediata de uma transação.

    Mede latência de sinais + nota + decisão (sem explicação).

    Args:
        transacao_dict: Campos da transação (valores ausentes viram NaN no agente).

    Returns:
        Dicionário com os campos de Analise (ESPECIFICACAO, seção 12.1).

    Raises:
        RuntimeError: Se o agente não estiver carregado.
    """
    if _estado.agente is None:
        raise RuntimeError("Modelo não carregado.")

    agente = _estado.agente
    inicio = time.perf_counter()
    sinais = calcular_sinais(transacao_dict)
    nota = agente.pontuar(transacao_dict)
    decisao = decidir(nota, sinais)
    latencia_ms = (time.perf_counter() - inicio) * 1000

    decisao_legivel = ROTULOS_DECISAO.get(decisao, decisao)
    explicacao, _ = agente.explicar(transacao_dict, nota, sinais, decisao, usar_llm=False)

    pipeline = agente._pipeline  # noqa: SLF001
    contribs = contribuicoes(pipeline, transacao_dict)

    return {
        "nota": nota,
        "decisao": decisao,
        "decisao_legivel": decisao_legivel,
        "sinais": sinais,
        "explicacao": explicacao,
        "contribuicoes": contribs,
        "latencia_ms": round(latencia_ms, 3),
    }


def obter_transacao(id_transacao: int) -> dict[str, Any]:
    """Monta a resposta do GET /api/transacoes/{id_transacao}.

    Args:
        id_transacao: Identificador da transação.

    Returns:
        Dicionário com ``transacao``, ``analise``, ``historico`` e ``resposta_analista``.

    Raises:
        KeyError: Se o id_transacao não estiver na fila.
        RuntimeError: Se os dados não estiverem carregados.
    """
    if _estado.fila is None or _estado.base is None or _estado.agente is None:
        raise RuntimeError("Dados não carregados.")

    linha = _linha_da_fila(id_transacao)
    if linha is None:
        raise KeyError(f"Transação {id_transacao} não encontrada na fila.")

    # Busca a linha original da base para ter todos os campos incluindo id_cartao
    linha_base = _estado.base[_estado.base["id_transacao"] == id_transacao]
    if linha_base.empty:
        raise KeyError(f"Transação {id_transacao} não encontrada na base.")
    row_base = linha_base.iloc[0]

    transacao_dict = row_base.to_dict()
    analise = analisar_transacao(transacao_dict)

    id_cartao = row_base.get("id_cartao")
    data_hora_atual = row_base.get("data_hora")
    historico_df = _estado.agente.historico_cartao(id_cartao, antes_de=data_hora_atual, n=10)

    historico = [
        {
            "data_hora": _data_hora_para_str(h.get("data_hora")),
            "valor": _nan_para_none(h.get("valor")),
            "tipo_transacao": str(h.get("tipo_transacao", "")),
            "modalidade_transacao": str(h.get("modalidade_transacao", "")),
            "dist_terminal_anterior_km": _nan_para_none(h.get("dist_terminal_anterior_km")),
        }
        for _, h in historico_df.iterrows()
    ]

    ultima_resp = _ler_resposta(id_transacao)

    colunas_proibidas = {
        "fraude",
        "decisao_sistema_atual",
        "id_cartao",
        "id_cliente",
        "id_estabelecimento",
        "nota",
        "n_sinais",
        "decisao",
    }
    transacao_publica = {
        k: (_data_hora_para_str(v) if k == "data_hora" else _nan_para_none(v))
        for k, v in transacao_dict.items()
        if k not in colunas_proibidas
    }

    return {
        "transacao": transacao_publica,
        "analise": analise,
        "historico": historico,
        "resposta_analista": ultima_resp,
    }


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


def gravar_resposta(id_transacao: int, resposta: str) -> dict[str, Any]:
    """Grava a resposta do analista e retorna o objeto Resposta.

    Args:
        id_transacao: Identificador da transação.
        resposta: "fraude" ou "legitima".

    Returns:
        Dicionário com ``id_transacao``, ``resposta`` e ``registrado_em``.

    Raises:
        KeyError: Se id_transacao não estiver na fila.
        ValueError: Se resposta não for "fraude" ou "legitima".
        OSError: Se falhar ao gravar o arquivo.
    """
    if not _id_esta_na_fila(id_transacao):
        raise KeyError(f"Transação {id_transacao} não está na fila.")

    linha = _linha_da_fila(id_transacao)
    nota = float(linha["nota"]) if linha is not None else 0.0
    decisao = str(linha["decisao"]) if linha is not None else ""
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


def listar_respostas() -> dict[str, Any]:
    """Lista todas as respostas do analista (última por transação).

    Returns:
        Dicionário com ``total``, ``fraudes``, ``legitimas``, ``concordancia`` e ``itens``.
    """
    if not CAMINHO_FEEDBACK.exists():
        return {"total": 0, "fraudes": 0, "legitimas": 0, "concordancia": None, "itens": []}

    try:
        with CAMINHO_FEEDBACK.open(encoding="utf-8", newline="") as arq:
            leitor = csv.DictReader(arq)
            ultimas: dict[int, dict[str, str]] = {}
            for linha in leitor:
                tid = int(linha["id_transacao"])
                ultimas[tid] = linha
    except (OSError, ValueError) as erro:
        logger.warning("Falha ao ler feedback: %s", erro)
        return {"total": 0, "fraudes": 0, "legitimas": 0, "concordancia": None, "itens": []}

    itens = []
    concordantes = 0
    for tid, linha in ultimas.items():
        resp = linha["resposta_analista"]
        decisao = linha["decisao"]
        nota = float(linha["nota"])
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
                "nota": nota,
            }
        )

    total = len(itens)
    fraudes = sum(1 for i in itens if i["resposta"] == "fraude")
    legitimas = total - fraudes
    concordancia = round(concordantes / total * 100, 1) if total > 0 else None

    return {
        "total": total,
        "fraudes": fraudes,
        "legitimas": legitimas,
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
