"""Testes da auditoria por IA (ESPECIFICACAO, seção 13), sem rede e com dados inventados."""

from __future__ import annotations

import json

import pandas as pd
import pytest
import requests

from src import auditoria
from src.auditoria import watsonx
from src.auditoria.ferramentas import CaixaDeFerramentas
from src.auditoria.relatorio import calcular_parecer, validar_parcial

CHAVES_PROIBIDAS = {
    "fraude",
    "decisao_sistema_atual",
    "id_cartao",
    "id_cliente",
    "id_estabelecimento",
}


def _base_inventada() -> pd.DataFrame:
    linhas = []
    for i in range(6):
        linhas.append(
            {
                "id_transacao": i,
                "data_hora": pd.Timestamp("2025-03-01 10:00") + pd.Timedelta(hours=i),
                "id_cartao": "cartao-a",
                "id_cliente": "cliente-a",
                "id_estabelecimento": "loja-a",
                "valor": 40.0 + i,
                "madrugada": 0,
                "credito": 1,
                "nao_presente": 0,
                "qtd_transacoes_cartao_1min": 1,
                "fraude": 0,
                "decisao_sistema_atual": "approve",
            }
        )
    return pd.DataFrame(linhas)


def _transacao(**extra) -> dict:
    base = {
        "id_transacao": 99,
        "data_hora": pd.Timestamp("2025-03-01 13:30"),
        "id_cartao": "cartao-a",
        "id_cliente": "cliente-a",
        "id_estabelecimento": "loja-a",
        "valor": 420.0,
        "hora": 13,
        "ip_pais_desconhecido": 0,
        "risco_estabelecimento": 20,
    }
    return {**base, **extra}


def _analise(decisao: str = "BLOQUEAR", n_sinais: int = 1) -> dict:
    sinais = [{"id": f"s{i}", "descricao": f"Sinal inventado {i}."} for i in range(n_sinais)]
    return {"decisao": decisao, "sinais": sinais, "contribuicoes": []}


def _chaves(valor) -> set[str]:
    if isinstance(valor, dict):
        return set(valor) | {c for item in valor.values() for c in _chaves(item)}
    if isinstance(valor, list):
        return {c for item in valor for c in _chaves(item)}
    return set()


class _Resposta:
    def __init__(self, corpo: dict, status: int = 200):
        self._corpo = corpo
        self.status_code = status

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(str(self.status_code))

    def json(self) -> dict:
        return self._corpo


@pytest.fixture
def sem_credenciais(monkeypatch):
    monkeypatch.delenv("WATSONX_APIKEY", raising=False)
    monkeypatch.delenv("WATSONX_PROJECT_ID", raising=False)


@pytest.fixture
def com_credenciais(monkeypatch):
    monkeypatch.setenv("WATSONX_APIKEY", "chave-inventada")
    monkeypatch.setenv("WATSONX_PROJECT_ID", "projeto-inventado")
    monkeypatch.setattr(watsonx, "_token", {"valor": None, "expira": 0.0})


def _respostas_em_sequencia(monkeypatch, chats: list) -> list[dict]:
    enviados: list[dict] = []
    fila = list(chats)

    def falso_post(url, **kwargs):
        if "identity/token" in url:
            return _Resposta({"access_token": "token-inventado", "expiration": 9_999_999_999})
        enviados.append(kwargs["json"])
        proximo = fila.pop(0)
        if isinstance(proximo, Exception):
            raise proximo
        return _Resposta({"choices": [{"message": proximo}]})

    monkeypatch.setattr(watsonx.requests, "post", falso_post)
    return enviados


FINAL_VALIDO = {
    "role": "assistant",
    "content": json.dumps(
        {
            "risco_ia": "ALTO",
            "confianca": "ALTA",
            "explicacao": "O valor é dez vezes a mediana do cliente.",
            "evidencias_a_favor": ["Valor atípico para o cliente."],
            "evidencias_contra": [],
            "dados_ausentes": [],
        }
    ),
}


@pytest.mark.parametrize(
    ("risco", "confianca", "decisao", "esperado"),
    [
        ("ALTO", "ALTA", "BLOQUEAR", "CONFIRMA"),
        ("BAIXO", "MEDIA", "BLOQUEAR", "DIVERGE"),
        ("SUSPEITO", "MEDIA", "PEDIR_CONFIRMACAO", "CONFIRMA"),
        (None, "ALTA", "APROVAR", "INCONCLUSIVO"),
        ("ALTO", "BAIXA", "BLOQUEAR", "INCONCLUSIVO"),
    ],
)
def test_parecer_segue_a_regra_da_especificacao(risco, confianca, decisao, esperado):
    assert calcular_parecer(risco, confianca, decisao) == esperado


def test_relatorio_com_risco_invalido_e_recusado():
    with pytest.raises(ValueError):
        validar_parcial({"risco_ia": "ENORME", "confianca": "ALTA", "explicacao": "x"})


def test_explicacao_longa_e_cortada_no_fim_de_uma_frase():
    frase = "A compra foi feita de madrugada com nota 97.3 e IP desconhecido. "
    texto = (frase * 20).strip()

    parcial = validar_parcial({"risco_ia": None, "confianca": "BAIXA", "explicacao": texto})

    assert len(parcial["explicacao"]) <= 600
    assert parcial["explicacao"].endswith("desconhecido.")


def test_explicacao_longa_sem_pontuacao_termina_em_reticencias_sem_quebrar_palavra():
    texto = "palavra " * 120

    parcial = validar_parcial({"risco_ia": None, "confianca": "BAIXA", "explicacao": texto})

    assert len(parcial["explicacao"]) <= 600
    assert parcial["explicacao"].endswith("palavra…")


def test_explicacao_curta_fica_igual():
    texto = "Sinais fortes de fraude. Nota 100.0 de 100."

    parcial = validar_parcial({"risco_ia": "ALTO", "confianca": "ALTA", "explicacao": texto})

    assert parcial["explicacao"] == texto


def test_historico_do_cartao_usa_so_compras_anteriores():
    caixa = CaixaDeFerramentas(_transacao(), _analise(), _base_inventada())

    envelope = caixa.executar("historico_do_cartao")

    assert envelope["status"] == "ok"
    assert envelope["dados"]["compras_anteriores"] == 4


def test_nenhuma_ferramenta_devolve_rotulo_ou_identificador():
    caixa = CaixaDeFerramentas(_transacao(), _analise(), _base_inventada())

    envelopes = [caixa.executar(nome) for nome in caixa.nomes()]

    assert not (_chaves(envelopes) & CHAVES_PROIBIDAS)


@pytest.mark.parametrize(
    ("ferramenta", "esperado"),
    [
        ("historico_do_cartao", "histórico do cartão"),
        ("perfil_do_cliente", "histórico do cliente"),
        ("perfil_do_estabelecimento", "histórico do estabelecimento"),
    ],
)
def test_compra_sem_identificador_informa_historico_em_texto_legivel(ferramenta, esperado):
    transacao = _transacao(id_cartao=None, id_cliente=None, id_estabelecimento=None)
    caixa = CaixaDeFerramentas(transacao, _analise(), _base_inventada())

    envelope = caixa.executar(ferramenta)

    assert envelope["status"] == "sem_dados"
    assert envelope["campos_ausentes"] == [esperado]
    assert caixa.usadas[-1]["resumo"] == "sem histórico: compra sem identificação (simulada)"


def test_compra_sem_identificador_nao_cita_colunas_internas():
    transacao = _transacao(id_cartao=None, id_cliente=None, id_estabelecimento=None)
    caixa = CaixaDeFerramentas(transacao, _analise(), _base_inventada())

    envelopes = [caixa.executar(nome) for nome in caixa.nomes()]

    assert "id_" not in json.dumps(envelopes, default=str)
    assert all("id_" not in usada["resumo"] for usada in caixa.usadas)


def test_ferramenta_sem_base_informa_o_que_faltou():
    caixa = CaixaDeFerramentas(_transacao(), _analise(), None)

    envelope = caixa.executar("perfil_do_cliente")

    assert envelope["status"] == "sem_dados"
    assert envelope["campos_ausentes"] == ["base de dados"]


def test_modo_local_marca_alto_com_ip_desconhecido(sem_credenciais):
    relatorio = auditoria.auditar(_transacao(ip_pais_desconhecido=1), _analise(n_sinais=1))

    assert relatorio["fonte"] == "local"
    assert relatorio["risco_ia"] == "ALTO"
    assert relatorio["parecer"] == "CONFIRMA"


def test_modo_local_diverge_quando_o_modelo_bloqueia_sem_sinais(sem_credenciais):
    relatorio = auditoria.auditar(_transacao(), _analise(decisao="BLOQUEAR", n_sinais=0))

    assert relatorio["risco_ia"] == "BAIXO"
    assert relatorio["parecer"] == "DIVERGE"


def test_watsonx_chama_ferramenta_e_entrega_relatorio(com_credenciais, monkeypatch):
    pedido = {
        "role": "assistant",
        "tool_calls": [
            {
                "id": "c1",
                "type": "function",
                "function": {"name": "perfil_do_cliente", "arguments": "{}"},
            }
        ],
    }
    enviados = _respostas_em_sequencia(monkeypatch, [pedido, FINAL_VALIDO])
    auditoria.configurar_base(_base_inventada())

    relatorio = auditoria.auditar(_transacao(), _analise())

    auditoria.configurar_base(None)
    assert relatorio["fonte"] == "watsonx"
    assert relatorio["parecer"] == "CONFIRMA"
    assert [f["nome"] for f in relatorio["ferramentas_usadas"]] == ["perfil_do_cliente"]
    texto_enviado = json.dumps(enviados, default=str)
    assert all(ident not in texto_enviado for ident in ("cartao-a", "cliente-a", "loja-a"))


def test_json_invalido_duas_vezes_cai_no_modo_local(com_credenciais, monkeypatch):
    invalido = {"role": "assistant", "content": "não sei"}
    _respostas_em_sequencia(monkeypatch, [invalido, invalido])

    relatorio = auditoria.auditar(_transacao(), _analise())

    assert relatorio["fonte"] == "local"


def test_tempo_esgotado_cai_no_modo_local(com_credenciais, monkeypatch):
    _respostas_em_sequencia(monkeypatch, [requests.Timeout("lento")])

    relatorio = auditoria.auditar(_transacao(), _analise())

    assert relatorio["fonte"] == "local"


def test_env_nao_sobrescreve_variavel_ja_definida(tmp_path, monkeypatch):
    arquivo = tmp_path / ".env"
    arquivo.write_text("WATSONX_MODELO=modelo-do-arquivo\nWATSONX_URL=\n", encoding="utf-8")
    monkeypatch.setenv("WATSONX_MODELO", "modelo-do-ambiente")
    monkeypatch.delenv("WATSONX_URL", raising=False)

    watsonx.carregar_env(arquivo)

    import os  # noqa: PLC0415

    assert os.environ["WATSONX_MODELO"] == "modelo-do-ambiente"
    assert "WATSONX_URL" not in os.environ
