"""Composição da aplicação (Issue #92): o único lugar que escolhe os adaptadores.

Hoje devolve os repositórios em memória carregados com os dados de demonstração; trocar por
Postgres é trocar só este arquivo.
"""

from __future__ import annotations

import dataclasses
import logging
from collections.abc import Mapping

import pandas as pd

from src.adaptadores.arquivo.rotulos import RotulosEmArquivo
from src.adaptadores.memoria.dados_demo import montar_repositorios
from src.config import CAMINHO_PREPARADO, CAMINHO_ROTULOS
from src.portas.repositorios import RepositorioRotulos, Repositorios

logger = logging.getLogger(__name__)


def _ler_base() -> pd.DataFrame | None:
    """Lê o parquet preparado, ou devolve None se ele faltar ou estiver ilegível."""
    if not CAMINHO_PREPARADO.exists():
        logger.warning(
            "Parquet não encontrado: %s; subindo só com dados inventados.", CAMINHO_PREPARADO
        )
        return None
    try:
        return pd.read_parquet(CAMINHO_PREPARADO)
    except (OSError, ValueError) as erro:
        logger.error("Falha ao ler o parquet: %s", erro)
        return None


def obter_repositorios(
    base: pd.DataFrame | None = None, decisoes: Mapping[int, str] | None = None
) -> Repositorios:
    """Repositórios em memória já carregados com os dados de demonstração.

    Args:
        base: Parquet preparado já em memória; None lê de ``CAMINHO_PREPARADO`` (ou sobe só com
            os dados inventados, se o arquivo faltar).
        decisoes: Decisão do modelo por ``id_transacao`` de março, para carregar as compras dos
            associados com login (seção 17.1).

    Returns:
        Repositorios prontos para a aplicação.
    """
    if base is None:
        base = _ler_base()
    # Os rótulos sobrevivem a reiniciar a API; o resto da demonstração fica em memória.
    return dataclasses.replace(montar_repositorios(base, decisoes), rotulos=obter_rotulos())


def obter_rotulos() -> RepositorioRotulos:
    """Histórico de rótulos usado pela API e pela exportação para o retreino."""
    return RotulosEmArquivo(CAMINHO_ROTULOS)
