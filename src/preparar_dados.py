"""Prepara os dados brutos e salva em data/transacoes_preparadas.parquet.

Uso: python -m src.preparar_dados
"""

import math

import pandas as pd

from src.config import CAMINHO_CSV, CAMINHO_PREPARADO

# Colunas a carregar do CSV original (seção 4)
COLUNAS_ORIGINAIS = [
    "event_occurred_at",
    "card_id",
    "customer_id",
    "acceptor_id",
    "amount",
    "tipo_transacao",
    "modalidade_transacao",
    "device_ip_country_code",
    "cp_card_term_vel_1h",
    "cardid_count_1m",
    "digitalwallettoken_count_3m",
    "cp_card_prev_term_dist_1h",
    "acceptor_risk",
    "mcc",
    "decision",
    "feedback_label",
]


def preparar() -> pd.DataFrame:
    """Lê o CSV com usecols, gera as 21 colunas e salva o parquet."""

    print("Lendo CSV (apenas 16 colunas)...")
    df_raw = pd.read_csv(
        CAMINHO_CSV,
        usecols=COLUNAS_ORIGINAIS,
        encoding="utf-8",
    )
    print(f"  Linhas lidas: {len(df_raw):,}")

    # --- Montagem das 21 colunas na ordem exata da seção 6 ---

    df = pd.DataFrame()

    # id_transacao: número da linha no CSV original, começando em 0
    df["id_transacao"] = df_raw.index.astype("int64")

    # data_hora: datetime64
    df["data_hora"] = pd.to_datetime(df_raw["event_occurred_at"], errors="coerce")

    # identificadores (texto)
    df["id_cartao"] = df_raw["card_id"].astype(str).where(df_raw["card_id"].notna(), other=None)
    df["id_cliente"] = df_raw["customer_id"].astype(str).where(df_raw["customer_id"].notna(), other=None)
    df["id_estabelecimento"] = df_raw["acceptor_id"].astype(str).where(df_raw["acceptor_id"].notna(), other=None)

    # valor: float64
    df["valor"] = df_raw["amount"].astype("float64")

    # categorias de transação (texto, sem acento)
    df["tipo_transacao"] = df_raw["tipo_transacao"]
    df["modalidade_transacao"] = df_raw["modalidade_transacao"]

    # hora: float64 (vazio se data_hora for vazia)
    df["hora"] = df["data_hora"].dt.hour.astype("float64")

    # madrugada: int64 — 1 se hora < 5; senão 0 (0 quando hora é vazia)
    df["madrugada"] = (df["hora"].notna() & (df["hora"] < 5)).astype("int64")

    # credito: int64
    df["credito"] = (df_raw["tipo_transacao"] == "credito").astype("int64")

    # nao_presente: int64
    df["nao_presente"] = (df_raw["modalidade_transacao"] == "cartao_nao_presente").astype("int64")

    # ip_pais_desconhecido: int64
    df["ip_pais_desconhecido"] = (df_raw["device_ip_country_code"] == "ZZ").astype("int64")

    # colunas de velocidade / distância / risco: float64 (mantém NaN)
    df["vel_cartao_terminal_1h"] = df_raw["cp_card_term_vel_1h"].astype("float64")
    df["qtd_transacoes_cartao_1min"] = df_raw["cardid_count_1m"].astype("float64")
    df["qtd_token_carteira_3m"] = df_raw["digitalwallettoken_count_3m"].astype("float64")
    df["dist_terminal_anterior_km"] = df_raw["cp_card_prev_term_dist_1h"].astype("float64")
    df["risco_estabelecimento"] = df_raw["acceptor_risk"].astype("float64")
    df["mcc"] = df_raw["mcc"].astype("float64")

    # decisao_sistema_atual: texto (manter vazio como vazio)
    df["decisao_sistema_atual"] = df_raw["decision"]

    # fraude: int64 — rótulo (feedback_label)
    df["fraude"] = df_raw["feedback_label"].fillna(False).astype(bool).astype("int64")

    # --- Salvar ---
    print(f"Salvando parquet em {CAMINHO_PREPARADO} ...")
    CAMINHO_PREPARADO.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(CAMINHO_PREPARADO, index=False)
    print("Parquet salvo.")

    return df


def imprimir_resumo(df: pd.DataFrame) -> None:
    """Imprime o resumo pedido na seção 6."""

    print("\n" + "=" * 60)
    print("RESUMO DOS DADOS PREPARADOS")
    print("=" * 60)

    total_linhas = len(df)
    total_fraudes = int(df["fraude"].sum())
    print(f"Total de linhas        : {total_linhas:,}")
    print(f"Total de fraudes       : {total_fraudes:,}  ({total_fraudes / total_linhas * 100:.2f}%)")

    print("\nFraudes por mês:")
    fraudes = df[df["fraude"] == 1].copy()
    fraudes["mes"] = fraudes["data_hora"].dt.to_period("M")
    por_mes = fraudes.groupby("mes").size()
    for mes, qtd in por_mes.items():
        print(f"  {mes}: {qtd:,}")

    print("\nContagem por tipo_transacao:")
    for tipo, qtd in df["tipo_transacao"].value_counts().items():
        print(f"  {tipo}: {qtd:,}")

    print("\nPercentual de vazios por coluna:")
    for col in df.columns:
        n_vazios = df[col].isna().sum()
        pct = n_vazios / total_linhas * 100
        if pct > 0:
            print(f"  {col}: {pct:.2f}%")

    n_ip_desconhecido = int((df["ip_pais_desconhecido"] == 1).sum())
    n_ip_desc_fraude = int(df.loc[df["ip_pais_desconhecido"] == 1, "fraude"].sum())
    print(f"\nip_pais_desconhecido == 1 : {n_ip_desconhecido:,}")
    print(f"  Dessas que são fraude   : {n_ip_desc_fraude:,}")

    print("\nColunas no parquet:")
    print(f"  {list(df.columns)}")
    print(f"  Total: {len(df.columns)} colunas")
    print("=" * 60)


if __name__ == "__main__":
    df = preparar()
    imprimir_resumo(df)
