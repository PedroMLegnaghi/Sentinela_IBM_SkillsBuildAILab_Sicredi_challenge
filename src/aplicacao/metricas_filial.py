"""Métricas do gerente (ESPECIFICACAO, seção 17.4; Issue #98).

A parte de março chega pronta (calculada uma vez na subida, por filial); aqui só se soma a
parte ao vivo: compras simuladas, avisos respondidos e contestações da carteira.
"""

from __future__ import annotations

import statistics
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from src.dominio import regras
from src.dominio.entidades import Compra
from src.portas.repositorios import Repositorios

PERIODO = "2025-03"
CHAVE_POR_DECISAO = {
    "APROVAR": "aprovadas",
    "PEDIR_CONFIRMACAO": "confirmacoes",
    "BLOQUEAR": "bloqueadas",
}


@dataclass
class ResumoFilial:
    """Contagens de uma filial: totais, valor protegido e linhas por tipo e modalidade."""

    aprovadas: int = 0
    confirmacoes: int = 0
    bloqueadas: int = 0
    valor_protegido: float = 0.0
    por_tipo: dict[tuple[str, str], dict[str, int]] = field(default_factory=dict)

    def somar(self, decisao: str, valor: float | None, tipo: str, modalidade: str) -> None:
        """Conta uma compra pela decisão do modelo; bloqueada soma no valor protegido."""
        chave = CHAVE_POR_DECISAO.get(decisao)
        if chave is None:
            return
        setattr(self, chave, getattr(self, chave) + 1)
        if decisao == "BLOQUEAR" and valor is not None:
            self.valor_protegido += valor
        linha = self.por_tipo.setdefault(
            (tipo, modalidade), {"aprovadas": 0, "confirmacoes": 0, "bloqueadas": 0}
        )
        linha[chave] += 1

    def copiar(self) -> ResumoFilial:
        """Cópia independente, para somar a parte ao vivo sem mexer no resumo de março."""
        return ResumoFilial(
            self.aprovadas,
            self.confirmacoes,
            self.bloqueadas,
            self.valor_protegido,
            {chave: dict(linha) for chave, linha in self.por_tipo.items()},
        )


def resumir_marco(linhas: Iterable[Mapping[str, Any]]) -> dict[str, ResumoFilial]:
    """Agrupa as compras de março por filial.

    Args:
        linhas: Dicionários com ``id_filial``, ``decisao``, ``valor``, ``tipo_transacao`` e
            ``modalidade_transacao``.

    Returns:
        Resumo por ``id_filial``.
    """
    resumos: dict[str, ResumoFilial] = {}
    for linha in linhas:
        resumo = resumos.setdefault(str(linha["id_filial"]), ResumoFilial())
        resumo.somar(
            str(linha["decisao"]),
            linha.get("valor"),
            str(linha.get("tipo_transacao") or ""),
            str(linha.get("modalidade_transacao") or ""),
        )
    return resumos


def _segundos(inicio: str, fim: str) -> float | None:
    try:
        return (datetime.fromisoformat(fim) - datetime.fromisoformat(inicio)).total_seconds()
    except (TypeError, ValueError):
        return None


def _acerto_e_tempo(
    compras: list[Compra], obter_aviso: Callable[[str], dict[str, Any] | None]
) -> tuple[dict[str, Any], float | None]:
    """Acerto do modelo pelos avisos da carteira e a mediana do tempo de resposta."""
    certos = desnecessarios = sem_resposta = 0
    tempos: list[float] = []
    for compra in compras:
        aviso = obter_aviso(compra.id_notificacao) if compra.id_notificacao else None
        if aviso is None:
            continue
        if aviso["status"] == "negada":
            certos += 1
        elif aviso["status"] == "confirmada":
            desnecessarios += 1
        else:
            sem_resposta += 1
            continue
        segundos = _segundos(aviso["criada_em"], aviso.get("respondida_em"))
        if segundos is not None:
            tempos.append(segundos)
    respondidos = certos + desnecessarios
    acerto = {
        "alertas_certos": certos,
        "alertas_desnecessarios": desnecessarios,
        "sem_resposta": sem_resposta,
        "taxa": round(certos / respondidos * 100, 1) if respondidos else None,
    }
    return acerto, round(statistics.median(tempos), 1) if tempos else None


def _fraudes_aprovadas(repos: Repositorios, id_filial: str) -> dict[str, Any]:
    """Compras contestadas da carteira: fraudes que o modelo deixou passar."""
    itens = []
    for contestacao in repos.contestacoes.listar_por_filial(id_filial):
        compra = repos.compras.obter(contestacao.id_compra)
        if compra is None:
            continue
        associado = repos.associados.obter(compra.id_associado)
        cartao = repos.cartoes.obter(compra.id_cartao) if compra.id_cartao else None
        itens.append(
            {
                "associado": regras.nome_abreviado(associado.nome) if associado else "",
                "final_cartao": cartao.final if cartao else "",
                "data_hora": compra.data_hora,
                "valor": compra.valor,
            }
        )
    return {"total": len(itens), "itens": itens}


def calcular_metricas(
    repos: Repositorios,
    id_filial: str,
    resumo_marco: ResumoFilial,
    obter_aviso: Callable[[str], dict[str, Any] | None],
) -> dict[str, Any]:
    """Monta o painel do gerente: março da carteira mais a parte ao vivo.

    Args:
        repos: Repositórios da aplicação.
        id_filial: Filial da sessão.
        resumo_marco: Contagens de março desta filial, calculadas na subida.
        obter_aviso: Devolve a Notificacao (seção 15) pelo id, ou None.

    Returns:
        Corpo de ``GET /api/filial/metricas``.
    """
    resumo = resumo_marco.copiar()
    compras = repos.compras.listar_por_filial(id_filial)
    for compra in compras:
        if compra.simulada and compra.decisao:
            resumo.somar(
                compra.decisao, compra.valor, compra.tipo_transacao, compra.modalidade_transacao
            )
    acerto, tempo = _acerto_e_tempo(compras, obter_aviso)
    filial = repos.filiais.obter(id_filial)
    return {
        "filial": {"id_filial": id_filial, "nome": filial.nome if filial else ""},
        "periodo": PERIODO,
        "totais": {
            "compras": resumo.aprovadas + resumo.confirmacoes + resumo.bloqueadas,
            "aprovadas": resumo.aprovadas,
            "confirmacoes": resumo.confirmacoes,
            "bloqueadas": resumo.bloqueadas,
            "valor_protegido": round(resumo.valor_protegido, 2),
        },
        "por_tipo": [
            {"tipo_transacao": tipo, "modalidade_transacao": modalidade, **contagens}
            for (tipo, modalidade), contagens in sorted(resumo.por_tipo.items())
        ],
        "acerto_modelo": acerto,
        "fraudes_aprovadas": _fraudes_aprovadas(repos, id_filial),
        "tempo_resposta_mediano_s": tempo,
    }
