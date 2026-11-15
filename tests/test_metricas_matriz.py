"""Painel da matriz (ESPECIFICACAO, seção 17.8)."""

from src.adaptadores.memoria import dados_demo
from src.aplicacao import metricas_matriz
from src.aplicacao.metricas_filial import ResumoFilial
from src.dominio.regras import ID_FILIAL_CENTRO, ID_FILIAL_NORTE

FILIAIS = (ID_FILIAL_CENTRO, ID_FILIAL_NORTE)
AVALIACAO = {
    "periodo": "2025-03",
    "transacoes": 10,
    "fraudes_total": 2,
    "sentinela": {
        "bloqueadas": 2,
        "fraudes_bloqueadas": 2,
        "confirmacoes": 1,
        "fraudes_aprovadas": 0,
    },
}


def _resumos():
    centro, norte = ResumoFilial(), ResumoFilial()
    centro.somar("APROVAR", 10.0, "debito", "cartao_presente")
    centro.somar("BLOQUEAR", 50.0, "credito", "cartao_nao_presente")
    norte.somar("APROVAR", 20.0, "debito", "cartao_presente")
    norte.somar("PEDIR_CONFIRMACAO", 30.0, "credito", "cartao_nao_presente")
    return {ID_FILIAL_CENTRO: centro, ID_FILIAL_NORTE: norte}


def _painel(**kwargs):
    repos = dados_demo.montar_repositorios(None)
    return metricas_matriz.calcular_painel_matriz(
        repos, FILIAIS, _resumos(), lambda _id: None, **kwargs
    )


def test_consolidado_soma_as_filiais():
    painel = _painel(avaliacao=AVALIACAO)
    totais = painel["consolidado"]["totais"]

    assert totais == {
        "compras": 4,
        "aprovadas": 2,
        "confirmacoes": 1,
        "bloqueadas": 1,
        "valor_protegido": 50.0,
    }
    assert [p["filial"]["id_filial"] for p in painel["por_filial"]] == list(FILIAIS)


def test_por_tipo_junta_as_linhas_iguais_das_filiais():
    linhas = {
        (linha["tipo_transacao"], linha["modalidade_transacao"]): linha
        for linha in _painel()["consolidado"]["por_tipo"]
    }

    assert linhas[("debito", "cartao_presente")]["aprovadas"] == 2
    assert linhas[("credito", "cartao_nao_presente")]["bloqueadas"] == 1
    assert linhas[("credito", "cartao_nao_presente")]["confirmacoes"] == 1


def test_bloqueios_por_auditor_trazem_a_filial():
    itens = _painel()["consolidado"]["bloqueios_por_auditor"]

    assert {i["filial"] for i in itens} == {"Agência Centro", "Agência Norte"}
    assert len(itens) == 4


def test_modelo_vem_da_avaliacao_e_some_sem_ela():
    assert _painel(
        avaliacao=AVALIACAO, metricas_modelo={"pr_auc": 0.99, "treino": {"linhas": 8, "fraudes": 3}}
    )["modelo"] == {
        "periodo": "2025-03",
        "transacoes": 10,
        "fraudes": 2,
        "sentinela": {
            "fraudes_bloqueadas": 2,
            "bloqueadas": 2,
            "confirmacoes": 1,
            "fraudes_aprovadas": 0,
        },
        "treino": {"linhas": 8, "fraudes": 3},
        "pr_auc": 0.99,
        "roc_auc": None,
    }
    assert _painel()["modelo"] is None
