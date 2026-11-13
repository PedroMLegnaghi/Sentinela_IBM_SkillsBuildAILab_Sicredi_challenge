"""Gravação e leitura das respostas do analista no arquivo de feedback."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

COLUNAS_FEEDBACK = ["registrado_em", "id_transacao", "nota", "decisao", "resposta_analista"]
RESPOSTAS_VALIDAS = ("fraude", "legitima")


@dataclass(frozen=True)
class RespostaAnalista:
    """Resposta registrada pelo analista para uma transação.

    Args:
        id_transacao: Identificador da transação avaliada.
        nota: Nota de risco atribuída pelo agente.
        decisao: Decisão do agente (BLOQUEAR, PEDIR_CONFIRMACAO ou APROVAR).
        resposta_analista: "fraude" ou "legitima".
        registrado_em: Momento do registro.
    """

    id_transacao: int
    nota: float
    decisao: str
    resposta_analista: str
    registrado_em: datetime


def registrar_resposta(caminho: Path, resposta: RespostaAnalista) -> None:
    """Acrescenta uma resposta do analista no arquivo CSV de feedback.

    Cria a pasta e o arquivo se não existirem; escreve o cabeçalho apenas
    na criação. O OSError sobe para a página tratar.

    Args:
        caminho: Caminho do arquivo feedback.csv.
        resposta: Dados da resposta a registrar.

    Raises:
        ValueError: Se resposta_analista não for "fraude" ou "legitima".
        OSError: Se não for possível gravar o arquivo.
    """
    if resposta.resposta_analista not in RESPOSTAS_VALIDAS:
        raise ValueError(
            f"Resposta inválida: '{resposta.resposta_analista}'. " f"Use um de: {RESPOSTAS_VALIDAS}"
        )

    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    arquivo_novo = not caminho.exists()

    with caminho.open("a", encoding="utf-8", newline="") as arquivo:
        escritor = csv.writer(arquivo)
        if arquivo_novo:
            escritor.writerow(COLUNAS_FEEDBACK)
        escritor.writerow(
            [
                resposta.registrado_em.strftime("%Y-%m-%dT%H:%M:%S"),
                resposta.id_transacao,
                resposta.nota,
                resposta.decisao,
                resposta.resposta_analista,
            ]
        )


def ler_ultima_resposta(caminho: Path, id_transacao: int) -> RespostaAnalista | None:
    """Lê a última resposta registrada para uma transação.

    Args:
        caminho: Caminho do arquivo feedback.csv.
        id_transacao: Identificador da transação a buscar.

    Returns:
        Última RespostaAnalista para o id, ou None se não houver.

    Raises:
        ValueError: Se o cabeçalho do arquivo diferir de COLUNAS_FEEDBACK.
    """
    caminho = Path(caminho)
    if not caminho.exists():
        return None

    with caminho.open(encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        if leitor.fieldnames != COLUNAS_FEEDBACK:
            raise ValueError(
                f"Cabeçalho inválido em {caminho}. Esperado: {COLUNAS_FEEDBACK}. "
                f"Encontrado: {leitor.fieldnames}"
            )
        ultima: RespostaAnalista | None = None
        for linha in leitor:
            if int(linha["id_transacao"]) == id_transacao:
                ultima = RespostaAnalista(
                    id_transacao=int(linha["id_transacao"]),
                    nota=float(linha["nota"]),
                    decisao=linha["decisao"],
                    resposta_analista=linha["resposta_analista"],
                    registrado_em=datetime.fromisoformat(linha["registrado_em"]),
                )
    return ultima
