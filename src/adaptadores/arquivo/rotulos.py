"""Rótulos de retorno num CSV só de acréscimo (Issue #127).

Uma linha por evento em ``data/rotulos_retreino.csv``, com cabeçalho na primeira vez. O
arquivo é dado gerado na hora e fica fora do Git.
"""

from __future__ import annotations

import csv
import threading
from pathlib import Path

from src.dominio.rotulos import VARIAVEIS, EventoRotulo

COLUNAS = (
    "registrado_em",
    "origem",
    "id_compra",
    "id_transacao",
    "simulada",
    "nota",
    "decisao_modelo",
    "situacao",
    "resposta",
    "rotulo",
    "data_hora",
    "valor",
    "tipo_transacao",
    "modalidade_transacao",
    *(v for v in VARIAVEIS if v != "valor"),
)
_FLOATS = {"nota", "valor", *VARIAVEIS}


def _numero(texto: str) -> float | None:
    return float(texto) if texto not in ("", "None") else None


def _texto(texto: str) -> str | None:
    return texto or None


def _evento_da_linha(linha: dict[str, str]) -> EventoRotulo:
    """Converte uma linha do CSV de volta em evento."""
    return EventoRotulo(
        registrado_em=linha["registrado_em"],
        origem=linha["origem"],
        id_compra=linha["id_compra"],
        id_transacao=int(linha["id_transacao"]) if linha["id_transacao"] else None,
        simulada=linha["simulada"] == "True",
        nota=_numero(linha["nota"]),
        decisao_modelo=_texto(linha["decisao_modelo"]),
        situacao=linha["situacao"],
        resposta=_texto(linha["resposta"]),
        rotulo=_texto(linha["rotulo"]),
        data_hora=_texto(linha["data_hora"]),
        valor=_numero(linha["valor"]),
        tipo_transacao=linha["tipo_transacao"],
        modalidade_transacao=linha["modalidade_transacao"],
        variaveis={nome: _numero(linha[nome]) for nome in VARIAVEIS},
    )


class RotulosEmArquivo:
    """Implementa ``RepositorioRotulos`` num CSV protegido por ``threading.Lock``."""

    def __init__(self, caminho: Path):
        self._caminho = caminho
        self._lock = threading.Lock()

    def acrescentar(self, evento: EventoRotulo) -> None:
        """Acrescenta uma linha; escreve o cabeçalho se o arquivo ainda não existe."""
        linha = evento.como_linha()
        with self._lock:
            novo = not self._caminho.exists()
            self._caminho.parent.mkdir(parents=True, exist_ok=True)
            with self._caminho.open("a", newline="", encoding="utf-8") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=COLUNAS)
                if novo:
                    escritor.writeheader()
                escritor.writerow({c: "" if linha[c] is None else linha[c] for c in COLUNAS})

    def listar(self) -> list[EventoRotulo]:
        """Todos os eventos, na ordem em que foram gravados."""
        with self._lock:
            if not self._caminho.exists():
                return []
            with self._caminho.open(newline="", encoding="utf-8") as arquivo:
                return [_evento_da_linha(linha) for linha in csv.DictReader(arquivo)]
