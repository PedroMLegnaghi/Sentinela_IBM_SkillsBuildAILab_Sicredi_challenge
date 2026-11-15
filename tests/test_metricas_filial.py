"""Testes das métricas do gerente (Issue #98): regras com dublês e a soma real das filiais."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.adaptadores.memoria import dados_demo
from src.api import rotas_filial, sessao
from src.aplicacao import associado as associado_app
from src.aplicacao import metricas_filial
from src.associado import notificacoes

RAIZ = Path(__file__).resolve().parents[1]
TEM_DADOS = (RAIZ / "data" / "transacoes_preparadas.parquet").exists()
TEM_MODELO = (RAIZ / "modelos" / "sentinela.joblib").exists()
SUSPEITA = {
    "estabelecimento": "Loja online",
    "data_hora": "2025-03-31T03:10:00",
    "valor": 500.0,
    "modalidade_transacao": "cartao_nao_presente",
}
COMUM = {**SUSPEITA, "valor": 35.0, "modalidade_transacao": "cartao_presente"}

pytest.importorskip("fastapi")


# --- Regras puras -----------------------------------------------------------------------------


def test_resumo_de_marco_conta_por_filial_decisao_e_tipo():
    linhas = [
        {
            "id_filial": "fil-centro",
            "decisao": "APROVAR",
            "valor": 10.0,
            "tipo_transacao": "debito",
            "modalidade_transacao": "cartao_presente",
        },
        {
            "id_filial": "fil-centro",
            "decisao": "BLOQUEAR",
            "valor": 90.5,
            "tipo_transacao": "credito",
            "modalidade_transacao": "cartao_nao_presente",
        },
        {
            "id_filial": "fil-norte",
            "decisao": "PEDIR_CONFIRMACAO",
            "valor": 40.0,
            "tipo_transacao": "debito",
            "modalidade_transacao": "cartao_presente",
        },
    ]

    resumos = metricas_filial.resumir_marco(linhas)

    centro = resumos["fil-centro"]
    assert (centro.aprovadas, centro.confirmacoes, centro.bloqueadas) == (1, 0, 1)
    assert centro.valor_protegido == 90.5
    assert centro.por_tipo[("credito", "cartao_nao_presente")]["bloqueadas"] == 1
    assert resumos["fil-norte"].confirmacoes == 1


def test_copiar_o_resumo_nao_altera_o_de_marco():
    original = metricas_filial.ResumoFilial()
    original.somar("APROVAR", 10.0, "debito", "cartao_presente")

    copia = original.copiar()
    copia.somar("APROVAR", 10.0, "debito", "cartao_presente")

    assert original.aprovadas == 1
    assert original.por_tipo[("debito", "cartao_presente")]["aprovadas"] == 1


# --- Rota com dublês --------------------------------------------------------------------------


def _base_inventada() -> pd.DataFrame:
    linhas = []
    numero = 0
    for indice in range(10):
        cliente = f"c{indice + 1:02d}"
        for i in range(5 if indice == 0 else 2):
            tipo = "debito" if i % 2 == 0 else "credito"
            linhas.append(
                {
                    "id_transacao": numero,
                    "data_hora": pd.Timestamp(f"2025-03-{i + 1:02d} 09:00:00"),
                    "id_cartao": f"{cliente}-{tipo}",
                    "id_cliente": cliente,
                    "valor": 20.0 * (i + 1),
                    "tipo_transacao": tipo,
                    "modalidade_transacao": "cartao_presente",
                    "risco_estabelecimento": 10.0,
                }
            )
            numero += 1
    return pd.DataFrame(linhas)


def _analise(transacao: dict) -> dict:
    decisao = "PEDIR_CONFIRMACAO" if (transacao.get("valor") or 0) >= 300 else "APROVAR"
    return {
        "nota": 50.0,
        "decisao": decisao,
        "decisao_legivel": decisao,
        "sinais": [],
        "explicacao": "x",
        "contribuicoes": [],
        "latencia_ms": 1.0,
    }


@pytest.fixture(scope="module")
def cliente():
    from fastapi.testclient import TestClient  # noqa: PLC0415

    from src.api.app import app  # noqa: PLC0415

    with TestClient(app) as cliente_teste:
        yield cliente_teste


@pytest.fixture
def ambiente(monkeypatch):
    import src.api.auditorias as auditoria_mem  # noqa: PLC0415
    import src.api.servicos as sv  # noqa: PLC0415

    monkeypatch.setattr(notificacoes, "_notificacoes", {})
    repos = dados_demo.montar_repositorios(
        _base_inventada(), {0: "APROVAR", 1: "APROVAR", 2: "APROVAR"}
    )
    associado_app.avisar_compras_de_marco(repos)
    marco = metricas_filial.ResumoFilial()
    for _ in range(3):
        marco.somar("APROVAR", 20.0, "debito", "cartao_presente")
    monkeypatch.setattr(sessao._estado, "repositorios", repos)
    monkeypatch.setattr(sessao._estado, "tokens", {})
    monkeypatch.setattr(rotas_filial, "_ids_fila", set())
    monkeypatch.setattr(rotas_filial, "_resumo_marco", {"fil-centro": marco})
    monkeypatch.setattr(sv, "modelo_carregado", lambda: True)
    monkeypatch.setattr(sv, "analisar_transacao", _analise)
    monkeypatch.setattr(auditoria_mem, "disparar_auditoria_em_segundo_plano", lambda *_: None)
    return repos


def _cabecalho(cliente, id_perfil: str) -> dict[str, str]:
    return {"X-Sessao": cliente.post("/api/sessao", json={"id_perfil": id_perfil}).json()["token"]}


def _metricas(cliente) -> dict:
    return cliente.get("/api/filial/metricas", headers=_cabecalho(cliente, "ger-01")).json()


def test_so_o_gerente_ve_as_metricas(cliente, ambiente):
    assert (
        cliente.get("/api/filial/metricas", headers=_cabecalho(cliente, "aud-01")).status_code
        == 403
    )
    assert (
        cliente.get("/api/filial/metricas", headers=_cabecalho(cliente, "asc-01")).status_code
        == 403
    )
    assert cliente.get("/api/filial/metricas").status_code == 401


def test_metricas_somam_marco_e_compras_simuladas(cliente, ambiente):
    cabecalho = _cabecalho(cliente, "asc-01")
    cliente.post("/api/associado/compras", json={"cartao": "car-01-d", **COMUM}, headers=cabecalho)
    cliente.post(
        "/api/associado/compras", json={"cartao": "car-01-c", **SUSPEITA}, headers=cabecalho
    )

    corpo = _metricas(cliente)

    assert corpo["periodo"] == "2025-03"
    assert corpo["totais"] == {
        "compras": 5,
        "aprovadas": 4,
        "confirmacoes": 1,
        "bloqueadas": 0,
        "valor_protegido": 0.0,
    }
    assert {
        "tipo_transacao": "credito",
        "modalidade_transacao": "cartao_nao_presente",
        "aprovadas": 0,
        "confirmacoes": 1,
        "bloqueadas": 0,
    } in corpo["por_tipo"]


def test_nao_fui_eu_soma_um_alerta_certo_e_mede_o_tempo(cliente, ambiente):
    cabecalho = _cabecalho(cliente, "asc-01")
    antes = _metricas(cliente)["acerto_modelo"]
    compra = cliente.post(
        "/api/associado/compras", json={"cartao": "car-01-c", **SUSPEITA}, headers=cabecalho
    ).json()["compra"]

    cliente.post(f"/api/notificacoes/{compra['id_notificacao']}/resposta", json={"resposta": "nao"})
    depois = _metricas(cliente)

    assert depois["acerto_modelo"]["alertas_certos"] == antes["alertas_certos"] + 1
    assert depois["acerto_modelo"]["taxa"] == 100.0
    assert depois["tempo_resposta_mediano_s"] is not None


def test_fui_eu_conta_como_alerta_desnecessario(cliente, ambiente):
    cabecalho = _cabecalho(cliente, "asc-01")
    compra = cliente.post(
        "/api/associado/compras", json={"cartao": "car-01-c", **SUSPEITA}, headers=cabecalho
    ).json()["compra"]

    cliente.post(f"/api/notificacoes/{compra['id_notificacao']}/resposta", json={"resposta": "sim"})
    acerto = _metricas(cliente)["acerto_modelo"]

    assert (acerto["alertas_certos"], acerto["alertas_desnecessarios"], acerto["taxa"]) == (
        0,
        1,
        0.0,
    )


def test_contestacao_entra_em_fraudes_aprovadas(cliente, ambiente):
    cabecalho = _cabecalho(cliente, "asc-01")
    antes = _metricas(cliente)["fraudes_aprovadas"]["total"]
    compra = cliente.post(
        "/api/associado/compras", json={"cartao": "car-01-d", **COMUM}, headers=cabecalho
    ).json()["compra"]

    cliente.post(f"/api/associado/compras/{compra['id_compra']}/contestacao", headers=cabecalho)
    fraudes = _metricas(cliente)["fraudes_aprovadas"]

    assert fraudes["total"] == antes + 1
    assert fraudes["itens"][-1] == {
        "associado": "Ana S.",
        "final_cartao": "1111",
        "data_hora": "2025-03-31T03:10:00",
        "valor": 35.0,
    }


def test_sem_respostas_a_taxa_e_o_tempo_sao_nulos(cliente, ambiente):
    corpo = _metricas(cliente)

    assert corpo["acerto_modelo"]["taxa"] is None
    assert corpo["tempo_resposta_mediano_s"] is None


# --- Soma real das duas filiais ---------------------------------------------------------------


@pytest.mark.skipif(not (TEM_DADOS and TEM_MODELO), reason="sem parquet ou modelo")
def test_as_duas_filiais_somadas_dao_os_numeros_da_secao_11():
    import src.api.servicos as sv  # noqa: PLC0415

    sv.inicializar()
    resumos = metricas_filial.resumir_marco(
        rotas_filial._linhas_de_marco(sessao.obter_repositorios())
    )

    soma = [
        sum(getattr(r, campo) for r in resumos.values())
        for campo in ("aprovadas", "confirmacoes", "bloqueadas")
    ]
    assert soma == [13395, 159, 54]


# --- Bloqueios por auditor (Issue #104) -------------------------------------------------------


def _compra_bloqueada_pelo_auditor(cliente, id_auditor: str = "aud-01") -> dict:
    cabecalho = _cabecalho(cliente, "asc-01")
    compra = cliente.post(
        "/api/associado/compras", json={"cartao": "car-01-c", **SUSPEITA}, headers=cabecalho
    ).json()["compra"]
    cliente.post(
        f"/api/filial/compras/{compra['id_compra']}/bloqueio",
        json={"nota": None},
        headers=_cabecalho(cliente, id_auditor),
    )
    return compra


def _por_auditor(cliente) -> dict[str, dict]:
    return {linha["auditor"]: linha for linha in _metricas(cliente)["bloqueios_por_auditor"]}


def test_cada_auditor_da_filial_aparece_com_zeros_antes_de_bloquear(cliente, ambiente):
    linhas = _por_auditor(cliente)

    assert set(linhas) == {"Rafael Moura", "Júlia Prates"}
    assert linhas["Rafael Moura"] == {
        "auditor": "Rafael Moura",
        "bloqueios": 0,
        "corretos": 0,
        "liberados_depois": 0,
    }


def test_nao_fui_eu_conta_o_bloqueio_como_correto(cliente, ambiente):
    compra = _compra_bloqueada_pelo_auditor(cliente)

    cliente.post(f"/api/notificacoes/{compra['id_notificacao']}/resposta", json={"resposta": "nao"})
    rafael = _por_auditor(cliente)["Rafael Moura"]

    assert (rafael["bloqueios"], rafael["corretos"], rafael["liberados_depois"]) == (1, 1, 0)


def test_fui_eu_conta_o_bloqueio_como_liberado_depois(cliente, ambiente):
    compra = _compra_bloqueada_pelo_auditor(cliente, "aud-02")

    cliente.post(f"/api/notificacoes/{compra['id_notificacao']}/resposta", json={"resposta": "sim"})
    linhas = _por_auditor(cliente)

    assert (linhas["Júlia Prates"]["bloqueios"], linhas["Júlia Prates"]["liberados_depois"]) == (
        1,
        1,
    )
    assert linhas["Rafael Moura"]["bloqueios"] == 0


def test_bloqueio_sem_resposta_conta_so_no_total(cliente, ambiente):
    _compra_bloqueada_pelo_auditor(cliente)

    rafael = _por_auditor(cliente)["Rafael Moura"]

    assert (rafael["bloqueios"], rafael["corretos"], rafael["liberados_depois"]) == (1, 0, 0)
