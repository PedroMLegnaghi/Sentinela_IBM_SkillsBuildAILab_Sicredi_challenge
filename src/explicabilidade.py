"""Contribuições e importância global das variáveis do modelo Sentinela.

Esqueleto: devolve lista vazia até a Issue #41 implementar o cálculo real.
"""

from __future__ import annotations

# TODO(#41, 2026-11-12): implementar contribuicoes e importancia_global com o pipeline real


def contribuicoes(pipeline, transacao: dict) -> list[dict]:
    """Calcula as contribuições de cada variável para a nota da transação.

    Esqueleto — devolve lista vazia até a Issue #41.

    Args:
        pipeline: Pipeline scikit-learn treinado (imputer → scaler → regressão).
        transacao: Dicionário com os campos da transação.

    Returns:
        Lista de dicts ``{"variavel": str, "nome": str, "contribuicao": float}``,
        ordenada por valor absoluto da contribuição. Vazia até a Issue #41.
    """
    return []
