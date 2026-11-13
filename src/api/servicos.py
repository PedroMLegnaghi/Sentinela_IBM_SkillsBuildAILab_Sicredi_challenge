"""Carga de dados, fila e análise de transações para a API do Sentinela.

Responsabilidades: carregar parquet e agente na subida; montar a fila;
executar análise imediata. Respostas e métricas ficam em ``src.api.respostas``.
"""

from __future__ import annotations

import logging
import math
import time
from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from src.agente import AgenteSentinela, calcular_sinais, decidir
from src.auditoria import configurar_base
from src.auditoria.watsonx import carregar_env
from src.config import (
    CAMINHO_MODELO,
    CAMINHO_PREPARADO,
    ROTULOS_DECISAO,
)
from src.explicabilidade import contribuicoes
from src.interface.dados import montar_fila

logger = logging.getLogger(__name__)


@dataclass
class _Estado:
    """Estado carregado na subida da API; mutável via atributos (sem global)."""

    base: pd.DataFrame | None = field(default=None)
    agente: AgenteSentinela | None = field(default=None)
    fila: pd.DataFrame | None = field(default=None)


# Instância única — atualizada dentro de inicializar()
_estado = _Estado()


def _carregar_agente(base: pd.DataFrame | None) -> AgenteSentinela | None:
    """Carrega o agente com o modelo salvo, com ou sem a base de histórico.

    Args:
        base: DataFrame preparado, ou None quando o parquet não está disponível.

    Returns:
        O agente carregado, ou None se o modelo não puder ser lido.
    """
    try:
        return AgenteSentinela(base=base)
    except (FileNotFoundError, OSError, ValueError) as erro:
        logger.error("Falha ao carregar o modelo: %s", erro)
        return None


def _ler_base() -> pd.DataFrame | None:
    """Lê o parquet preparado, ou devolve None se ele faltar ou estiver ilegível."""
    if not CAMINHO_PREPARADO.exists():
        logger.warning("Parquet não encontrado: %s", CAMINHO_PREPARADO)
        return None
    try:
        return pd.read_parquet(CAMINHO_PREPARADO)
    except (OSError, ValueError) as erro:
        logger.error("Falha ao ler o parquet: %s", erro)
        return None


def inicializar() -> None:
    """Carrega o modelo e, se houver, o parquet e a fila na subida da API.

    O modelo carrega sozinho, para ``/api/analisar`` funcionar sem os dados.
    Sem o parquet, as rotas de dados respondem 503 e ``/api/saude`` informa.
    """
    _estado.base = None
    _estado.fila = None
    _estado.agente = None
    carregar_env()
    configurar_base(None)
    if not CAMINHO_MODELO.exists():
        logger.warning("Modelo não encontrado: %s", CAMINHO_MODELO)
        return
    base = _ler_base()
    _estado.agente = _carregar_agente(base)
    if _estado.agente is None or base is None:
        return
    try:
        _estado.fila = montar_fila(base, _estado.agente.analisar_lote)
    except (KeyError, ValueError) as erro:
        logger.error("Falha ao montar a fila: %s", erro)
        return
    _estado.base = base
    configurar_base(base)
    logger.info("API inicializada: %d transações na fila.", len(_estado.fila))


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
    contribs = contribuicoes(agente._pipeline, transacao_dict)  # noqa: SLF001

    return {
        "nota": nota,
        "decisao": decisao,
        "decisao_legivel": decisao_legivel,
        "sinais": sinais,
        "explicacao": explicacao,
        "contribuicoes": contribs,
        "latencia_ms": round(latencia_ms, 3),
    }


_COLUNAS_PROIBIDAS = frozenset(
    {
        "fraude",
        "decisao_sistema_atual",
        "id_cartao",
        "id_cliente",
        "id_estabelecimento",
        "nota",
        "n_sinais",
        "decisao",
    }
)


def _montar_historico(historico_df: pd.DataFrame) -> list[dict[str, Any]]:
    """Converte o DataFrame do histórico em lista de ItemHistorico.

    Args:
        historico_df: DataFrame retornado por ``AgenteSentinela.historico_cartao``.

    Returns:
        Lista de dicts com data_hora, valor, tipo_transacao, modalidade_transacao
        e dist_terminal_anterior_km.
    """
    return [
        {
            "data_hora": _data_hora_para_str(h.get("data_hora")),
            "valor": _nan_para_none(h.get("valor")),
            "tipo_transacao": str(h.get("tipo_transacao", "")),
            "modalidade_transacao": str(h.get("modalidade_transacao", "")),
            "dist_terminal_anterior_km": _nan_para_none(h.get("dist_terminal_anterior_km")),
        }
        for _, h in historico_df.iterrows()
    ]


def _montar_transacao_publica(transacao_dict: dict[str, Any]) -> dict[str, Any]:
    """Filtra campos proibidos e normaliza NaN/datas para serialização JSON.

    Args:
        transacao_dict: Linha completa da base (inclui id_cartao, fraude etc.).

    Returns:
        Dicionário com apenas os campos públicos da Transacao.
    """
    return {
        k: (_data_hora_para_str(v) if k == "data_hora" else _nan_para_none(v))
        for k, v in transacao_dict.items()
        if k not in _COLUNAS_PROIBIDAS
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

    if _linha_da_fila(id_transacao) is None:
        raise KeyError(f"Transação {id_transacao} não encontrada na fila.")

    linha_base = _estado.base[_estado.base["id_transacao"] == id_transacao]
    if linha_base.empty:
        raise KeyError(f"Transação {id_transacao} não encontrada na base.")

    row_base = linha_base.iloc[0]
    transacao_dict = row_base.to_dict()
    analise = analisar_transacao(transacao_dict)

    historico_df = _estado.agente.historico_cartao(
        row_base.get("id_cartao"), antes_de=row_base.get("data_hora"), n=10
    )

    from src.api.respostas import _ler_resposta  # noqa: PLC0415

    return {
        "transacao": _montar_transacao_publica(transacao_dict),
        "analise": analise,
        "historico": _montar_historico(historico_df),
        "resposta_analista": _ler_resposta(id_transacao),
    }


def transacao_para_auditoria(id_transacao: int) -> dict[str, Any]:
    """Linha completa da transação na base, só para as ferramentas da auditoria.

    Os identificadores internos ficam dentro do servidor: a auditoria não os devolve nem os
    envia ao watsonx.ai (ESPECIFICACAO, seção 13).

    Args:
        id_transacao: Identificador da transação.

    Returns:
        Dicionário com todas as colunas da base para essa transação.

    Raises:
        KeyError: Se a transação não estiver na base.
        RuntimeError: Se os dados não estiverem carregados.
    """
    if _estado.base is None:
        raise RuntimeError("Dados não carregados.")
    linha = _estado.base[_estado.base["id_transacao"] == id_transacao]
    if linha.empty:
        raise KeyError(f"Transação {id_transacao} não encontrada na base.")
    return linha.iloc[0].to_dict()


def dados_fila_para_resposta(id_transacao: int) -> tuple[float, str] | None:
    """Retorna (nota, decisao) de uma transação da fila, ou None se ausente.

    Usado por ``app.py`` ao gravar a resposta do analista.

    Args:
        id_transacao: Identificador da transação.

    Returns:
        Tupla ``(nota, decisao)`` ou None.
    """
    linha = _linha_da_fila(id_transacao)
    if linha is None:
        return None
    return float(linha["nota"]), str(linha["decisao"])
