"""Testes do "Pergunte à IA" (Issue #66): modo local, watsonx simulado e nenhum vazamento."""

from __future__ import annotations

import json

import pytest

from src.auditoria import watsonx
from src.auditoria.perguntas import responder_pergunta
from src.auditoria.watsonx import FalhaWatsonx

TRANSACAO = {
    "valor": 4520.0,
    "hora": 3.0,
    "data_hora": "2025-03-15T03:12:00",
    "tipo_transacao": "credito",
    "modalidade_transacao": "cartao_nao_presente",
    "id_cartao": "CARTAO-SECRETO-1",
    "id_cliente": "CLIENTE-SECRETO-1",
    "id_estabelecimento": "ESTAB-SECRETO-1",
    "fraude": 1,
    "decisao_sistema_atual": "APROVAR",
}
ANALISE = {
    "sinais": [{"id": "madrugada", "descricao": "Compra feita na madrugada."}],
    "contribuicoes": [],
}
CHAVES = {"resposta", "ferramentas_usadas", "fonte", "latencia_ms"}
CINCO_FERRAMENTAS = {
    "sinais_da_transacao",
    "contribuicoes_da_nota",
    "historico_do_cartao",
    "perfil_do_cliente",
    "perfil_do_estabelecimento",
}


@pytest.fixture
def sem_credenciais(monkeypatch):
    monkeypatch.delenv("WATSONX_APIKEY", raising=False)
    monkeypatch.delenv("WATSONX_PROJECT_ID", raising=False)


@pytest.fixture
def com_credenciais(monkeypatch):
    monkeypatch.setenv("WATSONX_APIKEY", "chave-falsa")
    monkeypatch.setenv("WATSONX_PROJECT_ID", "projeto-falso")


def _chat_falso(enviadas: list[str]):
    """Primeiro pede uma ferramenta; depois responde em texto."""

    def chat(mensagens, ferramentas, prazo, max_tokens=900):
        enviadas.append(json.dumps(mensagens, default=str))
        if len(enviadas) == 1:
            return {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "id": "1",
                        "type": "function",
                        "function": {"name": "sinais_da_transacao", "arguments": "{}"},
                    }
                ],
            }
        return {"role": "assistant", "content": "A compra foi feita na madrugada."}

    return chat


def test_sem_credenciais_lista_o_resumo_das_cinco_ferramentas(sem_credenciais):
    resultado = responder_pergunta("Por que bloquear?", TRANSACAO, ANALISE, None)

    assert resultado["fonte"] == "local"
    assert "indisponível" in resultado["resposta"]
    assert {f["nome"] for f in resultado["ferramentas_usadas"]} == CINCO_FERRAMENTAS
    assert resultado["latencia_ms"] >= 0


def test_com_watsonx_usa_ferramentas_e_devolve_o_texto_do_modelo(com_credenciais, monkeypatch):
    enviadas: list[str] = []
    monkeypatch.setattr(watsonx, "_chamar_chat", _chat_falso(enviadas))

    resultado = responder_pergunta("Por que bloquear?", TRANSACAO, ANALISE, None)

    assert resultado["fonte"] == "watsonx"
    assert resultado["resposta"] == "A compra foi feita na madrugada."
    assert [f["nome"] for f in resultado["ferramentas_usadas"]] == ["sinais_da_transacao"]
    assert "Por que bloquear?" in enviadas[0]


def test_falha_do_watsonx_cai_no_modo_local(com_credenciais, monkeypatch):
    def chat_com_erro(*_args, **_kwargs):
        raise FalhaWatsonx("fora do ar")

    monkeypatch.setattr(watsonx, "_chamar_chat", chat_com_erro)

    resultado = responder_pergunta("Por que bloquear?", TRANSACAO, ANALISE, None)

    assert resultado["fonte"] == "local"
    assert len(resultado["ferramentas_usadas"]) == 5


def test_nao_devolve_identificadores_rotulo_nem_decisao_do_sistema_atual(
    sem_credenciais,
):
    resultado = responder_pergunta("Quem é o cliente?", TRANSACAO, ANALISE, None)
    texto = json.dumps(resultado, ensure_ascii=False)

    assert set(resultado) == CHAVES
    for segredo in ("SECRETO", "decisao_sistema_atual", "id_cartao", "id_cliente"):
        assert segredo not in texto


def test_nao_envia_identificadores_ao_watsonx(com_credenciais, monkeypatch):
    enviadas: list[str] = []
    monkeypatch.setattr(watsonx, "_chamar_chat", _chat_falso(enviadas))

    resultado = responder_pergunta("Por que bloquear?", TRANSACAO, ANALISE, None)
    texto = json.dumps(resultado, ensure_ascii=False)

    assert set(resultado) == CHAVES
    assert "SECRETO" not in texto
    assert all("SECRETO" not in enviada for enviada in enviadas)
    assert all("decisao_sistema_atual" not in enviada for enviada in enviadas)