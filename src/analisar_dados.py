"""Análise exploratória dos dados do projeto Sentinela.

Lê o parquet, calcula estatísticas resumidas e grava ``modelos/eda.json``.
Também produz o documento ``docs/analise-exploratoria.md``.

Uso: python -m src.analisar_dados
"""

import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd

from src.config import CAMINHO_EDA, CAMINHO_PREPARADO, VARIAVEIS_MODELO

logger = logging.getLogger(__name__)

CAMINHO_DOC = Path(__file__).resolve().parent.parent / "docs" / "analise-exploratoria.md"

# Colunas proibidas da ESPECIFICACAO, seção 5, e motivo de cada uma
COLUNAS_PROIBIDAS = [
    {
        "coluna": "fraud",
        "motivo": "Rótulo incorreto: está errado em quase todas as linhas; "
        "o rótulo correto é feedback_label.",
    },
    {
        "coluna": "fraud_score",
        "motivo": "Score de fraude calculado pelo sistema externo após a decisão; "
        "vazamento direto do alvo.",
    },
    {
        "coluna": "visa_fraud_score",
        "motivo": "Score de fraude da Visa; disponível apenas após a transação ser processada.",
    },
    {
        "coluna": "mc_fraud_score",
        "motivo": "Score de fraude da Mastercard; disponível apenas após o processamento.",
    },
    {
        "coluna": "decision",
        "motivo": "Decisão do sistema atual (approve/deny); só é carregada para comparação, "
        "nunca como entrada do modelo.",
    },
    {
        "coluna": "transaction_status",
        "motivo": "Status final da transação; determinado depois da decisão.",
    },
    {
        "coluna": "action_code",
        "motivo": "Código de ação do sistema; resultado da decisão, não entrada.",
    },
    {
        "coluna": "reason_code",
        "motivo": "Código de motivo; resultado da decisão, não entrada.",
    },
    {
        "coluna": "alert_id",
        "motivo": "Identificador do alerta gerado pelo sistema antifraude; pós-decisão.",
    },
    {
        "coluna": "dispute_*",
        "motivo": "Colunas de disputa (prefixo dispute_); existem somente após contestação, "
        "posterior à decisão.",
    },
    {
        "coluna": "fdz_*",
        "motivo": "Colunas do sistema FDZ (prefixo fdz_); scores e marcadores pós-decisão.",
    },
    {
        "coluna": "oob_*",
        "motivo": "Colunas out-of-band (prefixo oob_); dados coletados após a autorização.",
    },
]

# Definições dos sinais: (id, coluna, operador, limiar)
# coluna None e operador "composto" indicam sinal derivado de duas colunas.
_DEFINICOES_SINAIS = [
    ("velocidade_terminal", "vel_cartao_terminal_1h", ">=", 10),
    ("rajada_1min", "qtd_transacoes_cartao_1min", ">=", 5),
    ("token_carteira", "qtd_token_carteira_3m", ">=", 30),
    ("salto_geografico", "dist_terminal_anterior_km", ">", 100),
    ("madrugada", "madrugada", "==", 1),
    ("valor_alto", "valor", ">", 150),
    ("credito_nao_presente", None, "composto", None),
    ("ip_desconhecido", "ip_pais_desconhecido", "==", 1),
    ("estabelecimento_risco", "risco_estabelecimento", ">=", 40),
]


def _stats_serie(serie: pd.Series) -> dict:
    """Calcula mediana, percentil 10 e percentil 90 de uma série numérica.

    Args:
        serie: Série pandas sem valores NaN.

    Returns:
        Dicionário com as chaves ``mediana``, ``p10`` e ``p90``.
        Retorna ``None`` para todos os valores se a série estiver vazia.
    """
    if len(serie) == 0:
        return {"mediana": None, "p10": None, "p90": None}
    return {
        "mediana": round(float(np.median(serie)), 6),
        "p10": round(float(np.percentile(serie, 10)), 6),
        "p90": round(float(np.percentile(serie, 90)), 6),
    }


def _agregar_por_categoria(df: pd.DataFrame, coluna: str) -> list[dict]:
    """Conta linhas e fraudes agrupando por uma coluna categórica.

    Args:
        df: DataFrame com a coluna ``coluna`` e a coluna ``fraude``.
        coluna: Nome da coluna para agrupar.

    Returns:
        Lista de dicionários com ``coluna``, ``linhas``, ``fraudes`` e
        ``percentual_fraude``.
    """
    grupo = df.groupby(coluna)["fraude"].agg(linhas="count", fraudes="sum").reset_index()
    grupo["percentual_fraude"] = (grupo["fraudes"] / grupo["linhas"] * 100).round(4)
    registros = grupo.to_dict(orient="records")
    for r in registros:
        r["linhas"] = int(r["linhas"])
        r["fraudes"] = int(r["fraudes"])
    return registros


def _calcular_variaveis(df: pd.DataFrame) -> list[dict]:
    """Calcula percentis e % de vazios para cada variável do modelo.

    Args:
        df: DataFrame com as colunas de ``VARIAVEIS_MODELO`` e ``fraude``.

    Returns:
        Lista de dicionários com estatísticas por variável.
    """
    fraudes_mask = df["fraude"] == 1
    legitimas_mask = df["fraude"] == 0
    resultado: list[dict] = []
    for var in VARIAVEIS_MODELO:
        if var not in df.columns:
            continue
        col = df[var]
        pct_vazios = round(col.isna().mean() * 100, 4)
        resultado.append(
            {
                "variavel": var,
                "pct_vazios": pct_vazios,
                "fraudes": _stats_serie(df.loc[fraudes_mask, var].dropna()),
                "legitimas": _stats_serie(df.loc[legitimas_mask, var].dropna()),
            }
        )
    return resultado


def _mask_sinal(
    df: pd.DataFrame, id_sinal: str, coluna: str | None, op: str, limiar: object
) -> pd.Series:
    """Constrói a máscara booleana para um sinal de alerta.

    Args:
        df: DataFrame de transações.
        id_sinal: Identificador do sinal (ex.: ``"credito_nao_presente"``).
        coluna: Coluna a comparar ou ``None`` para sinal composto.
        op: Operador de comparação (``">="``, ``">"``, ``"=="`` ou ``"composto"``).
        limiar: Valor de corte.

    Returns:
        Série booleana com ``True`` onde o sinal dispara.
    """
    if id_sinal == "credito_nao_presente":
        return (df["credito"] == 1) & (df["nao_presente"] == 1)
    if op == ">=":
        return df[coluna].notna() & (df[coluna] >= limiar)
    if op == ">":
        return df[coluna].notna() & (df[coluna] > limiar)
    return df[coluna] == limiar


def _calcular_sinais(df: pd.DataFrame) -> list[dict]:
    """Calcula a cobertura de cada sinal de alerta em fraudes e legítimas.

    Args:
        df: DataFrame com as colunas necessárias para os sinais.

    Returns:
        Lista com ``sinal``, ``pct_fraudes_com_sinal`` e
        ``pct_legitimas_com_sinal`` para cada sinal.
    """
    fraudes_mask = df["fraude"] == 1
    legitimas_mask = df["fraude"] == 0
    total_fraudes = int(df["fraude"].sum())
    total_legitimas = int((df["fraude"] == 0).sum())
    resultado: list[dict] = []
    for id_sinal, coluna, op, limiar in _DEFINICOES_SINAIS:
        mask = _mask_sinal(df, id_sinal, coluna, op, limiar)
        pct_fraude = (
            round(df.loc[fraudes_mask & mask].shape[0] / total_fraudes * 100, 4)
            if total_fraudes > 0
            else 0.0
        )
        pct_legitima = (
            round(df.loc[legitimas_mask & mask].shape[0] / total_legitimas * 100, 4)
            if total_legitimas > 0
            else 0.0
        )
        resultado.append(
            {
                "sinal": id_sinal,
                "pct_fraudes_com_sinal": pct_fraude,
                "pct_legitimas_com_sinal": pct_legitima,
            }
        )
    return resultado


def _calcular_por_hora(df: pd.DataFrame) -> list[dict]:
    """Conta transações fraudulentas e legítimas para cada hora do dia.

    Args:
        df: DataFrame com as colunas ``hora`` e ``fraude``.

    Returns:
        Lista de 24 dicionários com ``hora``, ``fraudes`` e ``legitimas``.
    """
    fraudes_mask = df["fraude"] == 1
    legitimas_mask = df["fraude"] == 0
    por_hora: list[dict] = []
    for h in range(24):
        mask_h = df["hora"] == h
        por_hora.append(
            {
                "hora": h,
                "fraudes": int(df.loc[fraudes_mask & mask_h, "fraude"].count()),
                "legitimas": int(df.loc[legitimas_mask & mask_h, "fraude"].count()),
            }
        )
    return por_hora


def calcular_eda(df: pd.DataFrame) -> dict:
    """Calcula as estatísticas exploratórias a partir do DataFrame preparado.

    Args:
        df: DataFrame com as colunas do parquet de transações preparadas.

    Returns:
        Dicionário com todas as estatísticas para gravação em ``eda.json``.
    """
    total_linhas = len(df)
    total_fraudes = int(df["fraude"].sum())

    df_com_data = df.dropna(subset=["data_hora"]).copy()
    df_com_data["mes"] = df_com_data["data_hora"].dt.to_period("M").astype(str)
    por_mes = df_com_data.groupby("mes")["fraude"].agg(linhas="count", fraudes="sum").reset_index()
    por_mes["percentual_fraude"] = (por_mes["fraudes"] / por_mes["linhas"] * 100).round(4)
    por_mes_lista = por_mes.to_dict(orient="records")
    for r in por_mes_lista:
        r["linhas"] = int(r["linhas"])
        r["fraudes"] = int(r["fraudes"])

    return {
        "total_linhas": total_linhas,
        "total_fraudes": total_fraudes,
        "percentual_fraude": (
            round(total_fraudes / total_linhas * 100, 4) if total_linhas > 0 else 0.0
        ),
        "por_mes": por_mes_lista,
        "por_tipo": _agregar_por_categoria(df, "tipo_transacao"),
        "por_modalidade": _agregar_por_categoria(df, "modalidade_transacao"),
        "variaveis": _calcular_variaveis(df),
        "sinais": _calcular_sinais(df),
        "por_hora": _calcular_por_hora(df),
        "auditoria_vazamento": COLUNAS_PROIBIDAS,
    }


def _doc_secao_variaveis(eda: dict, linhas: list[str]) -> None:
    """Acrescenta a seção de estatísticas por variável ao documento.

    Args:
        eda: Dicionário com a chave ``variaveis``.
        linhas: Lista de strings em construção (modificada no lugar).
    """
    linhas += [
        "## Estatísticas por variável do modelo",
        "",
        "| Variável | % Vazios | Mediana (fraude) | P10 (fraude) | P90 (fraude) "
        "| Mediana (legítima) | P10 (legítima) | P90 (legítima) |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for v in eda["variaveis"]:
        fr = v["fraudes"]
        le = v["legitimas"]
        linhas.append(
            f"| {v['variavel']} | {v['pct_vazios']:.1f}% "
            f"| {fr['mediana']} | {fr['p10']} | {fr['p90']} "
            f"| {le['mediana']} | {le['p10']} | {le['p90']} |"
        )
    linhas += [
        "",
        "As variáveis de velocidade (`vel_cartao_terminal_1h`, `qtd_transacoes_cartao_1min`, "
        "`qtd_token_carteira_3m`) têm cerca de 8% de valores ausentes; "
        "o `SimpleImputer` do pipeline preenche com a mediana e adiciona um indicador de vazio. "
        "Fraudes apresentam medianas muito maiores que legítimas nessas variáveis, "
        "confirmando o poder discriminativo.",
        "",
    ]


def _doc_secao_sinais(eda: dict, linhas: list[str]) -> None:
    """Acrescenta a seção de cobertura dos sinais ao documento.

    Args:
        eda: Dicionário com a chave ``sinais``.
        linhas: Lista de strings em construção (modificada no lugar).
    """
    linhas += [
        "## Cobertura dos sinais de alerta",
        "",
        "| Sinal | % Fraudes com sinal | % Legítimas com sinal |",
        "| --- | --- | --- |",
    ]
    for s in eda["sinais"]:
        linhas.append(
            f"| {s['sinal']} | {s['pct_fraudes_com_sinal']:.1f}% "
            f"| {s['pct_legitimas_com_sinal']:.1f}% |"
        )
    linhas += [
        "",
        "Sinais como `salto_geografico`, `rajada_1min` e `velocidade_terminal` "
        "são quase exclusivos de fraudes. "
        "`valor_alto` e `madrugada` aparecem em parte das legítimas, "
        "mas com proporção bem maior nas fraudes. "
        "A combinação de 3 ou mais sinais é o critério de `PEDIR_CONFIRMACAO`.",
        "",
    ]


def _gerar_documento(eda: dict) -> str:
    """Gera o texto do documento de análise exploratória em Markdown.

    Args:
        eda: Dicionário retornado por :func:`calcular_eda`.

    Returns:
        String com o conteúdo completo do documento Markdown.
    """
    linhas: list[str] = [
        "# Análise Exploratória dos Dados — Projeto Sentinela",
        "",
        "Documento gerado automaticamente por `python -m src.analisar_dados`. "
        "Dados 100% sintéticos (Sicredi / IBM SkillsBuild). "
        "Nunca contém identificadores de cartão, cliente ou estabelecimento.",
        "",
        "## Visão geral",
        "",
        f"A base contém **{eda['total_linhas']:,} transações** com "
        f"**{eda['total_fraudes']} fraudes** "
        f"({eda['percentual_fraude']:.2f}% de taxa de fraude). "
        "O rótulo utilizado é `feedback_label` (coluna `fraude` no parquet); "
        "a coluna `fraud` foi descartada por conter erros sistemáticos.",
        "",
        "## Distribuição por mês",
        "",
        "| Mês | Transações | Fraudes | % Fraude |",
        "| --- | --- | --- | --- |",
    ]
    for r in eda["por_mes"]:
        linhas.append(
            f"| {r['mes']} | {r['linhas']:,} | {r['fraudes']} | {r['percentual_fraude']:.2f}% |"
        )
    linhas += [
        "",
        "As fraudes estão concentradas entre janeiro e março de 2025, "
        "período de treino e teste do modelo. "
        "Meses fora desse intervalo têm zero fraudes, o que é esperado nos dados sintéticos. "
        "A taxa de fraude mais alta está em março, o mês de teste.",
        "",
        "## Distribuição por tipo de transação",
        "",
        "| Tipo | Transações | Fraudes | % Fraude |",
        "| --- | --- | --- | --- |",
    ]
    for r in eda["por_tipo"]:
        linhas.append(
            f"| {r['tipo_transacao']} | {r['linhas']:,} | "
            f"{r['fraudes']} | {r['percentual_fraude']:.2f}% |"
        )
    linhas += [
        "",
        "Transações de crédito apresentam taxa de fraude significativamente maior "
        "que as de débito. "
        "Isso justifica o sinal `credito_nao_presente` no modelo. "
        "A maioria das transações legítimas é de débito.",
        "",
        "## Distribuição por modalidade",
        "",
        "| Modalidade | Transações | Fraudes | % Fraude |",
        "| --- | --- | --- | --- |",
    ]
    for r in eda["por_modalidade"]:
        linhas.append(
            f"| {r['modalidade_transacao']} | {r['linhas']:,} | "
            f"{r['fraudes']} | {r['percentual_fraude']:.2f}% |"
        )
    linhas += [
        "",
        "Compras sem cartão presente (online) concentram a maior parte das fraudes. "
        "Combinado com crédito, esse padrão é o sinal mais discriminante. "
        "O modelo captura essa interação com o indicador `nao_presente`.",
        "",
    ]
    _doc_secao_variaveis(eda, linhas)
    _doc_secao_sinais(eda, linhas)
    linhas += [
        "## Volume por hora do dia",
        "",
        "| Hora | Fraudes | Legítimas |",
        "| --- | --- | --- |",
    ]
    for r in eda["por_hora"]:
        linhas.append(f"| {r['hora']:02d}h | {r['fraudes']} | {r['legitimas']:,} |")
    linhas += [
        "",
        "Fraudes se concentram na madrugada (0h–4h), confirmando o sinal `madrugada`. "
        "Legítimas seguem o padrão comercial, com pico entre 9h e 18h. "
        "A divergência entre os dois perfis é clara e consistente.",
        "",
        "## Auditoria de vazamento de informação",
        "",
        "As colunas abaixo foram identificadas como proibidas (ESPECIFICACAO, seção 5) "
        "e nunca são usadas como entrada do modelo nem das regras de alerta.",
        "",
        "| Coluna | Motivo |",
        "| --- | --- |",
    ]
    for c in eda["auditoria_vazamento"]:
        linhas.append(f"| `{c['coluna']}` | {c['motivo']} |")
    linhas += [
        "",
        "O único identificador carregado (`card_id`, `customer_id`, `acceptor_id`) "
        "serve apenas para o cálculo de histórico do agente e nunca é exposto na API "
        "nem enviado ao watsonx.ai.",
        "",
    ]
    return "\n".join(linhas)


def main() -> dict:
    """Carrega o parquet, calcula a EDA, grava o JSON e escreve o documento.

    Returns:
        Dicionário com as estatísticas exploratórias gravadas em ``eda.json``.

    Raises:
        FileNotFoundError: Se o parquet ``CAMINHO_PREPARADO`` não existir.
    """
    print(f"Carregando dados de {CAMINHO_PREPARADO} ...")
    df = pd.read_parquet(CAMINHO_PREPARADO)
    print(f"  {len(df):,} linhas carregadas.")

    print("Calculando estatísticas exploratórias...")
    eda = calcular_eda(df)

    CAMINHO_EDA.parent.mkdir(parents=True, exist_ok=True)
    with CAMINHO_EDA.open("w", encoding="utf-8") as fout:
        json.dump(eda, fout, indent=2, ensure_ascii=False)
    print(f"JSON salvo em {CAMINHO_EDA}")

    documento = _gerar_documento(eda)
    CAMINHO_DOC.parent.mkdir(parents=True, exist_ok=True)
    CAMINHO_DOC.write_text(documento, encoding="utf-8")
    print(f"Documento salvo em {CAMINHO_DOC}")

    print(
        f"\nResumo: {eda['total_linhas']:,} linhas, "
        f"{eda['total_fraudes']} fraudes ({eda['percentual_fraude']:.2f}%)."
    )
    return eda


if __name__ == "__main__":
    main()
