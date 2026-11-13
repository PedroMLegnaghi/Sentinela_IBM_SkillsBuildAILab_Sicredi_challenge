"""Compara a auditoria por IA com o modelo: latência e concordância (Issue #46; ADR-012).

Uso: ``python -m src.avaliar_ia``. Com as credenciais do watsonx.ai no ``.env``, audita pelo
watsonx; sem elas, pelo modo local (o JSON registra quantas auditorias foram de cada fonte).
Grava só agregados em ``modelos/ia_contra_modelo.json``; nenhum identificador.
"""

from __future__ import annotations

import json
import time
from collections import Counter
from collections.abc import Callable
from typing import Any

import numpy as np
import pandas as pd

from src.agente import AgenteSentinela, calcular_sinais, decidir
from src.auditoria import auditar, configurar_base
from src.auditoria.watsonx import carregar_env
from src.config import (
    CAMINHO_IA_CONTRA_MODELO,
    CAMINHO_PREPARADO,
    FIM_TESTE,
    INICIO_TESTE,
    SEMENTE,
)

TAMANHO_AMOSTRA_LEGITIMAS_IA = 200
PAUSA_ENTRE_AUDITORIAS_S = 0.5
DECISOES = ("APROVAR", "PEDIR_CONFIRMACAO", "BLOQUEAR")
RISCOS_DE_ALERTA = ("ALTO", "SUSPEITO")
PERCENTIS = (50, 95)


def montar_amostra(
    base: pd.DataFrame, tamanho_legitimas: int = TAMANHO_AMOSTRA_LEGITIMAS_IA
) -> pd.DataFrame:
    """Todas as fraudes de março e uma amostra de legítimas de março (semente fixa).

    Args:
        base: DataFrame preparado.
        tamanho_legitimas: Quantidade de legítimas sorteadas.

    Returns:
        DataFrame com as linhas sorteadas, em ordem de data.
    """
    marco = base[(base["data_hora"] >= INICIO_TESTE) & (base["data_hora"] < FIM_TESTE)]
    fraudes = marco[marco["fraude"] == 1]
    legitimas = marco[marco["fraude"] == 0]
    sorteadas = legitimas.sample(n=min(tamanho_legitimas, len(legitimas)), random_state=SEMENTE)
    return pd.concat([fraudes, sorteadas]).sort_values("data_hora")


def medir_transacao(
    agente: AgenteSentinela, transacao: dict[str, Any], auditar_fn: Callable[..., dict]
) -> dict[str, Any]:
    """Decide com o modelo e audita, medindo o tempo de cada caminho.

    Args:
        agente: Agente com o modelo carregado.
        transacao: Linha da base (com o rótulo, usado só nesta avaliação).
        auditar_fn: Função de auditoria (``src.auditoria.auditar`` ou falsa nos testes).

    Returns:
        Registro com rótulo, decisão, relatório resumido e as duas latências em ms.
    """
    inicio = time.perf_counter()
    sinais = calcular_sinais(transacao)
    decisao = decidir(agente.pontuar(transacao), sinais)
    ms_modelo = (time.perf_counter() - inicio) * 1000
    entrada = {k: v for k, v in transacao.items() if k != "fraude"}
    inicio = time.perf_counter()
    relatorio = auditar_fn(entrada, {"decisao": decisao, "sinais": sinais, "contribuicoes": []})
    ms_ia = (time.perf_counter() - inicio) * 1000
    return {
        "fraude": int(transacao["fraude"]),
        "decisao": decisao,
        "risco_ia": relatorio["risco_ia"],
        "parecer": relatorio["parecer"],
        "fonte": relatorio["fonte"],
        "ms_modelo": ms_modelo,
        "ms_ia": ms_ia,
    }


def _percentis(valores: list[float]) -> dict[str, float]:
    """p50 e p95 em milissegundos, com 2 casas."""
    return {f"p{p}_ms": round(float(np.percentile(valores, p)), 2) for p in PERCENTIS}


def _acerto(alertas: list[bool], fraudes: list[int]) -> dict[str, float | int | None]:
    """Recall e precisão (em %) de um conjunto de alertas contra o rótulo."""
    verdadeiros = sum(1 for a, f in zip(alertas, fraudes, strict=True) if a and f)
    total_alertas, total_fraudes = sum(alertas), sum(fraudes)
    return {
        "alertas": total_alertas,
        "fraudes_pegas": verdadeiros,
        "recall": round(verdadeiros / total_fraudes * 100, 1) if total_fraudes else None,
        "precisao": round(verdadeiros / total_alertas * 100, 1) if total_alertas else None,
    }


def resumir(registros: list[dict[str, Any]]) -> dict[str, Any]:
    """Agrega os registros: latências, pareceres, concordância e acerto de cada lado.

    Args:
        registros: Saídas de ``medir_transacao``.

    Returns:
        Dicionário só com agregados (nenhum identificador).
    """
    fraudes = [r["fraude"] for r in registros]
    concordancia = {}
    for decisao in DECISOES:
        grupo = [r for r in registros if r["decisao"] == decisao]
        confirma = sum(1 for r in grupo if r["parecer"] == "CONFIRMA")
        concordancia[decisao] = round(confirma / len(grupo) * 100, 1) if grupo else None
    return {
        "transacoes": len(registros),
        "fraudes": sum(fraudes),
        "fontes": dict(Counter(r["fonte"] for r in registros)),
        "latencia_modelo": _percentis([r["ms_modelo"] for r in registros]),
        "latencia_ia": _percentis([r["ms_ia"] for r in registros]),
        "pareceres": dict(Counter(r["parecer"] for r in registros)),
        "concordancia_por_decisao": concordancia,
        "modelo": _acerto([r["decisao"] != "APROVAR" for r in registros], fraudes),
        "ia_sozinha": _acerto([r["risco_ia"] in RISCOS_DE_ALERTA for r in registros], fraudes),
    }


def main() -> None:
    """Roda a comparação em março e grava ``modelos/ia_contra_modelo.json``."""
    carregar_env()
    base = pd.read_parquet(CAMINHO_PREPARADO)
    configurar_base(base)
    agente = AgenteSentinela(base=base)
    registros = []
    for linha in montar_amostra(base).to_dict(orient="records"):
        registros.append(medir_transacao(agente, linha, auditar))
        if registros[-1]["fonte"] == "watsonx":
            time.sleep(PAUSA_ENTRE_AUDITORIAS_S)
    resumo = resumir(registros)
    CAMINHO_IA_CONTRA_MODELO.write_text(
        json.dumps(resumo, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        f"Transações: {resumo['transacoes']} ({resumo['fraudes']} fraudes); "
        f"fontes: {resumo['fontes']}"
    )
    print(f"Latência do modelo: {resumo['latencia_modelo']}; da IA: {resumo['latencia_ia']}")
    print(f"Pareceres: {resumo['pareceres']}; concordância: {resumo['concordancia_por_decisao']}")
    print(f"Modelo: {resumo['modelo']}; IA sozinha: {resumo['ia_sozinha']}")


if __name__ == "__main__":
    main()
