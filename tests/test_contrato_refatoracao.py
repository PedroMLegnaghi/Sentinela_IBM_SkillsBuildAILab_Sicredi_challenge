"""Contrato das rotas do associado e da filial (ESPECIFICACAO, seção 17; Issue #90).

Cada teste fica pulado até a rota existir na API. Quem implementa a rota não altera este arquivo
sem combinar com a outra trilha: ele é a régua das Issues #94, #96 e #98.
"""

from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
TEM_DADOS = (RAIZ / "data" / "transacoes_preparadas.parquet").exists()
TEM_MODELO = (RAIZ / "modelos" / "sentinela.joblib").exists()

pytestmark = pytest.mark.skipif(
    not (TEM_DADOS and TEM_MODELO), reason="sem data/transacoes_preparadas.parquet ou modelo"
)

CHAVES_PROIBIDAS = {
    "fraude",
    "feedback_label",
    "decisao_sistema_atual",
    "id_cartao",
    "id_cliente",
    "id_estabelecimento",
    "id_transacao",
}
CHAVES_PROIBIDAS_AO_ASSOCIADO = {"sinais", "nota", "contribuicoes", "analise", "auditoria"}
SITUACOES = {"APROVADA", "AGUARDANDO", "BLOQUEADA", "CONTESTADA"}
CHAVES_PERFIL = {"id_perfil", "nome", "papel", "filial"}
CHAVES_CARTAO = {"id", "tipo", "final", "bloqueado"}
CHAVES_COMPRA = {
    "id_compra",
    "estabelecimento",
    "data_hora",
    "valor",
    "tipo_transacao",
    "modalidade_transacao",
    "final_cartao",
    "situacao",
    "id_notificacao",
    "simulada",
}
CHAVES_ITEM_FILA = {
    "id_compra",
    "nota",
    "decisao",
    "associado",
    "final_cartao",
    "data_hora",
    "valor",
    "tipo_transacao",
    "modalidade_transacao",
    "situacao",
    "veredito_ia",
}
MOTIVO_GENERICO = "A compra fugiu do seu padrão de uso e foi bloqueada por segurança."

# Compra inventada de risco baixo e de risco alto (nenhum valor vem da base).
COMPRA_COMUM = {
    "estabelecimento": "Padaria Central",
    "data_hora": "2025-03-31T14:20:00",
    "valor": 35.0,
    "nao_presente": 0,
    "ip_pais_desconhecido": 0,
    "vel_cartao_terminal_1h": 0,
    "qtd_transacoes_cartao_1min": 0,
    "qtd_token_carteira_3m": 0,
    "dist_terminal_anterior_km": 1.0,
    "risco_estabelecimento": 5,
    "modalidade_transacao": "cartao_presente",
}
COMPRA_ALTO_RISCO = {
    "estabelecimento": "Loja online",
    "data_hora": "2025-03-31T03:10:00",
    "valor": 980.0,
    "nao_presente": 1,
    "ip_pais_desconhecido": 1,
    "vel_cartao_terminal_1h": 40,
    "qtd_transacoes_cartao_1min": 15,
    "qtd_token_carteira_3m": 90,
    "dist_terminal_anterior_km": 400.0,
    "risco_estabelecimento": 70,
    "modalidade_transacao": "cartao_nao_presente",
}


@pytest.fixture(scope="module")
def cliente():
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient  # noqa: PLC0415

    from src.api.app import app  # noqa: PLC0415

    with TestClient(app) as cliente_teste:
        yield cliente_teste


def _exige_rota(cliente, caminho: str) -> None:
    if caminho not in cliente.app.openapi()["paths"]:
        pytest.skip(f"rota {caminho} ainda não implementada (seção 17)")


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


def _sem_proibidas(corpo) -> None:
    proibidas = _chaves_recursivas(corpo) & CHAVES_PROIBIDAS
    assert not proibidas, f"chaves proibidas na resposta: {proibidas}"


def _perfil(cliente, papel: str, filial: str = "fil-centro") -> dict:
    perfis = cliente.get("/api/sessao/perfis").json()["perfis"]
    return next(p for p in perfis if p["papel"] == papel and p["filial"]["id_filial"] == filial)


def _cabecalho(cliente, papel: str, filial: str = "fil-centro") -> dict[str, str]:
    perfil = _perfil(cliente, papel, filial)
    token = cliente.post("/api/sessao", json={"id_perfil": perfil["id_perfil"]}).json()["token"]
    return {"X-Sessao": token}


# --- Sessão -------------------------------------------------------------------------------------


def test_perfis_e_sessao(cliente):
    _exige_rota(cliente, "/api/sessao/perfis")
    _exige_rota(cliente, "/api/sessao")

    perfis = cliente.get("/api/sessao/perfis")
    assert perfis.status_code == 200
    lista = perfis.json()["perfis"]
    assert all(set(p) == CHAVES_PERFIL for p in lista)
    papeis = [p["papel"] for p in lista]
    assert papeis.count("gerente") == 2
    assert papeis.count("auditor") == 4
    assert papeis.count("associado") == 10
    assert papeis.count("matriz") == 1  # seção 17.8
    assert {p["filial"]["id_filial"] for p in lista} == {"fil-centro", "fil-norte", "matriz"}

    sessao = cliente.post("/api/sessao", json={"id_perfil": lista[0]["id_perfil"]})
    assert sessao.status_code == 200
    assert set(sessao.json()) == {"token", "perfil"}
    assert sessao.json()["perfil"] == lista[0]

    assert cliente.post("/api/sessao", json={"id_perfil": "nao-existe"}).status_code == 404


# --- Associado ----------------------------------------------------------------------------------


def test_inicio_do_associado(cliente):
    _exige_rota(cliente, "/api/associado/inicio")
    assert cliente.get("/api/associado/inicio").status_code == 401
    assert (
        cliente.get("/api/associado/inicio", headers={"X-Sessao": "token-invalido"}).status_code
        == 401
    )
    assert (
        cliente.get("/api/associado/inicio", headers=_cabecalho(cliente, "auditor")).status_code
        == 403
    )

    resposta = cliente.get("/api/associado/inicio", headers=_cabecalho(cliente, "associado"))
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert set(corpo) == {
        "associado",
        "saldo",
        "limite_total",
        "limite_disponivel",
        "cartoes",
        "pendentes",
        "ultimas_compras",
    }
    assert {c["tipo"] for c in corpo["cartoes"]} == {"debito", "credito"}
    assert all(set(c) == CHAVES_CARTAO for c in corpo["cartoes"])
    assert len(corpo["ultimas_compras"]) <= 3
    assert all(set(c) == CHAVES_COMPRA for c in corpo["ultimas_compras"])
    _sem_proibidas(corpo)


def test_extrato_do_associado(cliente):
    _exige_rota(cliente, "/api/associado/extrato")
    cabecalho = _cabecalho(cliente, "associado")

    resposta = cliente.get("/api/associado/extrato", headers=cabecalho)
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["total"] == len(corpo["itens"]) > 0
    assert all(set(c) == CHAVES_COMPRA for c in corpo["itens"])
    assert all(c["situacao"] in SITUACOES for c in corpo["itens"])
    _sem_proibidas(corpo)
    assert not _chaves_recursivas(corpo) & CHAVES_PROIBIDAS_AO_ASSOCIADO

    filtrado = cliente.get("/api/associado/extrato?situacao=APROVADA", headers=cabecalho).json()
    assert all(c["situacao"] == "APROVADA" for c in filtrado["itens"])
    assert cliente.get("/api/associado/extrato?situacao=XYZ", headers=cabecalho).status_code == 422


def test_detalhe_da_compra_do_associado(cliente):
    _exige_rota(cliente, "/api/associado/compras/{id_compra}")
    cabecalho = _cabecalho(cliente, "associado")
    itens = cliente.get("/api/associado/extrato", headers=cabecalho).json()["itens"]

    resposta = cliente.get(f"/api/associado/compras/{itens[0]['id_compra']}", headers=cabecalho)
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert set(corpo) == CHAVES_COMPRA | {"bloqueio", "resposta_associado", "pode_contestar"}
    assert not _chaves_recursivas(corpo) & CHAVES_PROIBIDAS_AO_ASSOCIADO
    _sem_proibidas(corpo)

    outro = _cabecalho(cliente, "associado", "fil-norte")
    assert (
        cliente.get(f"/api/associado/compras/{itens[0]['id_compra']}", headers=outro).status_code
        == 404
    )


def test_simular_compra_entra_no_extrato(cliente):
    _exige_rota(cliente, "/api/associado/compras")
    cabecalho = _cabecalho(cliente, "associado")
    inicio = cliente.get("/api/associado/inicio", headers=cabecalho).json()
    debito = next(c for c in inicio["cartoes"] if c["tipo"] == "debito" and not c["bloqueado"])

    comum = cliente.post(
        "/api/associado/compras", json={"cartao": debito["id"], **COMPRA_COMUM}, headers=cabecalho
    )
    assert comum.status_code == 201
    compra = comum.json()["compra"]
    assert set(compra) == CHAVES_COMPRA
    assert compra["simulada"] is True
    assert compra["situacao"] == "APROVADA"
    depois = cliente.get("/api/associado/inicio", headers=cabecalho).json()
    assert depois["saldo"] == pytest.approx(inicio["saldo"] - COMPRA_COMUM["valor"])

    credito = next(c for c in inicio["cartoes"] if c["tipo"] == "credito")
    alto = cliente.post(
        "/api/associado/compras",
        json={"cartao": credito["id"], **COMPRA_ALTO_RISCO},
        headers=cabecalho,
    )
    assert alto.status_code == 201
    assert alto.json()["compra"]["situacao"] in {"AGUARDANDO", "BLOQUEADA"}
    assert alto.json()["id_notificacao"]
    _sem_proibidas(alto.json())

    extrato = cliente.get("/api/associado/extrato", headers=cabecalho).json()["itens"]
    ids = [c["id_compra"] for c in extrato[:2]]
    assert alto.json()["compra"]["id_compra"] in ids

    cartao_alheio = cliente.post(
        "/api/associado/compras",
        json={"cartao": "car-99-d", **COMPRA_COMUM},
        headers=cabecalho,
    )
    assert cartao_alheio.status_code == 404


def test_contestacao_bloqueia_o_cartao(cliente):
    _exige_rota(cliente, "/api/associado/compras/{id_compra}/contestacao")
    cabecalho = _cabecalho(cliente, "associado", "fil-norte")
    inicio = cliente.get("/api/associado/inicio", headers=cabecalho).json()
    debito = next(c for c in inicio["cartoes"] if c["tipo"] == "debito")
    compra = cliente.post(
        "/api/associado/compras", json={"cartao": debito["id"], **COMPRA_COMUM}, headers=cabecalho
    ).json()["compra"]
    rota = f"/api/associado/compras/{compra['id_compra']}/contestacao"

    resposta = cliente.post(rota, headers=cabecalho)
    assert resposta.status_code == 201
    assert resposta.json()["compra"]["situacao"] == "CONTESTADA"
    assert resposta.json()["cartao"]["bloqueado"] is True
    assert cliente.post(rota, headers=cabecalho).status_code == 409

    nova = cliente.post(
        "/api/associado/compras", json={"cartao": debito["id"], **COMPRA_COMUM}, headers=cabecalho
    )
    assert nova.status_code == 409


def test_motivo_generico_para_o_associado(cliente):
    _exige_rota(cliente, "/api/associado/compras")
    cabecalho = _cabecalho(cliente, "associado")
    credito = next(
        c
        for c in cliente.get("/api/associado/inicio", headers=cabecalho).json()["cartoes"]
        if c["tipo"] == "credito"
    )
    compra = cliente.post(
        "/api/associado/compras",
        json={"cartao": credito["id"], **COMPRA_ALTO_RISCO},
        headers=cabecalho,
    ).json()["compra"]
    if compra["situacao"] != "BLOQUEADA":
        pytest.skip("a compra de alto risco não foi bloqueada")
    detalhe = cliente.get(f"/api/associado/compras/{compra['id_compra']}", headers=cabecalho)
    assert detalhe.json()["bloqueio"]["motivo"] == MOTIVO_GENERICO
    assert detalhe.json()["bloqueio"]["por"] == "Sentinela"


# --- Filial -------------------------------------------------------------------------------------


def test_fila_da_filial(cliente):
    _exige_rota(cliente, "/api/filial/fila")
    assert (
        cliente.get("/api/filial/fila", headers=_cabecalho(cliente, "associado")).status_code == 403
    )

    centro = cliente.get("/api/filial/fila", headers=_cabecalho(cliente, "auditor"))
    norte = cliente.get("/api/filial/fila", headers=_cabecalho(cliente, "auditor", "fil-norte"))
    assert centro.status_code == norte.status_code == 200
    corpo = centro.json()
    assert set(corpo) == {"filial", "total", "itens"}
    assert corpo["filial"]["id_filial"] == "fil-centro"
    assert all(set(i) == CHAVES_ITEM_FILA for i in corpo["itens"])
    notas = [i["nota"] for i in corpo["itens"]]
    assert notas == sorted(notas, reverse=True)
    ids_centro = {i["id_compra"] for i in corpo["itens"]}
    ids_norte = {i["id_compra"] for i in norte.json()["itens"]}
    assert not ids_centro & ids_norte
    _sem_proibidas(corpo)


def test_compra_na_filial_respeita_a_lgpd(cliente):
    _exige_rota(cliente, "/api/filial/compras/{id_compra}")
    cabecalho = _cabecalho(cliente, "auditor")
    item = cliente.get("/api/filial/fila", headers=cabecalho).json()["itens"][0]

    resposta = cliente.get(f"/api/filial/compras/{item['id_compra']}", headers=cabecalho)
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert set(corpo) == {
        "compra",
        "analise",
        "auditoria",
        "associado",
        "resposta_associado",
        "bloqueio",
    }
    assert set(corpo["associado"]) == {"nome_abreviado", "final_cartao", "historico"}
    proibidas_lgpd = {"saldo", "limite_total", "limite_disponivel", "extrato"}
    assert not _chaves_recursivas(corpo) & proibidas_lgpd
    _sem_proibidas(corpo)

    outra = _cabecalho(cliente, "auditor", "fil-norte")
    assert cliente.get(f"/api/filial/compras/{item['id_compra']}", headers=outra).status_code == 403


def test_metricas_da_filial(cliente):
    _exige_rota(cliente, "/api/filial/metricas")
    assert (
        cliente.get("/api/filial/metricas", headers=_cabecalho(cliente, "auditor")).status_code
        == 403
    )

    resposta = cliente.get("/api/filial/metricas", headers=_cabecalho(cliente, "gerente"))
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert set(corpo) == {
        "filial",
        "periodo",
        "totais",
        "por_tipo",
        "acerto_modelo",
        "fraudes_aprovadas",
        "tempo_resposta_mediano_s",
        "bloqueios_por_auditor",  # seção 17.5 (Issue #104)
    }
    totais = corpo["totais"]
    assert totais["aprovadas"] + totais["confirmacoes"] + totais["bloqueadas"] == totais["compras"]
    assert set(corpo["acerto_modelo"]) == {
        "alertas_certos",
        "alertas_desnecessarios",
        "sem_resposta",
        "taxa",
    }
    _sem_proibidas(corpo)


# --- Matriz (seção 17.8) ------------------------------------------------------------------------


def test_metricas_da_matriz(cliente):
    _exige_rota(cliente, "/api/matriz/metricas")
    for papel in ("gerente", "auditor", "associado"):
        assert (
            cliente.get("/api/matriz/metricas", headers=_cabecalho(cliente, papel)).status_code
            == 403
        )

    resposta = cliente.get("/api/matriz/metricas", headers=_cabecalho(cliente, "matriz", "matriz"))
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert set(corpo) == {"periodo", "consolidado", "por_filial", "modelo"}
    assert {p["filial"]["id_filial"] for p in corpo["por_filial"]} == {"fil-centro", "fil-norte"}
    totais = corpo["consolidado"]["totais"]
    for campo in ("compras", "aprovadas", "confirmacoes", "bloqueadas"):
        assert totais[campo] == sum(p["totais"][campo] for p in corpo["por_filial"])
    assert corpo["modelo"]["transacoes"] == 13608
    assert corpo["modelo"]["sentinela"]["fraudes_bloqueadas"] == 54
    assert corpo["modelo"]["sistema_atual"]["fraudes_bloqueadas"] == 26
    _sem_proibidas(corpo)
