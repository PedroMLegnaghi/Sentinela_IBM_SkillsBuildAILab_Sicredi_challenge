"""Exporta os rótulos de retorno para uma base de retreino (Issue #127).

Executar: python -m src.exportar_retreino

Lê os eventos de ``data/rotulos_retreino.csv``, descarta os sem rótulo, fica com o último
evento de cada compra e grava ``data/retreino.parquet`` com as 11 variáveis do modelo,
``data_hora`` e ``rotulo_retorno`` (1 = fraude, 0 = legítima). Não retreina nada.
"""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd

from src.composicao import obter_rotulos
from src.config import CAMINHO_PREPARADO, VARIAVEIS_MODELO
from src.dominio.rotulos import EventoRotulo

CAMINHO_RETREINO = CAMINHO_PREPARADO.parent / "retreino.parquet"
ROTULO_PARA_NUMERO = {"fraude": 1, "legitima": 0}


def montar_base_retreino(eventos: Sequence[EventoRotulo]) -> pd.DataFrame:
    """Base de retreino: último evento rotulado de cada compra.

    Args:
        eventos: Eventos na ordem em que foram gravados.

    Returns:
        DataFrame com ``VARIAVEIS_MODELO``, ``data_hora`` e ``rotulo_retorno``.
    """
    ultimos: dict[str, EventoRotulo] = {}
    for evento in eventos:
        if evento.rotulo in ROTULO_PARA_NUMERO:
            ultimos.pop(evento.id_compra, None)  # o último evento vence e vai para o fim
            ultimos[evento.id_compra] = evento
    linhas = [
        {
            **{nome: e.variaveis.get(nome) for nome in VARIAVEIS_MODELO},
            "data_hora": pd.to_datetime(e.data_hora, errors="coerce"),
            "rotulo_retorno": ROTULO_PARA_NUMERO[str(e.rotulo)],
        }
        for e in ultimos.values()
    ]
    colunas = [*VARIAVEIS_MODELO, "data_hora", "rotulo_retorno"]
    base = pd.DataFrame(linhas, columns=colunas)
    base[list(VARIAVEIS_MODELO)] = base[list(VARIAVEIS_MODELO)].astype("float64")
    return base


def exportar() -> pd.DataFrame:
    """Lê os eventos, grava o parquet e imprime o resumo."""
    eventos = obter_rotulos().listar()
    base = montar_base_retreino(eventos)
    base.to_parquet(CAMINHO_RETREINO, index=False)
    sem_rotulo = sum(1 for e in eventos if e.rotulo is None)
    fraudes = int((base["rotulo_retorno"] == 1).sum())
    legitimas = int((base["rotulo_retorno"] == 0).sum())
    print(f"Eventos lidos: {len(eventos)}")  # noqa: T201
    print(f"Rótulos de fraude exportados: {fraudes}")  # noqa: T201
    print(f"Rótulos de legítima exportados: {legitimas}")  # noqa: T201
    print(f"Eventos sem rótulo: {sem_rotulo}")  # noqa: T201
    print(f"Base de retreino salva em {CAMINHO_RETREINO}")  # noqa: T201
    return base


if __name__ == "__main__":
    exportar()
