"""Painel da matriz (ESPECIFICACAO, seção 17.8).

Junta o painel de cada filial (seção 17.4) num consolidado da cooperativa e acrescenta o
desempenho do modelo em toda a base de teste (março) e quantas fraudes ele viu no treino.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from src.aplicacao import metricas_filial
from src.aplicacao.metricas_filial import ResumoFilial
from src.portas.repositorios import Repositorios

CHAVES_TOTAIS = ("compras", "aprovadas", "confirmacoes", "bloqueadas")
CHAVES_TIPO = ("aprovadas", "confirmacoes", "bloqueadas")


def _consolidar_por_tipo(paineis: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Soma as linhas por tipo e modalidade de todas as filiais."""
    somas: dict[tuple[str, str], dict[str, int]] = {}
    for painel in paineis:
        for linha in painel["por_tipo"]:
            chave = (linha["tipo_transacao"], linha["modalidade_transacao"])
            alvo = somas.setdefault(chave, dict.fromkeys(CHAVES_TIPO, 0))
            for campo in CHAVES_TIPO:
                alvo[campo] += linha[campo]
    return [
        {"tipo_transacao": tipo, "modalidade_transacao": modalidade, **contagens}
        for (tipo, modalidade), contagens in sorted(somas.items())
    ]


def _com_filial(painel: dict[str, Any], itens: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Itens de uma filial com o nome dela, para as listas consolidadas."""
    return [{"filial": painel["filial"]["nome"], **item} for item in itens]


def _modelo(avaliacao: Mapping[str, Any] | None, metricas: Mapping[str, Any] | None):
    """Desempenho do modelo em toda a base de teste e o tamanho do treino.

    A coluna ``decision`` da base não é documentada pela Sicredi como a decisão de um sistema
    real (e nunca recusa compra legítima), por isso o painel não compara com ela.
    """
    if not avaliacao:
        return None
    sentinela = avaliacao.get("sentinela", {})
    treino = (metricas or {}).get("treino", {})
    return {
        "periodo": avaliacao.get("periodo"),
        "transacoes": avaliacao.get("transacoes"),
        "fraudes": avaliacao.get("fraudes_total"),
        "sentinela": {
            "fraudes_bloqueadas": sentinela.get("fraudes_bloqueadas"),
            "bloqueadas": sentinela.get("bloqueadas"),
            "confirmacoes": sentinela.get("confirmacoes"),
            "fraudes_aprovadas": sentinela.get("fraudes_aprovadas"),
        },
        "treino": {"linhas": treino.get("linhas"), "fraudes": treino.get("fraudes")},
        "pr_auc": (metricas or {}).get("pr_auc"),
        "roc_auc": (metricas or {}).get("roc_auc"),
    }


def calcular_painel_matriz(
    repos: Repositorios,
    ids_filiais: tuple[str, ...],
    resumos_marco: Mapping[str, ResumoFilial],
    obter_aviso: Callable[[str], dict[str, Any] | None],
    avaliacao: Mapping[str, Any] | None = None,
    metricas_modelo: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Monta o corpo de ``GET /api/matriz/metricas``.

    Args:
        repos: Repositórios da aplicação.
        ids_filiais: Filiais da cooperativa, na ordem de exibição.
        resumos_marco: Contagens de março por filial, calculadas na subida.
        obter_aviso: Devolve a Notificacao (seção 15) pelo id, ou None.
        avaliacao: Conteúdo de ``modelos/avaliacao_agente.json`` (ou None).
        metricas_modelo: Conteúdo de ``modelos/metricas.json`` (ou None).

    Returns:
        Consolidado, painel de cada filial e desempenho do modelo.
    """
    paineis = [
        metricas_filial.calcular_metricas(
            repos, id_filial, resumos_marco.get(id_filial, ResumoFilial()), obter_aviso
        )
        for id_filial in ids_filiais
    ]
    compras = [c for id_filial in ids_filiais for c in repos.compras.listar_por_filial(id_filial)]
    acerto, tempo = metricas_filial._acerto_e_tempo(compras, obter_aviso)  # noqa: SLF001
    totais = {campo: sum(p["totais"][campo] for p in paineis) for campo in CHAVES_TOTAIS}
    totais["valor_protegido"] = round(sum(p["totais"]["valor_protegido"] for p in paineis), 2)
    fraudes = [i for p in paineis for i in _com_filial(p, p["fraudes_aprovadas"]["itens"])]
    consolidado = {
        "totais": totais,
        "por_tipo": _consolidar_por_tipo(paineis),
        "acerto_modelo": acerto,
        "fraudes_aprovadas": {"total": len(fraudes), "itens": fraudes},
        "tempo_resposta_mediano_s": tempo,
        "bloqueios_por_auditor": [
            i for p in paineis for i in _com_filial(p, p["bloqueios_por_auditor"])
        ],
    }
    return {
        "periodo": metricas_filial.PERIODO,
        "consolidado": consolidado,
        "por_filial": paineis,
        "modelo": _modelo(avaliacao, metricas_modelo),
    }
