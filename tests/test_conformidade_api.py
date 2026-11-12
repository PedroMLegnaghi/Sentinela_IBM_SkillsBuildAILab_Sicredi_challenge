"""Testes de conformidade da API (ESPECIFICACAO, seções 12 e 13). Arquivo do líder.

O IBM Bob não pode editar, apagar ou renomear este arquivo (AGENTS.md, seção 12).

Grupos e quando rodam:
- Todos: só depois da Issue #38 (existe src/api/app.py) e com fastapi instalado
  (requirements-api.txt).
- Análise: precisam de modelos/sentinela.joblib.
- Fila, transação, respostas e métricas: precisam também de data/transacoes_preparadas.parquet.
- Auditoria concluída: só depois da Issue #39 (existe src/auditoria/__init__.py).
"""

from __future__ import annotations

import math
import re
import shutil
import time
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
TEM_API = (RAIZ / "src" / "api" / "app.py").exists()
TEM_AUDITORIA = (RAIZ / "src" / "auditoria" / "__init__.py").exists()
TEM_MODELO = (RAIZ / "modelos" / "sentinela.joblib").exists()
TEM_DADOS = (RAIZ / "data" / "transacoes_preparadas.parquet").exists()

pytestmark = pytest.mark.skipif(not TEM_API, reason="Issue #38 ainda não implementada")

precisa_modelo = pytest.mark.skipif(not TEM_MODELO, reason="sem modelos/sentinela.joblib")
precisa_dados = pytest.mark.skipif(
    not (TEM_MODELO and TEM_DADOS), reason="sem data/transacoes_preparadas.parquet ou modelo"
)
precisa_auditoria = pytest.mark.skipif(not TEM_AUDITORIA, reason="Issue #39 ainda não implementada")

DECISOES = {"APROVAR", "PEDIR_CONFIRMACAO", "BLOQUEAR"}
CHAVES_PROIBIDAS = {
    "fraude",
    "decisao_sistema_atual",
    "id_cartao",
    "id_cliente",
    "id_estabelecimento",
}
CHAVES_ANALISE = {
    "nota",
    "decisao",
    "decisao_legivel",
    "sinais",
    "explicacao",
    "contribuicoes",
    "latencia_ms",
}
CHAVES_ITEM_FILA = {
    "id_transacao",
    "nota",
    "decisao",
    "valor",
    "data_hora",
    "tipo_transacao",
    "modalidade_transacao",
    "n_sinais",
}
CHAVES_RELATORIO = {
    "parecer",
    "risco_ia",
    "confianca",
    "explicacao",
    "evidencias_a_favor",
    "evidencias_contra",
    "dados_ausentes",
    "ferramentas_usadas",
    "fonte",
    "modelo",
}
RISCO_PARA_DECISAO = {"ALTO": "BLOQUEAR", "SUSPEITO": "PEDIR_CONFIRMACAO", "BAIXO": "APROVAR"}

# Transação inventada, de risco alto (nenhum valor vem da base).
TRANSACAO_ALTO_RISCO = {
    "valor": 980.0,
    "hora": 3,
    "madrugada": 1,
    "credito": 1,
    "nao_presente": 1,
    "ip_pais_desconhecido": 1,
    "vel_cartao_terminal_1h": 40,
    "qtd_transacoes_cartao_1min": 15,
    "qtd_token_carteira_3m": 90,
    "dist_terminal_anterior_km": 400.0,
    "risco_estabelecimento": 70,
}


@pytest.fixture(scope="module")
def cliente():
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient  # noqa: PLC0415
    from src.api.app import app  # noqa: PLC0415

    with TestClient(app) as cliente_teste:
        yield cliente_teste


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


def _sem_nan(valor) -> bool:
    if isinstance(valor, float):
        return not math.isnan(valor) and not math.isinf(valor)
    if isinstance(valor, dict):
        return all(_sem_nan(item) for item in valor.values())
    if isinstance(valor, list):
        return all(_sem_nan(item) for item in valor)
    return True


def _confere_analise(analise: dict) -> None:
    assert set(analise) == CHAVES_ANALISE, f"Campos da Analise: {sorted(analise)}. Seção 12.1."
    assert 0 <= analise["nota"] <= 100
    assert analise["decisao"] in DECISOES
    assert all(set(sinal) == {"id", "descricao"} for sinal in analise["sinais"])
    assert isinstance(analise["contribuicoes"], list)
    assert analise["latencia_ms"] >= 0


# --- Requisitos e estrutura -------------------------------------------------------------------


def test_requirements_api_tem_fastapi_uvicorn_e_httpx_fixados():
    caminho = RAIZ / "requirements-api.txt"
    assert caminho.exists(), "Falta requirements-api.txt. ESPECIFICACAO, seção 12."
    linhas = [
        linha.strip()
        for linha in caminho.read_text(encoding="utf-8").splitlines()
        if linha.strip() and not linha.startswith("#")
    ]
    nomes = {re.split(r"[=<>~!\[ ]", linha)[0].lower() for linha in linhas}
    sem_versao = [linha for linha in linhas if not re.fullmatch(r"[A-Za-z0-9_.\-]+==[\w.]+", linha)]

    assert {"fastapi", "uvicorn", "httpx"} <= nomes, f"Faltam bibliotecas: {sorted(nomes)}"
    assert not sem_versao, f"Versão não fixada com ==: {sem_versao}"


def test_config_libera_cors_so_para_o_site_local():
    from src import config  # noqa: PLC0415

    assert config.API_ORIGENS_PERMITIDAS == ["http://localhost:3000"]


def test_env_example_lista_as_credenciais_sem_valores_secretos():
    caminho = RAIZ / ".env.example"
    assert caminho.exists(), "Falta .env.example. ESPECIFICACAO, seção 13."
    texto = caminho.read_text(encoding="utf-8")

    for nome in ("WATSONX_APIKEY", "WATSONX_PROJECT_ID", "WATSONX_URL", "WATSONX_MODELO"):
        assert f"{nome}=" in texto
    assert re.search(r"^WATSONX_APIKEY=\s*$", texto, flags=re.MULTILINE)
    assert re.search(r"^WATSONX_PROJECT_ID=\s*$", texto, flags=re.MULTILINE)


def test_env_fica_fora_do_git():
    linhas = (RAIZ / ".gitignore").read_text(encoding="utf-8").splitlines()

    assert ".env" in [linha.strip() for linha in linhas]


@pytest.mark.parametrize(
    ("caminho", "metodo"),
    [
        ("/api/saude", "get"),
        ("/api/fila", "get"),
        ("/api/transacoes/{id_transacao}", "get"),
        ("/api/analisar", "post"),
        ("/api/transacoes/{id_transacao}/auditoria", "post"),
        ("/api/auditorias/{id_auditoria}", "get"),
        ("/api/respostas", "post"),
        ("/api/respostas", "get"),
        ("/api/metricas", "get"),
    ],
)
def test_rota_do_contrato_existe(cliente, caminho, metodo):
    caminhos = cliente.app.openapi()["paths"]

    assert caminho in caminhos, f"Falta a rota {caminho}. ESPECIFICACAO, seção 12.2."
    assert metodo in caminhos[caminho], f"Falta {metodo.upper()} {caminho}."


# --- Saúde, CORS e erros ----------------------------------------------------------------------


def test_saude_responde_com_os_campos_do_contrato(cliente):
    resposta = cliente.get("/api/saude")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert set(corpo) == {"status", "modelo_carregado", "dados_carregados", "auditoria"}
    assert corpo["status"] == "ok"
    assert isinstance(corpo["modelo_carregado"], bool)
    assert isinstance(corpo["dados_carregados"], bool)
    assert corpo["auditoria"] in {"watsonx", "local"}


def test_cors_aceita_o_site_local(cliente):
    resposta = cliente.get("/api/saude", headers={"Origin": "http://localhost:3000"})

    assert resposta.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_cors_recusa_outra_origem(cliente):
    resposta = cliente.get("/api/saude", headers={"Origin": "http://exemplo.invalid"})

    assert resposta.headers.get("access-control-allow-origin") is None


def test_auditoria_desconhecida_devolve_404_em_portugues(cliente):
    resposta = cliente.get("/api/auditorias/nao-existe")

    assert resposta.status_code == 404
    assert isinstance(resposta.json()["detail"], str)


def test_analisar_recusa_numero_invalido_com_422(cliente):
    resposta = cliente.post("/api/analisar", json={"valor": "muito", "auditar": False})

    assert resposta.status_code == 422


# --- Análise imediata (precisa do modelo) -----------------------------------------------------


@precisa_modelo
def test_analisar_devolve_a_mesma_decisao_do_agente(cliente):
    from src.agente import AgenteSentinela  # noqa: PLC0415

    esperado = AgenteSentinela().analisar(dict(TRANSACAO_ALTO_RISCO), usar_llm=False)

    resposta = cliente.post("/api/analisar", json={**TRANSACAO_ALTO_RISCO, "auditar": False})

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert set(corpo) == {"analise", "id_auditoria"}
    _confere_analise(corpo["analise"])
    assert corpo["analise"]["nota"] == esperado["nota"]
    assert corpo["analise"]["decisao"] == esperado["decisao"]
    assert corpo["analise"]["decisao_legivel"] == esperado["decisao_legivel"]
    assert corpo["analise"]["sinais"] == esperado["sinais"]
    assert corpo["analise"]["explicacao"] == esperado["explicacao"]
    assert corpo["id_auditoria"] is None


@precisa_modelo
def test_analisar_aceita_transacao_vazia_sem_quebrar(cliente):
    resposta = cliente.post("/api/analisar", json={"auditar": False})

    assert resposta.status_code == 200
    _confere_analise(resposta.json()["analise"])


@precisa_modelo
def test_analisar_com_auditoria_responde_sem_esperar_a_ia(cliente):
    resposta = cliente.post("/api/analisar", json={**TRANSACAO_ALTO_RISCO, "auditar": True})

    assert resposta.status_code == 200
    id_auditoria = resposta.json()["id_auditoria"]
    assert isinstance(id_auditoria, str) and id_auditoria
    auditoria = cliente.get(f"/api/auditorias/{id_auditoria}").json()
    assert auditoria["status"] in {"pendente", "concluida", "erro"}


@precisa_modelo
@precisa_auditoria
def test_auditoria_conclui_com_relatorio_valido_e_parecer_coerente(cliente, monkeypatch):
    for nome in ("WATSONX_APIKEY", "WATSONX_PROJECT_ID"):
        monkeypatch.delenv(nome, raising=False)
    corpo = cliente.post("/api/analisar", json={**TRANSACAO_ALTO_RISCO, "auditar": True}).json()
    id_auditoria = corpo["id_auditoria"]

    auditoria = {}
    for _ in range(60):
        auditoria = cliente.get(f"/api/auditorias/{id_auditoria}").json()
        if auditoria["status"] != "pendente":
            break
        time.sleep(0.5)

    assert set(auditoria) == {"id_auditoria", "status", "relatorio", "latencia_ms", "mensagem"}
    assert auditoria["status"] == "concluida"
    relatorio = auditoria["relatorio"]
    assert set(relatorio) == CHAVES_RELATORIO, f"Campos do Relatorio: {sorted(relatorio)}"
    assert relatorio["fonte"] in {"watsonx", "local"}
    assert relatorio["confianca"] in {"BAIXA", "MEDIA", "ALTA"}
    assert len(relatorio["explicacao"]) <= 600
    if relatorio["risco_ia"] is None or relatorio["confianca"] == "BAIXA":
        esperado = "INCONCLUSIVO"
    elif RISCO_PARA_DECISAO[relatorio["risco_ia"]] == corpo["analise"]["decisao"]:
        esperado = "CONFIRMA"
    else:
        esperado = "DIVERGE"
    assert relatorio["parecer"] == esperado, "Parecer fora da regra da ESPECIFICACAO, seção 13."


@precisa_auditoria
def test_auditoria_local_classifica_pela_regra_dos_sinais():
    from src.auditoria import auditar  # noqa: PLC0415

    analise = {"nota": 99.0, "decisao": "BLOQUEAR", "sinais": [{"id": "ip", "descricao": "x"}]}
    relatorio = auditar(dict(TRANSACAO_ALTO_RISCO), analise)

    if relatorio["fonte"] == "local":
        assert relatorio["risco_ia"] == "ALTO"
        assert relatorio["confianca"] == "MEDIA"


# --- Fila, transação, respostas e métricas (precisam dos dados) -------------------------------


@precisa_dados
def test_fila_padrao_tem_as_contagens_da_fila_de_demonstracao(cliente):
    resposta = cliente.get("/api/fila")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["total_fila"] == 2054
    assert corpo["contagens"] == {"BLOQUEAR": 54, "PEDIR_CONFIRMACAO": 25, "APROVAR": 1975}
    assert len(corpo["itens"]) == 79
    assert {item["decisao"] for item in corpo["itens"]} == {"BLOQUEAR", "PEDIR_CONFIRMACAO"}
    notas = [item["nota"] for item in corpo["itens"]]
    assert notas == sorted(notas, reverse=True)
    assert all(set(item) == CHAVES_ITEM_FILA for item in corpo["itens"])


@precisa_dados
def test_fila_filtra_so_aprovar(cliente):
    corpo = cliente.get("/api/fila", params={"decisoes": "APROVAR"}).json()

    assert len(corpo["itens"]) == 1975
    assert corpo["total_fila"] == 2054


@precisa_dados
def test_fila_recusa_decisao_invalida(cliente):
    resposta = cliente.get("/api/fila", params={"decisoes": "TALVEZ"})

    assert resposta.status_code == 422


@precisa_dados
def test_respostas_da_api_nunca_trazem_rotulo_nem_identificadores(cliente):
    fila = cliente.get(
        "/api/fila", params={"decisoes": "BLOQUEAR,PEDIR_CONFIRMACAO,APROVAR"}
    ).json()
    id_transacao = fila["itens"][0]["id_transacao"]
    transacao = cliente.get(f"/api/transacoes/{id_transacao}").json()

    for corpo in (fila, transacao):
        assert not (_chaves_recursivas(corpo) & CHAVES_PROIBIDAS)
        assert _sem_nan(corpo)


@precisa_dados
def test_transacao_da_fila_traz_analise_historico_e_resposta(cliente):
    item = cliente.get("/api/fila").json()["itens"][0]

    resposta = cliente.get(f"/api/transacoes/{item['id_transacao']}")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert set(corpo) == {"transacao", "analise", "historico", "resposta_analista"}
    _confere_analise(corpo["analise"])
    assert corpo["analise"]["decisao"] == item["decisao"]
    assert abs(corpo["analise"]["nota"] - item["nota"]) <= 0.1
    assert corpo["transacao"]["id_transacao"] == item["id_transacao"]
    assert len(corpo["historico"]) <= 10


@precisa_dados
def test_transacao_fora_da_fila_devolve_404(cliente):
    resposta = cliente.get("/api/transacoes/-1")

    assert resposta.status_code == 404


@precisa_dados
def test_auditoria_de_transacao_da_fila_e_idempotente(cliente):
    id_transacao = cliente.get("/api/fila").json()["itens"][0]["id_transacao"]

    primeira = cliente.post(f"/api/transacoes/{id_transacao}/auditoria")
    segunda = cliente.post(f"/api/transacoes/{id_transacao}/auditoria")

    assert primeira.status_code == 202
    assert primeira.json()["id_auditoria"] == segunda.json()["id_auditoria"]


@pytest.fixture
def feedback_protegido():
    from src.config import CAMINHO_FEEDBACK  # noqa: PLC0415

    copia = CAMINHO_FEEDBACK.with_suffix(".csv.conformidade")
    existia = CAMINHO_FEEDBACK.exists()
    if existia:
        shutil.copy2(CAMINHO_FEEDBACK, copia)
    yield
    if existia:
        shutil.move(copia, CAMINHO_FEEDBACK)
    elif CAMINHO_FEEDBACK.exists():
        CAMINHO_FEEDBACK.unlink()


@precisa_dados
def test_resposta_do_analista_e_gravada_e_listada(cliente, feedback_protegido):
    item = cliente.get("/api/fila").json()["itens"][0]

    gravada = cliente.post(
        "/api/respostas", json={"id_transacao": item["id_transacao"], "resposta": "fraude"}
    )
    lista = cliente.get("/api/respostas").json()

    assert gravada.status_code == 201
    assert set(gravada.json()) == {"id_transacao", "resposta", "registrado_em"}
    assert set(lista) == {"total", "fraudes", "legitimas", "concordancia", "itens"}
    assert any(r["id_transacao"] == item["id_transacao"] for r in lista["itens"])


@precisa_dados
def test_resposta_invalida_e_recusada(cliente, feedback_protegido):
    item = cliente.get("/api/fila").json()["itens"][0]

    resposta = cliente.post(
        "/api/respostas", json={"id_transacao": item["id_transacao"], "resposta": "talvez"}
    )

    assert resposta.status_code == 422


@precisa_dados
def test_metricas_trazem_os_json_do_modelo_e_os_extras(cliente):
    resposta = cliente.get("/api/metricas")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert set(corpo) == {"metricas", "avaliacao", "extras"}
    assert set(corpo["extras"]) == {"avaliacao_rigorosa", "custos", "eda", "ia_contra_modelo"}
    assert corpo["avaliacao"]["fraudes_total"] == 54
    assert corpo["metricas"]["teste"]["fraudes"] == 54
