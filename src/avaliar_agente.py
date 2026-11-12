"""Avalia o agente Sentinela no conjunto de teste (março de 2025).

Uso: python -m src.avaliar_agente
"""

import json

import pandas as pd

from src.agente import AgenteSentinela
from src.config import CAMINHO_AVALIACAO, CAMINHO_PREPARADO, FIM_TESTE, INICIO_TESTE


def avaliar():
    """Roda analisar_lote no teste de março e salva avaliacao_agente.json."""
    print("Carregando dados preparados...")
    df = pd.read_parquet(CAMINHO_PREPARADO)

    teste = df[(df["data_hora"] >= INICIO_TESTE) & (df["data_hora"] < FIM_TESTE)].copy()
    print(f"  Transações em março: {len(teste):,}")

    print("Carregando agente...")
    agente = AgenteSentinela(base=df)

    print("Rodando analisar_lote...")
    resultado = agente.analisar_lote(teste)

    # Métricas do Sentinela
    bloqueadas = int((resultado["decisao"] == "BLOQUEAR").sum())
    fraudes_bloqueadas = int(resultado.loc[resultado["decisao"] == "BLOQUEAR", "fraude"].sum())
    confirmacoes = int((resultado["decisao"] == "PEDIR_CONFIRMACAO").sum())
    fraudes_em_confirmacao = int(
        resultado.loc[resultado["decisao"] == "PEDIR_CONFIRMACAO", "fraude"].sum()
    )
    aprovadas = int((resultado["decisao"] == "APROVAR").sum())
    fraudes_aprovadas = int(resultado.loc[resultado["decisao"] == "APROVAR", "fraude"].sum())

    fraudes_total = int(teste["fraude"].sum())
    transacoes = len(teste)

    # Métricas do sistema atual
    bloqueadas_atual = int((teste["decisao_sistema_atual"] == "deny").sum())
    fraudes_bloqueadas_atual = int(
        teste.loc[teste["decisao_sistema_atual"] == "deny", "fraude"].sum()
    )
    fraudes_nao_bloqueadas_atual = fraudes_total - fraudes_bloqueadas_atual

    avaliacao = {
        "periodo": "2025-03",
        "transacoes": transacoes,
        "fraudes_total": fraudes_total,
        "sentinela": {
            "bloqueadas": bloqueadas,
            "fraudes_bloqueadas": fraudes_bloqueadas,
            "confirmacoes": confirmacoes,
            "fraudes_em_confirmacao": fraudes_em_confirmacao,
            "aprovadas": aprovadas,
            "fraudes_aprovadas": fraudes_aprovadas,
        },
        "sistema_atual": {
            "bloqueadas": bloqueadas_atual,
            "fraudes_bloqueadas": fraudes_bloqueadas_atual,
            "fraudes_nao_bloqueadas": fraudes_nao_bloqueadas_atual,
        },
    }

    CAMINHO_AVALIACAO.parent.mkdir(parents=True, exist_ok=True)
    with CAMINHO_AVALIACAO.open("w", encoding="utf-8") as f:
        json.dump(avaliacao, f, indent=2, ensure_ascii=False)
    print(f"Avaliação salva em {CAMINHO_AVALIACAO}")

    _imprimir_avaliacao(avaliacao)
    return avaliacao


def _imprimir_avaliacao(av: dict) -> None:
    """Imprime o resumo da avaliação na tela."""
    print("\n" + "=" * 60)
    print(f"AVALIAÇÃO DO AGENTE — {av['periodo']}")
    print("=" * 60)
    print(f"Transações no período : {av['transacoes']:,}")
    print(f"Fraudes totais        : {av['fraudes_total']:,}")

    s = av["sentinela"]
    ft = av["fraudes_total"]
    pct_bloq = s["fraudes_bloqueadas"] / ft * 100 if ft > 0 else 0
    pct_aprov = s["fraudes_aprovadas"] / ft * 100 if ft > 0 else 0
    pct_conf_tx = s["confirmacoes"] / av["transacoes"] * 100 if av["transacoes"] > 0 else 0

    print("\nSentinela:")
    print(f"  Bloqueadas           : {s['bloqueadas']:,}")
    print(f"  Fraudes bloqueadas   : {s['fraudes_bloqueadas']:,} ({pct_bloq:.1f}% das fraudes)")
    print(f"  Confirmações         : {s['confirmacoes']:,} ({pct_conf_tx:.2f}% das transações)")
    print(f"  Fraudes em confirmação: {s['fraudes_em_confirmacao']:,}")
    print(f"  Aprovadas            : {s['aprovadas']:,}")
    print(f"  Fraudes aprovadas    : {s['fraudes_aprovadas']:,} ({pct_aprov:.1f}% das fraudes)")

    sa = av["sistema_atual"]
    pct_bloq_atual = sa["fraudes_bloqueadas"] / ft * 100 if ft > 0 else 0
    print("\nSistema atual:")
    print(f"  Bloqueadas           : {sa['bloqueadas']:,}")
    print(
        f"  Fraudes bloqueadas   : {sa['fraudes_bloqueadas']:,} ({pct_bloq_atual:.1f}% das fraudes)"
    )
    print(f"  Fraudes não bloqueadas: {sa['fraudes_nao_bloqueadas']:,}")
    print("=" * 60)


if __name__ == "__main__":
    avaliar()
