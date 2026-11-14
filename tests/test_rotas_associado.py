"""Testes das rotas do associado (Issue #94) sem ``data/`` nem modelo: tudo por dublês."""

from __future__ import annotations

import pandas as pd
import pytest

from src.adaptadores.memoria import dados_demo
from src.api import sessao
from src.aplicacao import associado as associado_app
from src.associado import notificacoes

CHAVES_PROIBIDAS = {"id_cartao", "id_cliente", "id_estabelecimento", "id_transacao", "fraude"}
CHAVES_TECNICAS = {"sinais", "nota", "contribuicoes", "analise", "auditoria"}
COMUM = {
    "estabelecimento": "Padaria Central",
    "data_hora": "2025-03-31T14:20:00",
    "valor": 35.0,
    "modalidade_transacao": "cartao_presente",
}
SUSPEITA = {**COMUM, "valor": 500.0, "data_hora": "2025-03-31T03:10:00"}
ALTO_RISCO = {**COMUM, "valor": 980.0, "modalidade_transacao": "cartao_nao_presente"}
LIMITE_SUSPEITA = 300.0
LIMITE_BLOQUEIO = 900.0

pytest.importorskip("fastapi")


def _base_inventada() -> pd.DataFrame:
    """Dez clientes de março; 'c01' é o maior e vira a Ana (asc-01)."""
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


def _analisar_falso(transacao: dict) -> dict:
    """Decide pelo valor, para o teste não depender do modelo."""
    valor = transacao.get("valor") or 0.0
    if valor >= LIMITE_BLOQUEIO:
        decisao = "BLOQUEAR"
    elif valor >= LIMITE_SUSPEITA:
        decisao = "PEDIR_CONFIRMACAO"
    else:
        decisao = "APROVAR"
    return {
        "nota": 10.0,
        "decisao": decisao,
        "decisao_legivel": decisao,
        "sinais": [],
        "explicacao": "Explicação técnica que o associado não pode ver.",
        "contribuicoes": [],
        "latencia_ms": 1.0,
    }


def _chaves_recursivas(valor) -> set[str]:
    if isinstance(valor, dict):
        chaves = set(valor)
        for item in valor.values():
            chaves |= _chaves_recursivas(item)
        return chaves
    if isinstance(valor, list):
        chaves: set[str] = set()
        for item in valor:
            chaves |= _chaves_recursivas(item)
        return chaves
    return set()


@pytest.fixture(scope="module")
def cliente():
    from fastapi.testclient import TestClient  # noqa: PLC0415

    from src.api.app import app  # noqa: PLC0415

    with TestClient(app) as cliente_teste:
        yield cliente_teste


@pytest.fixture(autouse=True)
def ambiente(monkeypatch):
    """Repositórios inventados, modelo falso e auditoria desligada, a cada teste."""
    import src.api.auditorias as auditoria_mem  # noqa: PLC0415
    import src.api.servicos as sv  # noqa: PLC0415

    # c01: transações 0..4 → BLOQUEADA, AGUARDANDO, APROVADA, APROVADA, APROVADA
    decisoes = {0: "BLOQUEAR", 1: "PEDIR_CONFIRMACAO", 2: "APROVAR", 3: "APROVAR", 4: "APROVAR"}
    monkeypatch.setattr(notificacoes, "_notificacoes", {})
    repos = dados_demo.montar_repositorios(_base_inventada(), decisoes)
    associado_app.avisar_compras_de_marco(repos)
    monkeypatch.setattr(sessao._estado, "repositorios", repos)
    monkeypatch.setattr(sessao._estado, "tokens", {})
    monkeypatch.setattr(sv, "modelo_carregado", lambda: True)
    monkeypatch.setattr(sv, "analisar_transacao", _analisar_falso)
    monkeypatch.setattr(auditoria_mem, "disparar_auditoria_em_segundo_plano", lambda *_: None)
    return repos


def _cabecalho(cliente, id_perfil: str = "asc-01") -> dict[str, str]:
    token = cliente.post("/api/sessao", json={"id_perfil": id_perfil}).json()["token"]
    return {"X-Sessao": token}


def _cartao(cliente, cabecalho, tipo: str) -> str:
    cartoes = cliente.get("/api/associado/inicio", headers=cabecalho).json()["cartoes"]
    return next(c["id"] for c in cartoes if c["tipo"] == tipo)


# --- Sessão -----------------------------------------------------------------------------------


def test_perfis_listam_dezesseis_e_sessao_devolve_token(cliente):
    perfis = cliente.get("/api/sessao/perfis").json()["perfis"]
    sessao_aberta = cliente.post("/api/sessao", json={"id_perfil": "asc-01"})

    assert len(perfis) == 16
    assert sessao_aberta.status_code == 200
    assert sessao_aberta.json()["perfil"]["filial"] == {
        "id_filial": "fil-centro",
        "nome": "Agência Centro",
    }
    assert cliente.post("/api/sessao", json={"id_perfil": "ninguem"}).status_code == 404


def test_sem_sessao_401_e_com_papel_errado_403(cliente):
    assert cliente.get("/api/associado/inicio").status_code == 401
    assert cliente.get("/api/associado/inicio", headers={"X-Sessao": "x"}).status_code == 401
    assert (
        cliente.get("/api/associado/inicio", headers=_cabecalho(cliente, "aud-01")).status_code
        == 403
    )


# --- Início e extrato -------------------------------------------------------------------------


def test_inicio_traz_saldo_cartoes_pendentes_e_ultimas_compras(cliente):
    corpo = cliente.get("/api/associado/inicio", headers=_cabecalho(cliente)).json()

    assert corpo["associado"] == {"nome": "Ana Souza", "filial": "Agência Centro"}
    assert corpo["saldo"] == 4820.35
    assert {c["tipo"] for c in corpo["cartoes"]} == {"debito", "credito"}
    assert len(corpo["ultimas_compras"]) == 3
    assert [p["id_compra"] for p in corpo["pendentes"]] == ["cmp-000002"]
    assert not _chaves_recursivas(corpo) & (CHAVES_PROIBIDAS | CHAVES_TECNICAS)


def test_extrato_vem_da_mais_recente_e_aceita_filtro(cliente):
    cabecalho = _cabecalho(cliente)

    extrato = cliente.get("/api/associado/extrato", headers=cabecalho).json()
    aprovadas = cliente.get("/api/associado/extrato?situacao=APROVADA", headers=cabecalho).json()

    assert extrato["total"] == 5
    assert [c["data_hora"][:10] for c in extrato["itens"]][:2] == ["2025-03-05", "2025-03-04"]
    assert aprovadas["total"] == 3
    assert extrato["itens"][0]["final_cartao"] == "1111"
    assert cliente.get("/api/associado/extrato?situacao=XYZ", headers=cabecalho).status_code == 422


def test_detalhe_mostra_motivo_generico_e_esconde_compra_de_outro_associado(cliente):
    cabecalho = _cabecalho(cliente)

    bloqueada = cliente.get("/api/associado/compras/cmp-000001", headers=cabecalho).json()
    alheia = cliente.get("/api/associado/compras/cmp-000001", headers=_cabecalho(cliente, "asc-02"))

    assert bloqueada["situacao"] == "BLOQUEADA"
    assert bloqueada["bloqueio"]["por"] == "Sentinela"
    assert bloqueada["bloqueio"]["motivo"] == associado_app.MOTIVO_GENERICO
    assert bloqueada["pode_contestar"] is False
    assert alheia.status_code == 404
    assert cliente.get("/api/associado/compras/cmp-999999", headers=cabecalho).status_code == 404


# --- Simular compra ---------------------------------------------------------------------------


def test_compra_aprovada_no_debito_desconta_o_saldo_e_entra_no_extrato(cliente):
    cabecalho = _cabecalho(cliente)
    debito = _cartao(cliente, cabecalho, "debito")

    resposta = cliente.post(
        "/api/associado/compras", json={"cartao": debito, **COMUM}, headers=cabecalho
    )
    inicio = cliente.get("/api/associado/inicio", headers=cabecalho).json()
    extrato = cliente.get("/api/associado/extrato", headers=cabecalho).json()

    assert resposta.status_code == 201
    assert resposta.json()["compra"]["situacao"] == "APROVADA"
    assert resposta.json()["compra"]["simulada"] is True
    assert resposta.json()["id_notificacao"] is None
    assert inicio["saldo"] == pytest.approx(4820.35 - 35.0)
    assert extrato["itens"][0]["id_compra"] == resposta.json()["compra"]["id_compra"]


def test_compra_aprovada_no_credito_consome_o_limite(cliente):
    cabecalho = _cabecalho(cliente)
    credito = _cartao(cliente, cabecalho, "credito")

    cliente.post("/api/associado/compras", json={"cartao": credito, **COMUM}, headers=cabecalho)
    inicio = cliente.get("/api/associado/inicio", headers=cabecalho).json()

    assert inicio["limite_disponivel"] == pytest.approx(2150.0 - 35.0)
    assert inicio["saldo"] == 4820.35


def test_compra_bloqueada_gera_aviso_e_bloqueio_generico_sem_mexer_no_saldo(cliente):
    cabecalho = _cabecalho(cliente)
    credito = _cartao(cliente, cabecalho, "credito")

    resposta = cliente.post(
        "/api/associado/compras", json={"cartao": credito, **ALTO_RISCO}, headers=cabecalho
    )
    compra = resposta.json()["compra"]
    detalhe = cliente.get(f"/api/associado/compras/{compra['id_compra']}", headers=cabecalho).json()
    inicio = cliente.get("/api/associado/inicio", headers=cabecalho).json()

    assert compra["situacao"] == "BLOQUEADA"
    assert resposta.json()["id_notificacao"] == compra["id_notificacao"]
    assert notificacoes.obter(compra["id_notificacao"])["tipo"] == "AVISO_BLOQUEIO"
    assert detalhe["bloqueio"] == {
        "por": "Sentinela",
        "em": detalhe["bloqueio"]["em"],
        "motivo": associado_app.MOTIVO_GENERICO,
    }
    assert inicio["limite_disponivel"] == 2150.0


def test_hora_e_madrugada_vem_da_data_e_credito_do_cartao(cliente, monkeypatch):
    import src.api.servicos as sv  # noqa: PLC0415

    recebidas: list[dict] = []
    monkeypatch.setattr(
        sv, "analisar_transacao", lambda t: recebidas.append(t) or _analisar_falso(t)
    )
    cabecalho = _cabecalho(cliente)

    cliente.post(
        "/api/associado/compras",
        json={"cartao": _cartao(cliente, cabecalho, "credito"), **SUSPEITA},
        headers=cabecalho,
    )

    assert recebidas[0]["hora"] == 3.0
    assert recebidas[0]["madrugada"] == 1
    assert recebidas[0]["credito"] == 1
    assert recebidas[0]["tipo_transacao"] == "credito"
    assert recebidas[0]["nao_presente"] == 0
    assert "id_cartao" not in recebidas[0]


def test_cartao_alheio_404_data_invalida_422_e_estabelecimento_longo_422(cliente):
    cabecalho = _cabecalho(cliente)

    assert (
        cliente.post(
            "/api/associado/compras", json={"cartao": "car-02-d", **COMUM}, headers=cabecalho
        ).status_code
        == 404
    )
    invalida = {"cartao": "car-01-d", **COMUM, "data_hora": "ontem"}
    assert (
        cliente.post("/api/associado/compras", json=invalida, headers=cabecalho).status_code == 422
    )
    longo = {"cartao": "car-01-d", **COMUM, "estabelecimento": "x" * 61}
    assert cliente.post("/api/associado/compras", json=longo, headers=cabecalho).status_code == 422


# --- Resposta ao aviso ------------------------------------------------------------------------


def test_fui_eu_numa_compra_aguardando_aprova_e_aplica_o_saldo_uma_vez(cliente):
    cabecalho = _cabecalho(cliente)
    debito = _cartao(cliente, cabecalho, "debito")
    compra = cliente.post(
        "/api/associado/compras", json={"cartao": debito, **SUSPEITA}, headers=cabecalho
    ).json()["compra"]
    assert compra["situacao"] == "AGUARDANDO"
    rota = f"/api/notificacoes/{compra['id_notificacao']}/resposta"

    primeira = cliente.post(rota, json={"resposta": "sim"})
    repetida = cliente.post(rota, json={"resposta": "sim"})
    detalhe = cliente.get(f"/api/associado/compras/{compra['id_compra']}", headers=cabecalho).json()
    inicio = cliente.get("/api/associado/inicio", headers=cabecalho).json()

    assert primeira.status_code == 200
    assert repetida.status_code == 409
    assert detalhe["situacao"] == "APROVADA"
    assert detalhe["resposta_associado"]["resposta"] == "sim"
    assert inicio["saldo"] == pytest.approx(4820.35 - 500.0)
    assert inicio["pendentes"] == [
        p for p in inicio["pendentes"] if p["id_compra"] != compra["id_compra"]
    ]


def test_nao_fui_eu_bloqueia_a_compra_sem_mexer_no_saldo(cliente):
    cabecalho = _cabecalho(cliente)
    debito = _cartao(cliente, cabecalho, "debito")
    compra = cliente.post(
        "/api/associado/compras", json={"cartao": debito, **SUSPEITA}, headers=cabecalho
    ).json()["compra"]

    cliente.post(f"/api/notificacoes/{compra['id_notificacao']}/resposta", json={"resposta": "nao"})
    detalhe = cliente.get(f"/api/associado/compras/{compra['id_compra']}", headers=cabecalho).json()

    assert detalhe["situacao"] == "BLOQUEADA"
    assert detalhe["bloqueio"]["motivo"] == associado_app.MOTIVO_GENERICO
    assert cliente.get("/api/associado/inicio", headers=cabecalho).json()["saldo"] == 4820.35


# --- Contestação ------------------------------------------------------------------------------


def test_contestacao_bloqueia_o_cartao_devolve_o_valor_e_impede_compra_nova(cliente):
    cabecalho = _cabecalho(cliente)
    debito = _cartao(cliente, cabecalho, "debito")
    compra = cliente.post(
        "/api/associado/compras", json={"cartao": debito, **COMUM}, headers=cabecalho
    ).json()["compra"]
    rota = f"/api/associado/compras/{compra['id_compra']}/contestacao"

    contestada = cliente.post(rota, headers=cabecalho)
    repetida = cliente.post(rota, headers=cabecalho)
    nova = cliente.post(
        "/api/associado/compras", json={"cartao": debito, **COMUM}, headers=cabecalho
    )
    inicio = cliente.get("/api/associado/inicio", headers=cabecalho).json()

    assert contestada.status_code == 201
    assert contestada.json()["compra"]["situacao"] == "CONTESTADA"
    assert contestada.json()["cartao"] == {
        "id": debito,
        "tipo": "debito",
        "final": "1111",
        "bloqueado": True,
    }
    assert repetida.status_code == 409
    assert nova.status_code == 409
    assert inicio["saldo"] == 4820.35


def test_contestar_compra_de_marco_devolve_o_valor_ao_saldo(cliente):
    cabecalho = _cabecalho(cliente)
    aprovada = cliente.get("/api/associado/extrato?situacao=APROVADA", headers=cabecalho).json()[
        "itens"
    ][0]

    resposta = cliente.post(
        f"/api/associado/compras/{aprovada['id_compra']}/contestacao", headers=cabecalho
    )
    inicio = cliente.get("/api/associado/inicio", headers=cabecalho).json()

    assert resposta.status_code == 201
    assert inicio["saldo"] == pytest.approx(4820.35 + aprovada["valor"])


def test_compra_aguardando_nao_pode_ser_contestada(cliente):
    cabecalho = _cabecalho(cliente)

    assert (
        cliente.post("/api/associado/compras/cmp-000002/contestacao", headers=cabecalho).status_code
        == 409
    )
    assert (
        cliente.post(
            "/api/associado/compras/cmp-000001/contestacao", headers=_cabecalho(cliente, "asc-02")
        ).status_code
        == 404
    )
