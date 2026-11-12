"""Treina o modelo de detecção de fraudes e salva em modelos/sentinela.joblib.

Uso: python -m src.treinar_modelo
"""

import json

import joblib
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.config import (
    CAMINHO_METRICAS,
    CAMINHO_MODELO,
    CAMINHO_PREPARADO,
    FIM_TESTE,
    INICIO_TESTE,
    INICIO_TREINO,
    SEMENTE,
    VARIAVEIS_MODELO,
)


def carregar_divisao():
    """Carrega o parquet e faz a divisão temporal treino/teste."""
    print("Carregando dados preparados...")
    df = pd.read_parquet(CAMINHO_PREPARADO)

    df = df[df["data_hora"].notna()].copy()

    treino = df[(df["data_hora"] >= INICIO_TREINO) & (df["data_hora"] < INICIO_TESTE)].copy()
    teste = df[(df["data_hora"] >= INICIO_TESTE) & (df["data_hora"] < FIM_TESTE)].copy()

    print(f"  Treino : {len(treino):,} linhas, {int(treino['fraude'].sum()):,} fraudes")
    print(f"  Teste  : {len(teste):,} linhas, {int(teste['fraude'].sum()):,} fraudes")

    return treino, teste


def treinar_avaliar():
    """Treina os modelos, salva o pipeline e as métricas."""
    treino, teste = carregar_divisao()

    entradas_treino = treino[VARIAVEIS_MODELO]
    y_treino = treino["fraude"]
    entradas_teste = teste[VARIAVEIS_MODELO]
    y_teste = teste["fraude"]

    print("\nTreinando Regressão Logística...")
    pipeline_rl = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median", add_indicator=True)),
            ("scaler", StandardScaler()),
            (
                "modelo",
                LogisticRegression(
                    class_weight="balanced",
                    max_iter=2000,
                    random_state=SEMENTE,
                ),
            ),
        ]
    )
    pipeline_rl.fit(entradas_treino, y_treino)

    proba_rl = pipeline_rl.predict_proba(entradas_teste)[:, 1]
    pr_auc_rl = float(average_precision_score(y_teste, proba_rl))
    roc_auc_rl = float(roc_auc_score(y_teste, proba_rl))
    nota_rl = proba_rl * 100

    print("Treinando HistGradientBoostingClassifier (comparação)...")
    hgb = HistGradientBoostingClassifier(
        class_weight="balanced",
        max_iter=200,
        learning_rate=0.05,
        random_state=SEMENTE,
    )
    hgb.fit(entradas_treino, y_treino)
    proba_hgb = hgb.predict_proba(entradas_teste)[:, 1]
    pr_auc_hgb = float(average_precision_score(y_teste, proba_hgb))
    roc_auc_hgb = float(roc_auc_score(y_teste, proba_hgb))

    limiares = []
    for corte in [30, 50, 70, 90]:
        alertas_mask = nota_rl >= corte
        alertas = int(alertas_mask.sum())
        fraudes_detectadas = int(y_teste[alertas_mask].sum())
        precisao = fraudes_detectadas / alertas if alertas > 0 else 0.0
        recall = fraudes_detectadas / int(y_teste.sum()) if int(y_teste.sum()) > 0 else 0.0
        limiares.append(
            {
                "limiar": corte,
                "alertas": alertas,
                "fraudes_detectadas": fraudes_detectadas,
                "precisao": round(precisao, 4),
                "recall": round(recall, 4),
            }
        )

    bloqueadas_atual = int((teste["decisao_sistema_atual"] == "deny").sum())
    fraudes_bloqueadas_atual = int(
        teste.loc[teste["decisao_sistema_atual"] == "deny", "fraude"].sum()
    )
    fraudes_total = int(y_teste.sum())

    CAMINHO_MODELO.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline_rl, CAMINHO_MODELO)
    print(f"\nModelo salvo em {CAMINHO_MODELO}")

    metricas = {
        "modelo": "regressao_logistica",
        "treino": {"linhas": len(treino), "fraudes": int(y_treino.sum())},
        "teste": {"linhas": len(teste), "fraudes": fraudes_total},
        "pr_auc": round(pr_auc_rl, 4),
        "roc_auc": round(roc_auc_rl, 4),
        "limiares": limiares,
        "comparacao_hgb": {
            "pr_auc": round(pr_auc_hgb, 4),
            "roc_auc": round(roc_auc_hgb, 4),
        },
        "sistema_atual": {
            "bloqueadas": bloqueadas_atual,
            "fraudes_bloqueadas": fraudes_bloqueadas_atual,
            "fraudes_total": fraudes_total,
        },
    }

    with CAMINHO_METRICAS.open("w", encoding="utf-8") as f:
        json.dump(metricas, f, indent=2, ensure_ascii=False)
    print(f"Métricas salvas em {CAMINHO_METRICAS}")

    _imprimir_metricas(metricas, pipeline_rl)

    return metricas


def _imprimir_metricas(metricas: dict, pipeline_rl: Pipeline) -> None:
    """Imprime as métricas e os coeficientes na tela."""
    print("\n" + "=" * 60)
    print("MÉTRICAS — REGRESSÃO LOGÍSTICA")
    print("=" * 60)
    treino = metricas["treino"]
    teste = metricas["teste"]
    print(f"Treino : {treino['linhas']:,} linhas, {treino['fraudes']:,} fraudes")
    print(f"Teste  : {teste['linhas']:,} linhas, {teste['fraudes']:,} fraudes")
    print(f"PR-AUC : {metricas['pr_auc']:.4f}")
    print(f"ROC-AUC: {metricas['roc_auc']:.4f}")

    print("\nLimiares de corte:")
    print(f"  {'Corte':>5}  {'Alertas':>8}  {'Fraudes':>8}  {'Precisão':>9}  {'Recall':>8}")
    for lim in metricas["limiares"]:
        print(
            f"  {lim['limiar']:>5}  {lim['alertas']:>8,}  "
            f"{lim['fraudes_detectadas']:>8,}  {lim['precisao']:>9.4f}  {lim['recall']:>8.4f}"
        )

    print("\nComparação com HGB:")
    print(f"  PR-AUC  HGB: {metricas['comparacao_hgb']['pr_auc']:.4f}")
    print(f"  ROC-AUC HGB: {metricas['comparacao_hgb']['roc_auc']:.4f}")

    sa = metricas["sistema_atual"]
    pct_atual = (
        sa["fraudes_bloqueadas"] / sa["fraudes_total"] * 100 if sa["fraudes_total"] > 0 else 0
    )
    print("\nSistema atual (março):")
    print(f"  Bloqueadas       : {sa['bloqueadas']:,}")
    print(
        f"  Fraudes bloqueadas: {sa['fraudes_bloqueadas']:,} /"
        f" {sa['fraudes_total']:,} ({pct_atual:.1f}%)"
    )

    modelo_lr = pipeline_rl.named_steps["modelo"]
    imputer = pipeline_rl.named_steps["imputer"]
    nomes = list(VARIAVEIS_MODELO) + [
        f"faltante_{VARIAVEIS_MODELO[i]}" for i in imputer.indicator_.features_
    ]
    coefs = modelo_lr.coef_[0]

    pares = sorted(zip(nomes, coefs, strict=False), key=lambda x: abs(x[1]), reverse=True)
    print("\nCoeficientes da regressão logística (por |coef|):")
    for nome, coef in pares:
        print(f"  {nome:<35} {coef:+.4f}")
    print("=" * 60)


if __name__ == "__main__":
    treinar_avaliar()
