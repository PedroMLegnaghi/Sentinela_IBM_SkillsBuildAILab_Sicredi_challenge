"""Ferramentas que a auditoria usa para investigar uma transação (ESPECIFICACAO, seção 13).

Cada ferramenta lê só dados anteriores à transação e devolve o envelope
``{"status": "ok"|"sem_dados", "dados": dict, "campos_ausentes": list[str]}``. Nenhuma
devolve o rótulo, a decisão do sistema atual, colunas proibidas ou identificadores.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from typing import Any

import pandas as pd

from src.config import LIMIAR_RAJADA_1MIN, VARIAVEIS_MODELO

LIMITE_HISTORICO = 10
MAX_CONTRIBUICOES = 6

DESCRICOES = {
    "sinais_da_transacao": "Sinais de alerta disparados pelas regras e campos vazios da compra.",
    "contribuicoes_da_nota": "Variáveis que mais aumentaram ou diminuíram a nota do modelo.",
    "historico_do_cartao": "Resumo das últimas compras do mesmo cartão antes desta.",
    "perfil_do_cliente": "Padrão de gasto do cliente antes desta compra.",
    "perfil_do_estabelecimento": "Padrão das compras no mesmo estabelecimento antes desta.",
}


def _numero(valor: Any) -> float | None:
    """Converte para float com 2 casas; vazio, NaN ou texto viram None."""
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(numero) or math.isinf(numero) else round(numero, 2)


def _envelope(dados: dict[str, Any], ausentes: list[str]) -> dict[str, Any]:
    """Monta o envelope padrão; sem dados quando o dicionário está vazio."""
    return {"status": "ok" if dados else "sem_dados", "dados": dados, "campos_ausentes": ausentes}


def _anteriores(base: pd.DataFrame, coluna: str, transacao: dict[str, Any]) -> pd.DataFrame:
    """Linhas da base com o mesmo valor em ``coluna`` e data anterior à transação.

    Args:
        base: DataFrame preparado.
        coluna: "id_cartao", "id_cliente" ou "id_estabelecimento".
        transacao: Transação auditada (com o identificador e ``data_hora``).

    Returns:
        DataFrame ordenado do mais recente para o mais antigo (pode ser vazio).
    """
    linhas = base[base[coluna] == transacao[coluna]]
    linhas = linhas[linhas["id_transacao"] != transacao.get("id_transacao")]
    momento = pd.to_datetime(transacao.get("data_hora"), errors="coerce")
    if not pd.isna(momento):
        linhas = linhas[linhas["data_hora"] < momento]
    return linhas.sort_values("data_hora", ascending=False)


def _proporcao(serie: pd.Series) -> float | None:
    """Percentual de valores iguais a 1 (2 casas), ou None se a série for vazia."""
    validos = serie.dropna()
    return None if validos.empty else round(float((validos == 1).mean()) * 100, 2)


class CaixaDeFerramentas:
    """Executa as ferramentas sobre uma transação e registra o que foi usado.

    Args:
        transacao: Transação auditada, com os identificadores internos quando houver.
        analise: Analise do modelo (sinais e contribuições).
        base: DataFrame preparado, ou None quando os dados não foram carregados.
    """

    def __init__(
        self, transacao: dict[str, Any], analise: dict[str, Any], base: pd.DataFrame | None
    ):
        self.transacao = transacao
        self.analise = analise
        self.base = base
        self.usadas: list[dict[str, str]] = []
        self._funcoes: dict[str, Callable[[], tuple[dict[str, Any], str]]] = {
            "sinais_da_transacao": self._sinais,
            "contribuicoes_da_nota": self._contribuicoes,
            "historico_do_cartao": self._historico_cartao,
            "perfil_do_cliente": self._perfil_cliente,
            "perfil_do_estabelecimento": self._perfil_estabelecimento,
        }

    def nomes(self) -> list[str]:
        """Nomes das ferramentas, na ordem em que o modo local as executa."""
        return list(self._funcoes)

    def definicoes(self) -> list[dict[str, Any]]:
        """Definições das ferramentas no formato de chamada de função do chat."""
        return [
            {
                "type": "function",
                "function": {
                    "name": nome,
                    "description": DESCRICOES[nome],
                    "parameters": {"type": "object", "properties": {}},
                },
            }
            for nome in self._funcoes
        ]

    def executar(self, nome: str) -> dict[str, Any]:
        """Executa uma ferramenta pelo nome e registra o resumo em ``usadas``.

        Args:
            nome: Nome da ferramenta.

        Returns:
            O envelope da ferramenta.

        Raises:
            KeyError: Se a ferramenta não existir.
        """
        envelope, resumo = self._funcoes[nome]()
        self.usadas.append({"nome": nome, "resumo": resumo})
        return envelope

    def _ausentes_da_transacao(self) -> list[str]:
        return [v for v in VARIAVEIS_MODELO if _numero(self.transacao.get(v)) is None]

    def _sinais(self) -> tuple[dict[str, Any], str]:
        descricoes = [sinal["descricao"] for sinal in self.analise.get("sinais", [])]
        dados = {
            "quantidade": len(descricoes),
            "sinais": descricoes,
            "ip_pais_desconhecido": _numero(self.transacao.get("ip_pais_desconhecido")) == 1,
            "valor": _numero(self.transacao.get("valor")),
            "hora": _numero(self.transacao.get("hora")),
        }
        envelope = {
            "status": "ok",
            "dados": dados,
            "campos_ausentes": self._ausentes_da_transacao(),
        }
        return envelope, f"{len(descricoes)} sinal(is) de alerta"

    def _contribuicoes(self) -> tuple[dict[str, Any], str]:
        itens = self.analise.get("contribuicoes") or []
        principais = [
            {"variavel": item["nome"], "contribuicao": _numero(item["contribuicao"])}
            for item in itens[:MAX_CONTRIBUICOES]
        ]
        dados = {"principais": principais} if principais else {}
        resumo = f"{len(principais)} variáveis com mais peso" if principais else "sem contribuições"
        return _envelope(dados, [] if principais else ["contribuicoes"]), resumo

    def _sem_historico(self, coluna: str) -> tuple[dict[str, Any], str] | None:
        if self.base is None:
            return _envelope({}, ["base de dados"]), "base de dados indisponível"
        if self.transacao.get(coluna) is None or pd.isna(self.transacao.get(coluna)):
            return _envelope({}, [coluna]), "identificador ausente"
        return None

    def _historico_cartao(self) -> tuple[dict[str, Any], str]:
        sem = self._sem_historico("id_cartao")
        if sem is not None:
            return sem
        linhas = _anteriores(self.base, "id_cartao", self.transacao).head(LIMITE_HISTORICO)
        if linhas.empty:
            return _envelope({}, []), "nenhuma compra anterior do cartão"
        rajada = _numero(linhas["qtd_transacoes_cartao_1min"].max())
        dados = {
            "compras_anteriores": len(linhas),
            "mediana_valor": _numero(linhas["valor"].median()),
            "maior_rajada_1min": rajada,
            "rajada_acima_do_limiar": rajada is not None and rajada >= LIMIAR_RAJADA_1MIN,
            "percentual_nao_presente": _proporcao(linhas["nao_presente"]),
        }
        return _envelope(dados, []), f"{len(linhas)} compras anteriores do cartão"

    def _hora_mais_comum(self, linhas: pd.DataFrame) -> int | None:
        """Hora inteira mais frequente nas compras anteriores, ou None se vazio."""
        if "hora" not in linhas.columns:
            return None
        horas = linhas["hora"].dropna()
        if horas.empty:
            return None
        return int(horas.apply(int).mode().iloc[0])

    def _perfil_cliente(self) -> tuple[dict[str, Any], str]:
        sem = self._sem_historico("id_cliente")
        if sem is not None:
            return sem
        linhas = _anteriores(self.base, "id_cliente", self.transacao)
        if linhas.empty:
            return _envelope({}, []), "cliente sem compras anteriores"
        mediana = _numero(linhas["valor"].median())
        valor = _numero(self.transacao.get("valor"))
        razao = round(valor / mediana, 2) if valor is not None and mediana else None
        dados = {
            "compras_anteriores": len(linhas),
            "mediana_valor": mediana,
            "valor_atual_sobre_mediana": razao,
            "hora_mais_comum": self._hora_mais_comum(linhas),
            "percentual_madrugada": _proporcao(linhas["madrugada"]),
            "percentual_credito_nao_presente": _proporcao(
                linhas["credito"] * linhas["nao_presente"]
            ),
        }
        return _envelope(dados, []), f"{len(linhas)} compras anteriores do cliente"

    def _perfil_estabelecimento(self) -> tuple[dict[str, Any], str]:
        sem = self._sem_historico("id_estabelecimento")
        if sem is not None:
            return sem
        linhas = _anteriores(self.base, "id_estabelecimento", self.transacao)
        dados = {
            "compras_anteriores": len(linhas),
            "mediana_valor": _numero(linhas["valor"].median()) if not linhas.empty else None,
            "risco_estabelecimento": _numero(self.transacao.get("risco_estabelecimento")),
        }
        return _envelope(dados, []), f"{len(linhas)} compras anteriores no estabelecimento"
