"""Rota da matriz (ESPECIFICACAO, seção 17.8): o painel de todas as filiais.

Só o papel "matriz" acessa. Reaproveita o resumo de março e o painel de cada filial (seção 17.4).
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends

from src.api import respostas, rotas_filial
from src.api.esquemas_refatoracao import MetricasMatrizSchema
from src.api.sessao import sessao_com_papel
from src.aplicacao import filial as filial_app
from src.aplicacao import metricas_matriz
from src.associado import notificacoes
from src.config import CAMINHO_AVALIACAO, CAMINHO_METRICAS
from src.dominio.entidades import Perfil

router = APIRouter(prefix="/api/matriz", tags=["matriz"])
Matriz = Annotated[Perfil, Depends(sessao_com_papel("matriz"))]


@router.get("/metricas", response_model=MetricasMatrizSchema)
def metricas(
    perfil: Matriz,
) -> dict[str, Any]:  # noqa: ARG001 (o papel é conferido pela dependência)
    """Consolidado da cooperativa, painel de cada filial e desempenho do modelo."""
    repos, _ = rotas_filial._repositorios_com_fila()  # noqa: SLF001
    resumos = rotas_filial._resumos_de_marco(repos)  # noqa: SLF001
    return metricas_matriz.calcular_painel_matriz(
        repos,
        filial_app.FILIAIS,
        resumos,
        notificacoes.obter,
        respostas._carregar_json_opcional(CAMINHO_AVALIACAO),  # noqa: SLF001
        respostas._carregar_json_opcional(CAMINHO_METRICAS),  # noqa: SLF001
    )
