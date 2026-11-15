"""Testes do chat do associado (Issue #105), com o watsonx.ai simulado e dados inventados."""

from __future__ import annotations

import pandas as pd
import pytest

from src.adaptadores.memoria import dados_demo
from src.api import sessao
from src.aplicacao import associado as associado_app
from src.associado import chat, notificacoes
from src.auditoria import watsonx

COMPRAS = [
    {
        "id_compra": "cmp-000003",
        "id_notificacao": None,
        "estabelecimento": "Mercado Bom Preço",
        "data_hora": "2025-03-10T10:00:00",
        "valor": 100.0,
        "tipo_transacao": "debito",
        "situacao": "APROVADA",
        "final_cartao": "1111",
    },
    {
        "id_compra": "cmp-000002",
        "id_notificacao": "abc",
        "estabelecimento": "Loja online",
        "data_hora": "2025-03-05T03:00:00",
        "valor": 980.0,
        "tipo_transacao": "credito",
        "situacao": "BLOQUEADA",
        "final_cartao": "4821",
    },
    {
        "id_compra": "cmp-000001",
        "id_notificacao": None,
        "estabelecimento": "Posto Avenida",
        "data_hora": "2025-03-01T09:00:00",
        "valor": 50.5,
        "tipo_transacao": "credito",
        "situacao": "APROVADA",
        "final_cartao": "4821",
    },
]
CONTEXTO = {"saldo": 4820.35, "limite_disponivel": 2150.0, "compras": COMPRAS}


@pytest.fixture
def ia_falsa(monkeypatch):
    """Simula o watsonx.ai e guarda o que foi enviado."""
    enviados: list[str] = []
    resposta = {"texto": "Em março você gastou R$ 150,50 nas compras aprovadas."}

    def redigir(instrucoes, pedido, max_tokens, timeout_s):
        enviados.append(instrucoes + "\n" + pedido)
        return resposta["texto"]

    monkeypatch.setattr(watsonx, "credenciais_disponiveis", lambda: True)
    monkeypatch.setattr(watsonx, "redigir_texto", redigir)
    return {"enviados": enviados, "resposta": resposta}


def test_pedido_a_ia_nao_leva_identificadores_nem_detalhe_tecnico(ia_falsa):
    resultado = chat.responder(
        "Quanto gastei no mês?", [{"autor": "associado", "texto": "oi"}], CONTEXTO
    )

    enviado = ia_falsa["enviados"][0]
    assert resultado == {"resposta": ia_falsa["resposta"]["texto"], "fonte": "watsonx"}
    for proibido in ("cmp-0000", "abc", "id_", "4821", "1111", "nota", "sinais", "parecer"):
        assert proibido not in enviado
    assert chat.MOTIVO_GENERICO in enviado


def test_pergunta_fora_do_assunto_recebe_a_recusa_padrao_sem_chamar_a_ia(ia_falsa):
    resultado = chat.responder("Qual a capital da França?", [], CONTEXTO)

    assert resultado == {"resposta": chat.RECUSA_PADRAO, "fonte": "local"}
    assert ia_falsa["enviados"] == []


def test_sem_credenciais_responde_no_modo_local(monkeypatch):
    monkeypatch.setattr(watsonx, "credenciais_disponiveis", lambda: False)

    resultado = chat.responder("Quanto gastei?", [], CONTEXTO)

    assert resultado["fonte"] == "local"
    assert "03/2025" in resultado["resposta"]
    assert "R$ 150,50" in resultado["resposta"]
    assert "1 estão bloqueadas" in resultado["resposta"]


def test_falha_do_watsonx_cai_no_modo_local(monkeypatch):
    def falhar(*_):
        raise watsonx.FalhaWatsonx("sem rede")

    monkeypatch.setattr(watsonx, "credenciais_disponiveis", lambda: True)
    monkeypatch.setattr(watsonx, "redigir_texto", falhar)

    assert chat.responder("Meu saldo?", [], CONTEXTO)["fonte"] == "local"


@pytest.mark.parametrize(
    "texto",
    [
        "Informe sua senha para eu ver a compra.",
        "Vou liberar a sua compra agora mesmo.",
        "Veja em www.exemplo.org",
        "x" * 401,
    ],
)
def test_resposta_da_ia_fora_das_regras_e_trocada_pelo_resumo_local(ia_falsa, texto):
    ia_falsa["resposta"]["texto"] = texto

    resultado = chat.responder("Por que minha compra foi bloqueada?", [], CONTEXTO)

    assert resultado["fonte"] == "local"


def test_resumo_para_o_gerente_traz_as_perguntas_e_a_situacao():
    historico = [
        {"autor": "associado", "texto": "Por que bloquearam minha compra?"},
        {"autor": "ia", "texto": "Ela fugiu do seu padrão."},
    ]

    resumo = chat.resumir_para_gerente(historico, CONTEXTO)

    assert "Por que bloquearam minha compra?" in resumo
    assert "1 estão bloqueadas" in resumo
    assert "Ela fugiu" not in resumo


# --- Rotas ------------------------------------------------------------------------------------

pytest.importorskip("fastapi")


def _base_inventada() -> pd.DataFrame:
    linhas = []
    for indice in range(10):
        cliente = f"c{indice + 1:02d}"
        for i in range(2):
            tipo = "debito" if i == 0 else "credito"
            linhas.append(
                {
                    "id_transacao": indice * 2 + i,
                    "data_hora": pd.Timestamp(f"2025-03-0{i + 1} 09:00:00"),
                    "id_cartao": f"{cliente}-{tipo}",
                    "id_cliente": cliente,
                    "valor": 25.0,
                    "tipo_transacao": tipo,
                    "modalidade_transacao": "cartao_presente",
                    "risco_estabelecimento": 10.0,
                }
            )
    return pd.DataFrame(linhas)


@pytest.fixture(scope="module")
def cliente():
    from fastapi.testclient import TestClient  # noqa: PLC0415

    from src.api.app import app  # noqa: PLC0415

    with TestClient(app) as cliente_teste:
        yield cliente_teste


@pytest.fixture
def ambiente(monkeypatch):
    monkeypatch.setattr(notificacoes, "_notificacoes", {})
    repos = dados_demo.montar_repositorios(_base_inventada(), {0: "APROVAR", 1: "BLOQUEAR"})
    associado_app.avisar_compras_de_marco(repos)
    monkeypatch.setattr(sessao._estado, "repositorios", repos)
    monkeypatch.setattr(sessao._estado, "tokens", {})
    monkeypatch.setattr(watsonx, "credenciais_disponiveis", lambda: False)


def _cabecalho(cliente, id_perfil: str) -> dict[str, str]:
    return {"X-Sessao": cliente.post("/api/sessao", json={"id_perfil": id_perfil}).json()["token"]}


def test_rota_do_chat_responde_no_modo_local_sem_env(cliente, ambiente):
    resposta = cliente.post(
        "/api/associado/chat",
        json={"mensagem": "Quanto gastei em março?", "historico": []},
        headers=_cabecalho(cliente, "asc-01"),
    )

    assert resposta.status_code == 200
    assert resposta.json()["fonte"] == "local"
    assert "R$ 25,00" in resposta.json()["resposta"]


def test_rota_do_chat_valida_tamanho_e_papel(cliente, ambiente):
    cabecalho = _cabecalho(cliente, "asc-01")

    assert (
        cliente.post("/api/associado/chat", json={"mensagem": ""}, headers=cabecalho).status_code
        == 422
    )
    assert (
        cliente.post(
            "/api/associado/chat", json={"mensagem": "x" * 501}, headers=cabecalho
        ).status_code
        == 422
    )
    muitas = [{"autor": "ia", "texto": "oi"}] * 21
    assert (
        cliente.post(
            "/api/associado/chat",
            json={"mensagem": "saldo", "historico": muitas},
            headers=cabecalho,
        ).status_code
        == 422
    )
    assert (
        cliente.post(
            "/api/associado/chat", json={"mensagem": "saldo"}, headers=_cabecalho(cliente, "aud-01")
        ).status_code
        == 403
    )


def test_conversar_com_gerente_traz_o_gerente_da_agencia_e_o_resumo(cliente, ambiente):
    historico = [{"autor": "associado", "texto": "Minha compra foi bloqueada?"}]

    centro = cliente.post(
        "/api/associado/chat/gerente",
        json={"historico": historico},
        headers=_cabecalho(cliente, "asc-01"),
    ).json()
    norte = cliente.post(
        "/api/associado/chat/gerente", json={"historico": []}, headers=_cabecalho(cliente, "asc-02")
    ).json()

    assert centro["gerente"] == {"nome": "Helena Castro"}
    assert "Minha compra foi bloqueada?" in centro["resumo"]
    assert "1 estão bloqueadas" in centro["resumo"]
    assert norte["gerente"] == {"nome": "Marcos Viana"}
