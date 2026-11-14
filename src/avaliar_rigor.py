"""Avaliação rigorosa do modelo Sentinela com janelas temporais e bootstrap.

Calcula PR-AUC, ROC-AUC, recall e precisão em duas janelas temporais, IC 95%
por bootstrap, comparação com baselines (só regras, só modelo, HistGradient-
BoostingClassifier) e ablação de variáveis. Também mede calibração (Brier e
10 faixas).

Uso: python -m src.avaliar_rigor
"""

import json
import logging

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.agente import calcular_sinais, decidir
from src.config import (
    CAMINHO_AVALIACAO_RIGOROSA,
    CAMINHO_PREPARADO,
    COLUNAS_VELOCIDADE,
    FIM_TESTE,
    INICIO_TESTE,
    INICIO_TREINO,
    NOTA_CONFIRMAR,
    REPETICOES_BOOTSTRAP,
    SEMENTE,
    VARIAVEIS_MODELO,
)

logger = logging.getLogger(__name__)

# Número mínimo de sinais para as baselines de regras
_MIN_SINAIS_BASELINE_3 = 3
_MIN_SINAIS_BASELINE_4 = 4
# Faixas de mesma largura em que a calibração divide a nota (0 a 100)
_QTD_FAIXAS_CALIBRACAO = 10


def _treinar_pipeline(treino: pd.DataFrame) -> Pipeline:
    """Treina um pipeline de regressão logística nos dados fornecidos.

    Args:
        treino: DataFrame com as colunas de ``VARIAVEIS_MODELO`` e ``fraude``.

    Returns:
        Pipeline sklearn treinado.
    """
    pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median", add_indicator=True)),
            ("scaler", StandardScaler()),
            (
                "modelo",
                LogisticRegression(class_weight="balanced", max_iter=2000, random_state=SEMENTE),
            ),
        ]
    )
    pipeline.fit(treino[VARIAVEIS_MODELO], treino["fraude"])
    return pipeline


def _metricas_no_corte(y_true: np.ndarray, y_prob: np.ndarray, corte: float) -> dict:
    """Calcula recall, precisão e alertas num corte de nota.

    Args:
        y_true: Rótulos verdadeiros (0/1).
        y_prob: Probabilidades previstas (0–100).
        corte: Nota de corte para classificar como alerta.

    Returns:
        Dicionário com ``alertas``, ``fraudes_detectadas``, ``recall`` e ``precisao``.
    """
    alertas = y_prob >= corte
    n_alertas = int(alertas.sum())
    fraudes_detectadas = int(y_true[alertas].sum()) if n_alertas > 0 else 0
    recall = float(recall_score(y_true, alertas, zero_division=0))
    precisao = float(precision_score(y_true, alertas, zero_division=0))
    return {
        "alertas": n_alertas,
        "fraudes_detectadas": fraudes_detectadas,
        "recall": round(recall, 4),
        "precisao": round(precisao, 4),
    }


def _avaliar_janelas(df: pd.DataFrame) -> list[dict]:
    """Avalia o modelo em duas janelas temporais (jan→fev; jan+fev→mar).

    Args:
        df: DataFrame preparado completo.

    Returns:
        Lista de resultados por janela com PR-AUC, ROC-AUC e métricas no corte.
    """
    janelas = [
        ("jan→fev", "2025-01-01", "2025-02-01", "2025-02-01", "2025-03-01"),
        ("jan+fev→mar", "2025-01-01", "2025-03-01", "2025-03-01", "2025-04-01"),
    ]
    resultados = []
    for nome, ini_tr, fim_tr, ini_te, fim_te in janelas:
        treino = df[(df["data_hora"] >= ini_tr) & (df["data_hora"] < fim_tr)].copy()
        teste = df[(df["data_hora"] >= ini_te) & (df["data_hora"] < fim_te)].copy()
        pipeline = _treinar_pipeline(treino)
        y_true = teste["fraude"].values
        y_prob = pipeline.predict_proba(teste[VARIAVEIS_MODELO])[:, 1] * 100
        pr_auc = float(average_precision_score(y_true, y_prob))
        roc_auc = float(roc_auc_score(y_true, y_prob))
        corte = _metricas_no_corte(y_true, y_prob, NOTA_CONFIRMAR)
        resultados.append(
            {
                "janela": nome,
                "treino_linhas": len(treino),
                "treino_fraudes": int(treino["fraude"].sum()),
                "teste_linhas": len(teste),
                "teste_fraudes": int(y_true.sum()),
                "pr_auc": round(pr_auc, 4),
                "roc_auc": round(roc_auc, 4),
                "no_corte": corte,
            }
        )
    return resultados


def _bootstrap_ic(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    corte: float,
    n: int = REPETICOES_BOOTSTRAP,
    semente: int = SEMENTE,
) -> dict:
    """Calcula IC 95% de recall e precisão por bootstrap.

    Args:
        y_true: Rótulos verdadeiros.
        y_prob: Probabilidades (0–100).
        corte: Nota de corte.
        n: Número de repetições bootstrap.
        semente: Semente de aleatoriedade.

    Returns:
        Dicionário com listas ``recall_ic95`` e ``precisao_ic95`` (inferior, superior).
    """
    rng = np.random.default_rng(semente)
    recalls = []
    precisoes = []
    tam = len(y_true)
    for _ in range(n):
        idx = rng.integers(0, tam, size=tam)
        yt = y_true[idx]
        yp = y_prob[idx]
        alertas = yp >= corte
        recalls.append(float(recall_score(yt, alertas, zero_division=0)))
        precisoes.append(float(precision_score(yt, alertas, zero_division=0)))
    recalls_arr = np.sort(recalls)
    precisoes_arr = np.sort(precisoes)
    low = int(n * 0.025)
    high = int(n * 0.975)
    return {
        "recall_ic95": [round(recalls_arr[low], 4), round(recalls_arr[high], 4)],
        "precisao_ic95": [round(precisoes_arr[low], 4), round(precisoes_arr[high], 4)],
    }


def _comparar_baselines(treino: pd.DataFrame, teste: pd.DataFrame) -> dict:
    """Compara PR-AUC de quatro abordagens no conjunto de teste.

    Abordagens: só regras (≥3 sinais), só regras (≥4 sinais), só modelo,
    Sentinela completo e HistGradientBoostingClassifier.

    Args:
        treino: Dados de treino.
        teste: Dados de teste.

    Returns:
        Dicionário com métricas de cada baseline.
    """
    pipeline = _treinar_pipeline(treino)
    y_true = teste["fraude"].values

    # Só modelo
    y_prob = pipeline.predict_proba(teste[VARIAVEIS_MODELO])[:, 1] * 100

    # Sentinela completo: nota do modelo, corte NOTA_CONFIRMAR
    sentinela_alertas = np.array(
        [
            1 if decidir(float(y_prob[i]), calcular_sinais(r.to_dict())) != "APROVAR" else 0
            for i, (_, r) in enumerate(teste.iterrows())
        ]
    )

    # Só regras com ≥3 e ≥4 sinais
    n_sinais = np.array([len(calcular_sinais(r.to_dict())) for _, r in teste.iterrows()])
    regras_3 = (n_sinais >= _MIN_SINAIS_BASELINE_3).astype(int)
    regras_4 = (n_sinais >= _MIN_SINAIS_BASELINE_4).astype(int)

    # HistGradientBoosting (em memória, não salvo)
    hgb = HistGradientBoostingClassifier(
        class_weight="balanced", max_iter=200, learning_rate=0.05, random_state=SEMENTE
    )
    hgb.fit(treino[VARIAVEIS_MODELO], treino["fraude"])
    y_prob_hgb = hgb.predict_proba(teste[VARIAVEIS_MODELO])[:, 1] * 100

    def _metricas_bin(y_pred: np.ndarray) -> dict:
        return {
            "alertas": int(y_pred.sum()),
            "fraudes_detectadas": int(y_true[y_pred.astype(bool)].sum()),
            "recall": round(float(recall_score(y_true, y_pred, zero_division=0)), 4),
            "precisao": round(float(precision_score(y_true, y_pred, zero_division=0)), 4),
        }

    return {
        "so_regras_3_sinais": _metricas_bin(regras_3),
        "so_regras_4_sinais": _metricas_bin(regras_4),
        "so_modelo": {
            "pr_auc": round(float(average_precision_score(y_true, y_prob)), 4),
            "roc_auc": round(float(roc_auc_score(y_true, y_prob)), 4),
            **_metricas_no_corte(y_true, y_prob, NOTA_CONFIRMAR),
        },
        "sentinela": _metricas_bin(sentinela_alertas),
        "hgb": {
            "pr_auc": round(float(average_precision_score(y_true, y_prob_hgb)), 4),
            "roc_auc": round(float(roc_auc_score(y_true, y_prob_hgb)), 4),
            **_metricas_no_corte(y_true, y_prob_hgb, NOTA_CONFIRMAR),
        },
    }


def _ablacao(treino: pd.DataFrame, teste: pd.DataFrame) -> list[dict]:
    """Mede a queda de PR-AUC ao remover cada variável e as 3 de velocidade juntas.

    Args:
        treino: Dados de treino.
        teste: Dados de teste.

    Returns:
        Lista de dicionários com ``variavel`` removida e ``pr_auc``.
    """
    y_true = teste["fraude"].values
    resultados = []

    for var in VARIAVEIS_MODELO:
        variaveis_sem = [v for v in VARIAVEIS_MODELO if v != var]
        pipeline = Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median", add_indicator=True)),
                ("scaler", StandardScaler()),
                (
                    "modelo",
                    LogisticRegression(
                        class_weight="balanced", max_iter=2000, random_state=SEMENTE
                    ),
                ),
            ]
        )
        pipeline.fit(treino[variaveis_sem], treino["fraude"])
        y_prob = pipeline.predict_proba(teste[variaveis_sem])[:, 1] * 100
        pr_auc = float(average_precision_score(y_true, y_prob))
        resultados.append({"variavel_removida": var, "pr_auc": round(pr_auc, 4)})

    # Sem as 3 de velocidade juntas
    variaveis_sem_vel = [v for v in VARIAVEIS_MODELO if v not in COLUNAS_VELOCIDADE]
    pipeline_sem_vel = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median", add_indicator=True)),
            ("scaler", StandardScaler()),
            (
                "modelo",
                LogisticRegression(class_weight="balanced", max_iter=2000, random_state=SEMENTE),
            ),
        ]
    )
    pipeline_sem_vel.fit(treino[variaveis_sem_vel], treino["fraude"])
    y_prob_sem_vel = pipeline_sem_vel.predict_proba(teste[variaveis_sem_vel])[:, 1] * 100
    pr_auc_sem_vel = float(average_precision_score(y_true, y_prob_sem_vel))
    resultados.append(
        {
            "variavel_removida": "COLUNAS_VELOCIDADE (3 juntas)",
            "pr_auc": round(pr_auc_sem_vel, 4),
        }
    )

    return resultados


def _calibracao(y_true: np.ndarray, y_prob: np.ndarray) -> dict:
    """Calcula Brier score e 10 faixas de calibração.

    A última faixa inclui a nota 100; sem isso, as compras com nota máxima (quase todas
    fraudes) ficariam fora de todas as faixas.

    Args:
        y_true: Rótulos verdadeiros.
        y_prob: Probabilidades (0–100); convertidas para 0–1 internamente.

    Returns:
        Dicionário com ``brier`` e lista ``faixas`` com 10 entradas. Em cada faixa,
        ``taxa_prevista_pct`` é a média da nota prevista nela (None se vazia).
    """
    prob01 = y_prob / 100.0
    brier = float(brier_score_loss(y_true, prob01))
    faixas = []
    for i in range(_QTD_FAIXAS_CALIBRACAO):
        low = i / _QTD_FAIXAS_CALIBRACAO
        high = (i + 1) / _QTD_FAIXAS_CALIBRACAO
        acima_do_inicio = prob01 >= low
        ultima_faixa = i == _QTD_FAIXAS_CALIBRACAO - 1
        abaixo_do_fim = prob01 <= high if ultima_faixa else prob01 < high
        mascara = acima_do_inicio & abaixo_do_fim
        n = int(mascara.sum())
        fraudes = int(y_true[mascara].sum()) if n > 0 else 0
        taxa_real = round(fraudes / n * 100, 2) if n > 0 else None
        taxa_prevista = round(float(prob01[mascara].mean()) * 100, 2) if n > 0 else None
        faixas.append(
            {
                "faixa": f"{int(low * 100)}-{int(high * 100)}",
                "n": n,
                "fraudes": fraudes,
                "taxa_real_pct": taxa_real,
                "taxa_prevista_pct": taxa_prevista,
            }
        )
    return {"brier": round(brier, 6), "faixas": faixas}


def calcular_avaliacao_rigorosa(df: pd.DataFrame) -> dict:
    """Executa a avaliação rigorosa completa e devolve o dicionário de resultados.

    Args:
        df: DataFrame preparado completo (parquet).

    Returns:
        Dicionário com janelas, bootstrap, baselines, ablacao e calibracao.
    """
    treino = df[(df["data_hora"] >= INICIO_TREINO) & (df["data_hora"] < INICIO_TESTE)].copy()
    teste = df[(df["data_hora"] >= INICIO_TESTE) & (df["data_hora"] < FIM_TESTE)].copy()

    pipeline = _treinar_pipeline(treino)
    y_true = teste["fraude"].values
    y_prob = pipeline.predict_proba(teste[VARIAVEIS_MODELO])[:, 1] * 100

    janelas = _avaliar_janelas(df)
    ic = _bootstrap_ic(y_true, y_prob, NOTA_CONFIRMAR)
    baselines = _comparar_baselines(treino, teste)
    ablacao = _ablacao(treino, teste)
    calibracao = _calibracao(y_true, y_prob)

    return {
        "janelas_temporais": janelas,
        "bootstrap_ic95": ic,
        "baselines": baselines,
        "ablacao": ablacao,
        "calibracao": calibracao,
    }


def main() -> None:
    """Ponto de entrada: lê o parquet, calcula e grava avaliacao_rigorosa.json."""
    print("Carregando dados preparados...")
    df = pd.read_parquet(CAMINHO_PREPARADO)

    print("Calculando avaliação rigorosa (pode demorar alguns minutos)...")
    resultado = calcular_avaliacao_rigorosa(df)

    CAMINHO_AVALIACAO_RIGOROSA.parent.mkdir(parents=True, exist_ok=True)
    with CAMINHO_AVALIACAO_RIGOROSA.open("w", encoding="utf-8") as arq:
        json.dump(resultado, arq, indent=2, ensure_ascii=False)
    print(f"Avaliação rigorosa salva em {CAMINHO_AVALIACAO_RIGOROSA}")


if __name__ == "__main__":
    main()
