"""Testes de PerfilAssociado (Issue #64).

Verifica o cálculo do perfil com e sem histórico anterior, e que a
hora_mais_comum usa apenas compras anteriores.
"""

from __future__ import annotations

import pandas as pd

from src.auditoria.ferramentas import CaixaDeFerramentas

# ---------------------------------------------------------------------------
# Dados inventados (nunca linhas de data/)
# ---------------------------------------------------------------------------

_COLUNAS = [
    "id_transacao",
    "id_cliente",
    "id_cartao",
    "id_estabelecimento",
    "data_hora",
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
]

_ANALISE_VAZIA: dict = {"sinais": [], "contribuicoes": []}


def _base_simples() -> pd.DataFrame:
    """Base com 3 compras anteriores do cliente 'cli-1' e 1 de outro cliente."""
    linhas = [
        # compras anteriores do cli-1
        {
            "id_transacao": 1,
            "id_cliente": "cli-1",
            "id_cartao": "crt-1",
            "id_estabelecimento": "est-1",
            "data_hora": pd.Timestamp("2025-01-10T14:00:00"),
            "valor": 100.0,
            "hora": 14.0,
            "madrugada": 0.0,
            "credito": 1.0,
            "nao_presente": 0.0,
            "ip_pais_desconhecido": 0.0,
            "vel_cartao_terminal_1h": 1.0,
            "qtd_transacoes_cartao_1min": 1.0,
            "qtd_token_carteira_3m": 1.0,
            "dist_terminal_anterior_km": 0.5,
            "risco_estabelecimento": 0.1,
        },
        {
            "id_transacao": 2,
            "id_cliente": "cli-1",
            "id_cartao": "crt-1",
            "id_estabelecimento": "est-1",
            "data_hora": pd.Timestamp("2025-01-11T14:30:00"),
            "valor": 200.0,
            "hora": 14.5,
            "madrugada": 0.0,
            "credito": 1.0,
            "nao_presente": 1.0,
            "ip_pais_desconhecido": 0.0,
            "vel_cartao_terminal_1h": 1.0,
            "qtd_transacoes_cartao_1min": 1.0,
            "qtd_token_carteira_3m": 1.0,
            "dist_terminal_anterior_km": 1.0,
            "risco_estabelecimento": 0.1,
        },
        # outro cliente — não deve entrar no perfil
        {
            "id_transacao": 3,
            "id_cliente": "cli-2",
            "id_cartao": "crt-2",
            "id_estabelecimento": "est-2",
            "data_hora": pd.Timestamp("2025-01-11T02:00:00"),
            "valor": 999.0,
            "hora": 2.0,
            "madrugada": 1.0,
            "credito": 1.0,
            "nao_presente": 1.0,
            "ip_pais_desconhecido": 1.0,
            "vel_cartao_terminal_1h": 10.0,
            "qtd_transacoes_cartao_1min": 5.0,
            "qtd_token_carteira_3m": 30.0,
            "dist_terminal_anterior_km": 500.0,
            "risco_estabelecimento": 0.9,
        },
    ]
    return pd.DataFrame(linhas)


_TRANSACAO_CLI1 = {
    "id_transacao": 10,
    "id_cliente": "cli-1",
    "id_cartao": "crt-1",
    "id_estabelecimento": "est-1",
    "data_hora": pd.Timestamp("2025-02-01T10:00:00"),
    "valor": 300.0,
    "hora": 10.0,
    "madrugada": 0.0,
    "credito": 1.0,
    "nao_presente": 0.0,
}

_TRANSACAO_SEM_HISTORICO = {
    "id_transacao": 20,
    "id_cliente": "cli-999",
    "id_cartao": "crt-999",
    "id_estabelecimento": "est-1",
    "data_hora": pd.Timestamp("2025-02-01T12:00:00"),
    "valor": 50.0,
    "hora": 12.0,
    "madrugada": 0.0,
    "credito": 0.0,
    "nao_presente": 0.0,
}


# ---------------------------------------------------------------------------
# Testes
# ---------------------------------------------------------------------------


def test_perfil_sem_historico_devolve_none():
    """Perfil retorna None quando o cliente não tem compras anteriores."""
    base = _base_simples()
    caixa = CaixaDeFerramentas(_TRANSACAO_SEM_HISTORICO, _ANALISE_VAZIA, base)
    envelope = caixa.executar("perfil_do_cliente")
    assert envelope["status"] == "sem_dados"


def test_perfil_usa_apenas_compras_anteriores():
    """O perfil não inclui compras de outros clientes."""
    base = _base_simples()
    caixa = CaixaDeFerramentas(_TRANSACAO_CLI1, _ANALISE_VAZIA, base)
    envelope = caixa.executar("perfil_do_cliente")
    assert envelope["status"] == "ok"
    assert envelope["dados"]["compras_anteriores"] == 2


def test_hora_mais_comum_e_calculada():
    """hora_mais_comum reflete a hora inteira mais frequente no histórico."""
    base = _base_simples()
    caixa = CaixaDeFerramentas(_TRANSACAO_CLI1, _ANALISE_VAZIA, base)
    envelope = caixa.executar("perfil_do_cliente")
    # hora 14 aparece em ambas as transações anteriores (14.0 e 14.5 → int 14)
    assert envelope["dados"]["hora_mais_comum"] == 14


def test_perfil_tem_todas_as_chaves_do_contrato():
    """O dicionário de dados tem exatamente os campos de PerfilAssociado."""
    chaves_esperadas = {
        "compras_anteriores",
        "mediana_valor",
        "valor_atual_sobre_mediana",
        "hora_mais_comum",
        "percentual_madrugada",
        "percentual_credito_nao_presente",
    }
    base = _base_simples()
    caixa = CaixaDeFerramentas(_TRANSACAO_CLI1, _ANALISE_VAZIA, base)
    envelope = caixa.executar("perfil_do_cliente")
    assert set(envelope["dados"].keys()) == chaves_esperadas


def test_perfil_sem_base_devolve_sem_dados():
    """Perfil retorna sem_dados quando a base não está disponível."""
    caixa = CaixaDeFerramentas(_TRANSACAO_CLI1, _ANALISE_VAZIA, base=None)
    envelope = caixa.executar("perfil_do_cliente")
    assert envelope["status"] == "sem_dados"
