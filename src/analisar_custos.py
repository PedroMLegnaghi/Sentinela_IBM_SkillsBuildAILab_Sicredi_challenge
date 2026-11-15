"""Análise de custo-benefício da prevenção a fraudes.

Calcula o valor das fraudes bloqueadas e não bloqueadas pelo Sentinela, o custo dos pedidos de
confirmação, o valor líquido protegido e a curva de custo por nota de corte (0 a 100, de 5 em 5).

Não compara com a coluna ``decision`` da base: o dicionário da Sicredi não a documenta como a
decisão de um sistema real (e ela nunca recusa compra legítima).

Uso: python -m src.analisar_custos
"""

import json
import logging

import pandas as pd

from src.agente import AgenteSentinela
from src.config import (
    CAMINHO_CUSTOS,
    CAMINHO_PREPARADO,
    CUSTO_PEDIDO_CONFIRMACAO,
    FIM_TESTE,
    INICIO_TESTE,
)

logger = logging.getLogger(__name__)


def calcular_custos(teste: pd.DataFrame, custo_confirmacao: float) -> dict:
    """Calcula as métricas de custo do Sentinela em março.

    Valor vazio em ``valor`` conta como 0 e o índice entra em ``valores_vazios``.
    A curva de custo varre notas de corte de 0 a 100 de 5 em 5 e usa só a nota do modelo:
    em cada corte, toda compra com ``nota >= corte`` conta como um alerta (``confirmacoes``).
    Ela não inclui os sinais de regra, que também levam o Sentinela a pedir confirmação; por
    isso, no corte 30, a curva mostra menos alertas que o total de confirmações do Sentinela.

    Args:
        teste: DataFrame de março com colunas ``nota``, ``decisao``, ``valor`` e ``fraude``.
        custo_confirmacao: Custo unitário de um pedido de confirmação, em reais.

    Returns:
        Dicionário com sentinela, valor_liquido_protegido e curva_custo.
    """
    df = teste.copy()
    # Contagem de valores vazios em 'valor'
    valores_vazios = int(df["valor"].isna().sum())
    df["valor"] = df["valor"].fillna(0.0)

    # --- Sentinela ---
    bloqueadas_mask = df["decisao"] == "BLOQUEAR"
    confirmacao_mask = df["decisao"] == "PEDIR_CONFIRMACAO"

    fraudes_bloqueadas_val = float(df.loc[bloqueadas_mask & (df["fraude"] == 1), "valor"].sum())
    fraudes_nao_bloqueadas_val = float(
        df.loc[(~bloqueadas_mask) & (df["fraude"] == 1), "valor"].sum()
    )
    n_confirmacoes = int(confirmacao_mask.sum())
    custo_confirmacoes = round(n_confirmacoes * custo_confirmacao, 2)

    sentinela = {
        "fraudes_bloqueadas": int((bloqueadas_mask & (df["fraude"] == 1)).sum()),
        "valor_fraudes_bloqueadas": round(fraudes_bloqueadas_val, 2),
        "fraudes_nao_bloqueadas": int((~bloqueadas_mask & (df["fraude"] == 1)).sum()),
        "valor_fraudes_nao_bloqueadas": round(fraudes_nao_bloqueadas_val, 2),
        "confirmacoes": n_confirmacoes,
        "custo_confirmacoes": custo_confirmacoes,
        "valores_vazios": valores_vazios,
    }

    # Valor das fraudes barradas menos o custo de incomodar o associado com as confirmações
    valor_liquido = round(fraudes_bloqueadas_val - custo_confirmacoes, 2)

    # --- Curva de custo por nota de corte (0 a 100, de 5 em 5) ---
    curva = []
    notas = list(range(0, 105, 5))
    for corte in notas:
        alerta_mask = df["nota"] >= corte
        fraudes_cap = float(df.loc[alerta_mask & (df["fraude"] == 1), "valor"].sum())
        fraudes_perd = float(df.loc[(~alerta_mask) & (df["fraude"] == 1), "valor"].sum())
        n_conf = int(alerta_mask.sum())
        custo_conf = round(n_conf * custo_confirmacao, 2)
        curva.append(
            {
                "corte": corte,
                "fraudes_capturadas": int((alerta_mask & (df["fraude"] == 1)).sum()),
                "valor_fraudes_capturadas": round(fraudes_cap, 2),
                "fraudes_perdidas": int((~alerta_mask & (df["fraude"] == 1)).sum()),
                "valor_fraudes_perdidas": round(fraudes_perd, 2),
                "confirmacoes": n_conf,
                "custo_confirmacoes": custo_conf,
            }
        )

    return {
        "custo_confirmacao_unitario": custo_confirmacao,
        "sentinela": sentinela,
        "valor_liquido_protegido": valor_liquido,
        "curva_custo": curva,
    }


def main() -> None:
    """Ponto de entrada: lê o parquet, roda o agente em março e grava custos.json."""
    print("Carregando dados preparados...")
    df = pd.read_parquet(CAMINHO_PREPARADO)

    teste_bruto = df[(df["data_hora"] >= INICIO_TESTE) & (df["data_hora"] < FIM_TESTE)].copy()
    print(f"  Transações em março: {len(teste_bruto):,}")

    print("Carregando agente e pontuando transações de março...")
    agente = AgenteSentinela(base=df)
    teste = agente.analisar_lote(teste_bruto)

    print("Calculando análise de custos...")
    resultado = calcular_custos(teste, CUSTO_PEDIDO_CONFIRMACAO)

    CAMINHO_CUSTOS.parent.mkdir(parents=True, exist_ok=True)
    with CAMINHO_CUSTOS.open("w", encoding="utf-8") as arq:
        json.dump(resultado, arq, indent=2, ensure_ascii=False)
    print(f"Análise de custos salva em {CAMINHO_CUSTOS}")

    s = resultado["sentinela"]
    print("\n" + "=" * 60)
    print("ANÁLISE DE CUSTOS — março 2025")
    print("=" * 60)
    print(f"  Sentinela — fraudes bloqueadas   : {s['fraudes_bloqueadas']}")
    print(f"  Sentinela — valor bloqueado       : R$ {s['valor_fraudes_bloqueadas']:,.2f}")
    print(f"  Sentinela — fraudes não bloqueadas: {s['fraudes_nao_bloqueadas']}")
    print(f"  Sentinela — custo confirmações    : R$ {s['custo_confirmacoes']:,.2f}")
    print(f"  Valor líquido protegido           : R$ {resultado['valor_liquido_protegido']:,.2f}")
    print("=" * 60)


if __name__ == "__main__":
    main()
