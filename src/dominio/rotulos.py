"""Rótulos de retorno para o retreino do modelo (ESPECIFICACAO, seção 17.7; Issue #127).

Cada resposta do associado, contestação ou bloqueio do auditor vira um evento com o que o
modelo viu, o que decidiu e o que o associado disse. Nada de nome nem identificador da base
de cartão, cliente ou estabelecimento.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from src.dominio.entidades import Compra

ORIGENS = ("resposta_aviso", "contestacao", "bloqueio_auditor")
# Mesma ordem de VARIAVEIS_MODELO em src/config.py (o domínio não importa a configuração)
VARIAVEIS = (
    "valor",
    "hora",
    "madrugada",
    "credito",
    "nao_presente",
    "ip_pais_desconhecido",
    "vel_cartao_terminal_1h",
    "qtd_transacoes_cartao_1min",
    "qtd_token_carteira_3m",
    "dist_terminal_anterior_km",
    "risco_estabelecimento",
)


@dataclass(frozen=True)
class EventoRotulo:
    """Uma linha do histórico de rótulos, só de acréscimo."""

    registrado_em: str
    origem: str
    id_compra: str
    id_transacao: int | None
    simulada: bool
    nota: float | None
    decisao_modelo: str | None
    situacao: str
    resposta: str | None
    rotulo: str | None
    data_hora: str | None
    valor: float | None
    tipo_transacao: str
    modalidade_transacao: str
    variaveis: dict[str, float | None] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Garante uma origem conhecida."""
        if self.origem not in ORIGENS:
            raise ValueError(f"Origem desconhecida: {self.origem}.")

    def como_linha(self) -> dict[str, Any]:
        """Dicionário plano: campos do evento seguidos das 11 variáveis do modelo."""
        linha = {k: v for k, v in asdict(self).items() if k != "variaveis"}
        linha.update({nome: self.variaveis.get(nome) for nome in VARIAVEIS})
        return linha


def rotulo_do_evento(origem: str, resposta: str | None) -> str | None:
    """Tabela de rótulos da seção 17.7.

    Args:
        origem: "resposta_aviso", "contestacao" ou "bloqueio_auditor".
        resposta: "sim", "nao" ou None.

    Returns:
        "fraude", "legitima" ou None (sem rótulo).
    """
    if origem == "contestacao":
        return "fraude"  # fraude que o modelo aprovou
    if resposta == "nao":
        return "fraude"
    if resposta == "sim":
        return "legitima"
    return None


def evento_da_compra(compra: Compra, origem: str, resposta: str | None, em: str) -> EventoRotulo:
    """Monta o evento a partir da compra, com as variáveis que o modelo usou.

    Args:
        compra: Compra já atualizada pela regra (situação depois do evento).
        origem: De onde veio o evento.
        resposta: Resposta do associado, quando houver.
        em: Momento do evento em ISO 8601.

    Returns:
        O EventoRotulo a acrescentar.
    """
    return EventoRotulo(
        registrado_em=em,
        origem=origem,
        id_compra=compra.id_compra,
        id_transacao=None if compra.simulada else compra.id_transacao_base,
        simulada=compra.simulada,
        nota=(compra.analise or {}).get("nota"),
        decisao_modelo=compra.decisao,
        situacao=compra.situacao,
        resposta=resposta,
        rotulo=rotulo_do_evento(origem, resposta),
        data_hora=compra.data_hora,
        valor=compra.valor,
        tipo_transacao=compra.tipo_transacao,
        modalidade_transacao=compra.modalidade_transacao,
        variaveis=dict(compra.variaveis or {}),
    )
