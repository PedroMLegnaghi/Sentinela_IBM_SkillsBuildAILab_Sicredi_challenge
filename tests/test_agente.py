"""Testes unitários do agente Sentinela (seção 9 da especificação).

Não dependem da pasta data/ nem do Ollama.
"""

import math
import pytest

from src.agente import calcular_sinais, decidir
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

# ---------------------------------------------------------------------------
# Teste 1: calcular_sinais(FRAUDE) devolve 8 sinais (todos menos ip_desconhecido)
# ---------------------------------------------------------------------------

def test_sinais_fraude():
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

def test_sinais_legitima():
    sinais = calcular_sinais(LEGITIMA)
    assert sinais == [], f"Esperado [], obtido: {sinais}"


# ---------------------------------------------------------------------------
# Teste 3: calcular_sinais com todos os campos None/NaN devolve [] sem erro
# ---------------------------------------------------------------------------

def test_sinais_todos_none():
    transacao_nula = {col: None for col in FRAUDE}
    sinais = calcular_sinais(transacao_nula)
    assert sinais == []

def test_sinais_todos_nan():
    transacao_nan = {col: math.nan for col in FRAUDE}
    sinais = calcular_sinais(transacao_nan)
    assert sinais == []


# ---------------------------------------------------------------------------
# Teste 4: decidir
# ---------------------------------------------------------------------------

def test_decidir_aprovar():
    assert decidir(10, []) == "APROVAR"

def test_decidir_pedir_confirmacao_nota():
    assert decidir(50, []) == "PEDIR_CONFIRMACAO"

def test_decidir_pedir_confirmacao_sinais():
    tres_sinais = [
        {"id": "valor_alto", "descricao": "x"},
        {"id": "madrugada", "descricao": "x"},
        {"id": "rajada_1min", "descricao": "x"},
    ]
    assert decidir(10, tres_sinais) == "PEDIR_CONFIRMACAO"

def test_decidir_bloquear_nota():
    assert decidir(90, []) == "BLOQUEAR"

def test_decidir_bloquear_ip_desconhecido():
    sinal_ip = [{"id": "ip_desconhecido", "descricao": "Endereço IP de país desconhecido."}]
    assert decidir(5, sinal_ip) == "BLOQUEAR"


# ---------------------------------------------------------------------------
# Testes 5 e 6: dependem do modelo — pulam se sentinela.joblib não existir
# ---------------------------------------------------------------------------

modelo_ausente = not CAMINHO_MODELO.exists()

@pytest.mark.skipif(modelo_ausente, reason="modelos/sentinela.joblib não encontrado")
def test_analisar_fraude():
    from src.agente import AgenteSentinela
    agente = AgenteSentinela()
    resultado = agente.analisar(FRAUDE, usar_llm=False)
    assert resultado["decisao"] == "BLOQUEAR", f"Esperado BLOQUEAR, obtido {resultado['decisao']}"
    assert resultado["nota"] >= 70, f"Esperado nota >= 70, obtido {resultado['nota']}"

@pytest.mark.skipif(modelo_ausente, reason="modelos/sentinela.joblib não encontrado")
def test_analisar_legitima():
    from src.agente import AgenteSentinela
    agente = AgenteSentinela()
    resultado = agente.analisar(LEGITIMA, usar_llm=False)
    assert resultado["decisao"] == "APROVAR", f"Esperado APROVAR, obtido {resultado['decisao']}"
    assert resultado["nota"] < 30, f"Esperado nota < 30, obtido {resultado['nota']}"

@pytest.mark.skipif(modelo_ausente, reason="modelos/sentinela.joblib não encontrado")
def test_analisar_chaves_exatas():
    from src.agente import AgenteSentinela
    agente = AgenteSentinela()
    resultado = agente.analisar(FRAUDE, usar_llm=False)
    chaves_esperadas = {"nota", "sinais", "decisao", "decisao_legivel", "explicacao", "fonte_explicacao"}
    assert set(resultado.keys()) == chaves_esperadas, f"Chaves obtidas: {set(resultado.keys())}"

@pytest.mark.skipif(modelo_ausente, reason="modelos/sentinela.joblib não encontrado")
def test_analisar_fonte_regras_sem_llm():
    from src.agente import AgenteSentinela
    agente = AgenteSentinela()
    resultado = agente.analisar(FRAUDE, usar_llm=False)
    assert resultado["fonte_explicacao"] == "regras"


# ---------------------------------------------------------------------------
# Teste 6: analisar_lote dá as mesmas decisões que analisar
# ---------------------------------------------------------------------------

@pytest.mark.skipif(modelo_ausente, reason="modelos/sentinela.joblib não encontrado")
def test_analisar_lote_consistente():
    import pandas as pd
    from src.agente import AgenteSentinela
    agente = AgenteSentinela()

    df = pd.DataFrame([FRAUDE, LEGITIMA])
    resultado_lote = agente.analisar_lote(df)

    decisao_fraude_lote = resultado_lote.iloc[0]["decisao"]
    decisao_legitima_lote = resultado_lote.iloc[1]["decisao"]

    decisao_fraude_individual = agente.analisar(FRAUDE, usar_llm=False)["decisao"]
    decisao_legitima_individual = agente.analisar(LEGITIMA, usar_llm=False)["decisao"]

    assert decisao_fraude_lote == decisao_fraude_individual, (
        f"Lote: {decisao_fraude_lote} | Individual: {decisao_fraude_individual}"
    )
    assert decisao_legitima_lote == decisao_legitima_individual, (
        f"Lote: {decisao_legitima_lote} | Individual: {decisao_legitima_individual}"
    )
