"""Testes unitários do agente Sentinela (seção 9 da especificação).

Não dependem da pasta data/ nem do Ollama.
"""

import math

import pandas as pd
import pytest
import requests

from src.agente import AgenteSentinela, calcular_sinais, decidir, granite_disponivel
from src.config import CAMINHO_MODELO

# ---------------------------------------------------------------------------
# Transações de exemplo (seção 9)
# ---------------------------------------------------------------------------

FRAUDE = {
    "valor": 400.0,
    "hora": 3,
    "madrugada": 1,
    "credito": 1,
    "nao_presente": 1,
    "ip_pais_desconhecido": 0,
    "vel_cartao_terminal_1h": 45,
    "qtd_transacoes_cartao_1min": 20,
    "qtd_token_carteira_3m": 80,
    "dist_terminal_anterior_km": 300.0,
    "risco_estabelecimento": 45,
    "tipo_transacao": "credito",
    "modalidade_transacao": "cartao_nao_presente",
}

LEGITIMA = {
    "valor": 30.0,
    "hora": 14,
    "madrugada": 0,
    "credito": 0,
    "nao_presente": 0,
    "ip_pais_desconhecido": 0,
    "vel_cartao_terminal_1h": 2,
    "qtd_transacoes_cartao_1min": 1,
    "qtd_token_carteira_3m": 7,
    "dist_terminal_anterior_km": 10.0,
    "risco_estabelecimento": 18,
    "tipo_transacao": "debito",
    "modalidade_transacao": "cartao_presente",
}

modelo_ausente = not CAMINHO_MODELO.exists()


# ---------------------------------------------------------------------------
# Teste 1: calcular_sinais(FRAUDE) devolve 8 sinais (todos menos ip_desconhecido)
# ---------------------------------------------------------------------------


def test_sinais_fraude_devolve_oito_sinais():
    sinais = calcular_sinais(FRAUDE)

    ids = [s["id"] for s in sinais]
    assert len(sinais) == 8, f"Esperado 8 sinais, obtido {len(sinais)}: {ids}"
    assert "ip_desconhecido" not in ids
    assert "velocidade_terminal" in ids
    assert "rajada_1min" in ids
    assert "token_carteira" in ids
    assert "salto_geografico" in ids
    assert "madrugada" in ids
    assert "valor_alto" in ids
    assert "credito_nao_presente" in ids
    assert "estabelecimento_risco" in ids


# ---------------------------------------------------------------------------
# Teste 2: calcular_sinais(LEGITIMA) devolve lista vazia
# ---------------------------------------------------------------------------


def test_sinais_legitima_devolve_lista_vazia():
    sinais = calcular_sinais(LEGITIMA)

    assert sinais == [], f"Esperado [], obtido: {sinais}"


# ---------------------------------------------------------------------------
# Teste 3: calcular_sinais com todos os campos None/NaN devolve [] sem erro
# ---------------------------------------------------------------------------


def test_sinais_com_todos_campos_none_devolve_lista_vazia():
    transacao_nula = {col: None for col in FRAUDE}

    sinais = calcular_sinais(transacao_nula)

    assert sinais == []


def test_sinais_com_todos_campos_nan_devolve_lista_vazia():
    transacao_nan = {col: math.nan for col in FRAUDE}

    sinais = calcular_sinais(transacao_nan)

    assert sinais == []


# ---------------------------------------------------------------------------
# Teste 4: decidir — casos via parametrize
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "nota, sinais, esperado",
    [
        (10, [], "APROVAR"),
        (50, [], "PEDIR_CONFIRMACAO"),
        (
            10,
            [
                {"id": "valor_alto", "descricao": "x"},
                {"id": "madrugada", "descricao": "x"},
                {"id": "rajada_1min", "descricao": "x"},
            ],
            "PEDIR_CONFIRMACAO",
        ),
        (90, [], "BLOQUEAR"),
        (
            5,
            [{"id": "ip_desconhecido", "descricao": "Endereço IP de país desconhecido."}],
            "BLOQUEAR",
        ),
    ],
)
def test_decidir_retorna_decisao_correta(nota, sinais, esperado):
    decisao = decidir(nota, sinais)

    assert decisao == esperado


# ---------------------------------------------------------------------------
# Testes 5 e 6: dependem do modelo — pulam se sentinela.joblib não existir
# ---------------------------------------------------------------------------


@pytest.mark.skipif(modelo_ausente, reason="modelos/sentinela.joblib não encontrado")
def test_analisar_fraude_tem_decisao_bloquear_e_nota_alta():
    agente = AgenteSentinela()

    resultado = agente.analisar(FRAUDE, usar_llm=False)

    assert resultado["decisao"] == "BLOQUEAR", f"Esperado BLOQUEAR, obtido {resultado['decisao']}"
    assert resultado["nota"] >= 70, f"Esperado nota >= 70, obtido {resultado['nota']}"


@pytest.mark.skipif(modelo_ausente, reason="modelos/sentinela.joblib não encontrado")
def test_analisar_legitima_tem_decisao_aprovar_e_nota_baixa():
    agente = AgenteSentinela()

    resultado = agente.analisar(LEGITIMA, usar_llm=False)

    assert resultado["decisao"] == "APROVAR", f"Esperado APROVAR, obtido {resultado['decisao']}"
    assert resultado["nota"] < 30, f"Esperado nota < 30, obtido {resultado['nota']}"


@pytest.mark.skipif(modelo_ausente, reason="modelos/sentinela.joblib não encontrado")
def test_analisar_devolve_exatamente_seis_chaves():
    agente = AgenteSentinela()

    resultado = agente.analisar(FRAUDE, usar_llm=False)

    chaves_esperadas = {
        "nota",
        "sinais",
        "decisao",
        "decisao_legivel",
        "explicacao",
        "fonte_explicacao",
    }
    assert set(resultado.keys()) == chaves_esperadas, f"Chaves obtidas: {set(resultado.keys())}"


@pytest.mark.skipif(modelo_ausente, reason="modelos/sentinela.joblib não encontrado")
def test_analisar_sem_llm_usa_fonte_regras():
    agente = AgenteSentinela()

    resultado = agente.analisar(FRAUDE, usar_llm=False)

    assert resultado["fonte_explicacao"] == "regras"


@pytest.mark.skipif(modelo_ausente, reason="modelos/sentinela.joblib não encontrado")
def test_analisar_lote_da_mesmas_decisoes_que_analisar_individual():
    agente = AgenteSentinela()
    df = pd.DataFrame([FRAUDE, LEGITIMA])

    resultado_lote = agente.analisar_lote(df)

    decisao_fraude_lote = resultado_lote.iloc[0]["decisao"]
    decisao_legitima_lote = resultado_lote.iloc[1]["decisao"]
    decisao_fraude_individual = agente.analisar(FRAUDE, usar_llm=False)["decisao"]
    decisao_legitima_individual = agente.analisar(LEGITIMA, usar_llm=False)["decisao"]

    assert (
        decisao_fraude_lote == decisao_fraude_individual
    ), f"Lote: {decisao_fraude_lote} | Individual: {decisao_fraude_individual}"
    assert (
        decisao_legitima_lote == decisao_legitima_individual
    ), f"Lote: {decisao_legitima_lote} | Individual: {decisao_legitima_individual}"


# ---------------------------------------------------------------------------
# Testes do Granite com monkeypatch
# ---------------------------------------------------------------------------


def test_granite_disponivel_retorna_false_quando_conexao_falha(monkeypatch):
    def get_falha(*args, **kwargs):
        raise requests.ConnectionError("sem conexão")

    monkeypatch.setattr(requests, "get", get_falha)

    resultado = granite_disponivel()

    assert resultado is False


@pytest.mark.skipif(modelo_ausente, reason="modelos/sentinela.joblib não encontrado")
def test_explicar_usa_fonte_regras_quando_post_estoura_timeout(monkeypatch):
    def get_ok(*args, **kwargs):
        class Resp:
            status_code = 200

        return Resp()

    def post_timeout(*args, **kwargs):
        raise requests.Timeout("timeout")

    monkeypatch.setattr(requests, "get", get_ok)
    monkeypatch.setattr(requests, "post", post_timeout)
    agente = AgenteSentinela()

    _, fonte = agente.explicar(FRAUDE, 90.0, [], "BLOQUEAR", usar_llm=True)

    assert fonte == "regras"


@pytest.mark.skipif(modelo_ausente, reason="modelos/sentinela.joblib não encontrado")
def test_explicar_usa_fonte_regras_quando_response_vem_vazio(monkeypatch):
    def get_ok(*args, **kwargs):
        class Resp:
            status_code = 200

        return Resp()

    def post_vazio(*args, **kwargs):
        class Resp:
            status_code = 200

            def json(self):
                return {"response": ""}

        return Resp()

    monkeypatch.setattr(requests, "get", get_ok)
    monkeypatch.setattr(requests, "post", post_vazio)
    agente = AgenteSentinela()

    _, fonte = agente.explicar(FRAUDE, 90.0, [], "BLOQUEAR", usar_llm=True)

    assert fonte == "regras"


@pytest.mark.skipif(modelo_ausente, reason="modelos/sentinela.joblib não encontrado")
def test_explicar_usa_fonte_granite_quando_resposta_valida(monkeypatch):
    texto_esperado = "Explicação em 3 frases."

    def get_ok(*args, **kwargs):
        class Resp:
            status_code = 200

        return Resp()

    def post_ok(*args, **kwargs):
        class Resp:
            status_code = 200

            def json(self):
                return {"response": texto_esperado}

        return Resp()

    monkeypatch.setattr(requests, "get", get_ok)
    monkeypatch.setattr(requests, "post", post_ok)
    agente = AgenteSentinela()

    texto, fonte = agente.explicar(FRAUDE, 90.0, [], "BLOQUEAR", usar_llm=True)

    assert fonte == "granite"
    assert texto == texto_esperado
