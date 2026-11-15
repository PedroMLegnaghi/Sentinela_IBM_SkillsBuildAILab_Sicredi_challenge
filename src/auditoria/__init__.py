"""Auditoria por IA das decisões do modelo (ESPECIFICACAO, seção 13; ADR-012 e ADR-013).

O modelo de machine learning decide; esta auditoria investiga a mesma transação com
ferramentas e devolve um relatório para o analista, sem nunca mudar a decisão.
"""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd

from src.auditoria import local, watsonx
from src.auditoria.ferramentas import CaixaDeFerramentas
from src.auditoria.relatorio import finalizar_relatorio, validar_parcial

logger = logging.getLogger(__name__)

_contexto: dict[str, pd.DataFrame | None] = {"base": None}


def configurar_base(base: pd.DataFrame | None) -> None:
    """Informa a base de transações que as ferramentas consultam.

    Args:
        base: DataFrame preparado, ou None sem dados.
    """
    _contexto["base"] = base


def auditar(transacao: dict[str, Any], analise: dict[str, Any]) -> dict[str, Any]:
    """Audita uma decisão do modelo. Nunca levanta exceção.

    Usa o watsonx.ai quando há credenciais; em qualquer falha dele, cai no modo local.

    Args:
        transacao: Transação auditada (com identificadores internos quando houver; eles não
            saem do servidor).
        analise: Analise do modelo, com ``decisao``, ``sinais`` e ``contribuicoes``.

    Returns:
        O Relatorio da ESPECIFICACAO, seção 13.
    """
    decisao = analise.get("decisao", "")
    if watsonx.credenciais_disponiveis():
        caixa = CaixaDeFerramentas(transacao, analise, _contexto["base"])
        try:
            parcial, modelo = watsonx.auditar_com_watsonx(caixa)
            return finalizar_relatorio(parcial, decisao, caixa.usadas, "watsonx", modelo)
        except watsonx.FalhaWatsonx as erro:
            logger.warning("Auditoria pelo watsonx.ai falhou; usando o modo local: %s", erro)
    caixa = CaixaDeFerramentas(transacao, analise, _contexto["base"])
    parcial = validar_parcial(local.avaliar(caixa))
    return finalizar_relatorio(parcial, decisao, caixa.usadas, "local", local.NOME_MODELO)
