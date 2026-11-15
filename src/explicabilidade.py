"""O que pesou na nota: contribuições e importância global das variáveis (Issue #41).

Com o pipeline salvo (``imputer`` → ``scaler`` → ``modelo``) e sem treinar nada, a contribuição
de cada coluna da regressão logística é ``coeficiente × valor padronizado``. A soma das
contribuições mais o intercepto é o log-odds da nota, então o analista vê exatamente o que
empurrou a nota para cima ou para baixo.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline

# Nomes em português das variáveis do modelo, para o painel e para a auditoria por IA
NOMES_LEGIVEIS = {
    "valor": "Valor da compra",
    "hora": "Hora do dia",
    "madrugada": "Compra de madrugada",
    "credito": "Cartão de crédito",
    "nao_presente": "Cartão não presente",
    "ip_pais_desconhecido": "IP de país desconhecido",
    "vel_cartao_terminal_1h": "Uso do cartão em terminais na última hora",
    "qtd_transacoes_cartao_1min": "Transações do cartão no último minuto",
    "qtd_token_carteira_3m": "Uso do token de carteira digital em 3 meses",
    "dist_terminal_anterior_km": "Distância do terminal anterior",
    "risco_estabelecimento": "Risco do estabelecimento",
}
# Mesmo prefixo que o treino usa ao imprimir os coeficientes dos indicadores de vazio
PREFIXO_FALTANTE = "faltante_"


def nome_legivel(variavel: str) -> str:
    """Nome em português de uma coluna da regressão.

    Args:
        variavel: Nome da variável ou de um indicador de vazio (``faltante_<variavel>``).

    Returns:
        Nome legível; indicador de vazio vira "<nome> ausente". Desconhecida, volta como veio.
    """
    if variavel.startswith(PREFIXO_FALTANTE):
        original = variavel[len(PREFIXO_FALTANTE) :]
        return f"{NOMES_LEGIVEIS.get(original, original)} ausente"
    return NOMES_LEGIVEIS.get(variavel, variavel)


def _colunas_da_regressao(pipeline: Pipeline) -> list[str]:
    """Variáveis de entrada seguidas dos indicadores de vazio, na ordem dos coeficientes."""
    variaveis = list(pipeline.feature_names_in_)
    indices_com_indicador = pipeline.named_steps["imputer"].indicator_.features_
    return variaveis + [f"{PREFIXO_FALTANTE}{variaveis[i]}" for i in indices_com_indicador]


def _valores_padronizados(pipeline: Pipeline, transacao: dict[str, Any]) -> np.ndarray:
    """Aplica imputer e scaler à transação; chaves ausentes ou None viram NaN, como no agente."""
    variaveis = list(pipeline.feature_names_in_)
    entrada = pd.DataFrame([{v: transacao.get(v) for v in variaveis}], columns=variaveis)
    imputado = pipeline.named_steps["imputer"].transform(entrada)
    return pipeline.named_steps["scaler"].transform(imputado)[0]


def contribuicoes(pipeline: Pipeline, transacao: dict[str, Any]) -> list[dict[str, Any]]:
    """Calcula quanto cada coluna da regressão pesou na nota desta transação.

    Args:
        pipeline: Pipeline scikit-learn treinado (imputer → scaler → regressão logística).
        transacao: Dicionário com os campos da transação; ausentes viram NaN.

    Returns:
        Lista de ``{"variavel": str, "nome": str, "contribuicao": float}`` para as variáveis e
        os indicadores de vazio, ordenada por valor absoluto decrescente. A soma mais o
        intercepto é o log-odds da nota.
    """
    coeficientes = pipeline.named_steps["modelo"].coef_[0]
    valores = _valores_padronizados(pipeline, transacao)
    itens = [
        {"variavel": coluna, "nome": nome_legivel(coluna), "contribuicao": float(coef * valor)}
        for coluna, coef, valor in zip(
            _colunas_da_regressao(pipeline), coeficientes, valores, strict=True
        )
    ]
    return sorted(itens, key=lambda item: abs(item["contribuicao"]), reverse=True)


def importancia_global(pipeline: Pipeline) -> list[dict[str, Any]]:
    """Importância de cada coluna no modelo inteiro, sem depender de uma transação.

    Como as colunas entram padronizadas, o valor absoluto do coeficiente compara o peso delas.

    Args:
        pipeline: Pipeline scikit-learn treinado (imputer → scaler → regressão logística).

    Returns:
        Lista de ``{"variavel": str, "nome": str, "coeficiente": float}`` ordenada por valor
        absoluto decrescente do coeficiente.
    """
    coeficientes = pipeline.named_steps["modelo"].coef_[0]
    itens = [
        {"variavel": coluna, "nome": nome_legivel(coluna), "coeficiente": float(coef)}
        for coluna, coef in zip(_colunas_da_regressao(pipeline), coeficientes, strict=True)
    ]
    return sorted(itens, key=lambda item: abs(item["coeficiente"]), reverse=True)
