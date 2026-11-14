"""Testes do canal do associado (ESPECIFICACAO, seção 15), só com valores inventados.

Cobre a mensagem (modelos fixos, regras contra golpe, ponto da IA), as regras de status e
resultado das notificações e as rotas da API sem depender de ``data/`` nem do modelo.
"""

from __future__ import annotations

import pytest

from src.associado import mensagem, notificacoes

TRANSACAO = {"valor": 341.79, "data_hora": "2025-03-03T00:17:00", "tipo_transacao": "credito"}
CONFIRMAR = {"decisao": "PEDIR_CONFIRMACAO"}
BLOQUEAR = {"decisao": "BLOQUEAR"}
APROVAR = {"decisao": "APROVAR"}
MENSAGEM_CONFIRMACAO = (
    "Sicredi: compra de R$ 341,79 em 03/03 às 00:17 no seu cartão de crédito. "
    "Foi você? Responda no app."
)
MENSAGEM_BLOQUEIO = (
    "Sicredi: bloqueamos uma compra de R$ 341,79 em 03/03 às 00:17 por segurança. "
    "Seu cartão está protegido. Foi você? Responda no app."
)


@pytest.fixture(autouse=True)
def memoria_limpa(monkeypatch):
    monkeypatch.setattr(notificacoes, "_notificacoes", {})


# --- Mensagem ---------------------------------------------------------------------------------


def test_formatar_moeda_usa_o_padrao_pt_br():
    assert mensagem.formatar_moeda(341.79) == "R$ 341,79"
    assert mensagem.formatar_moeda(1234.5) == "R$ 1.234,50"


def test_pedido_de_confirmacao_usa_o_modelo_fixo_de_confirmacao():
    texto, fonte = mensagem.redigir_mensagem(TRANSACAO, CONFIRMAR)

    assert texto == MENSAGEM_CONFIRMACAO
    assert fonte == "modelo"


def test_bloqueio_usa_o_modelo_fixo_de_aviso():
    texto, fonte = mensagem.redigir_mensagem(TRANSACAO, BLOQUEAR)

    assert texto == MENSAGEM_BLOQUEIO
    assert fonte == "modelo"


@pytest.mark.parametrize("data_hora", [None, "", float("nan"), "sem-data"])
def test_sem_data_a_mensagem_omite_o_quando_e_continua_valida(data_hora):
    texto, _ = mensagem.redigir_mensagem({**TRANSACAO, "data_hora": data_hora}, CONFIRMAR)

    assert (
        texto == "Sicredi: compra de R$ 341,79 no seu cartão de crédito. Foi você? Responda no app."
    )
    assert mensagem.validar_mensagem(texto)


def test_sem_valor_nem_tipo_a_mensagem_omite_os_trechos():
    texto, _ = mensagem.redigir_mensagem({"data_hora": "2025-03-03T00:17:00"}, BLOQUEAR)

    assert texto == (
        "Sicredi: bloqueamos uma compra em 03/03 às 00:17 por segurança. "
        "Seu cartão está protegido. Foi você? Responda no app."
    )


def test_decisao_aprovar_nao_gera_mensagem():
    with pytest.raises(ValueError, match="APROVAR"):
        mensagem.redigir_mensagem(TRANSACAO, APROVAR)


def test_mensagem_valida_da_ia_e_usada_com_fonte_watsonx(monkeypatch):
    monkeypatch.setattr(
        mensagem, "redigir_com_ia", lambda *_: "Sicredi: foi você? Responda no app."
    )

    texto, fonte = mensagem.redigir_mensagem(TRANSACAO, CONFIRMAR)

    assert texto == "Sicredi: foi você? Responda no app."
    assert fonte == "watsonx"


def test_mensagem_da_ia_que_quebra_regra_e_trocada_pelo_modelo_fixo(monkeypatch):
    monkeypatch.setattr(mensagem, "redigir_com_ia", lambda *_: "Sicredi: confirme em www.x.org")

    texto, fonte = mensagem.redigir_mensagem(TRANSACAO, CONFIRMAR)

    assert texto == MENSAGEM_CONFIRMACAO
    assert fonte == "modelo"


@pytest.mark.parametrize(
    "texto",
    [
        "Compra de R$ 10,00. Foi você? Responda no app.",
        "Sicredi: " + "x" * 152,
        "Sicredi: confirme em http://sicredi.app",
        "Sicredi: confirme em www.sicredi.app",
        "Sicredi: confirme em sicredi.com",
        "Sicredi: informe sua senha no app.",
        "Sicredi: informe o código recebido.",
        "Sicredi: informe o token do app.",
        "Sicredi: informe o CVV do cartão.",
        "Sicredi: compra 1234 negada.",
    ],
)
def test_mensagem_que_quebra_regra_contra_golpe_e_recusada(texto):
    assert not mensagem.validar_mensagem(texto)


def test_mensagem_com_valor_de_milhar_e_horario_e_aceita():
    texto = "Sicredi: compra de R$ 1.234,50 em 03/03 às 00:17 no seu cartão. Foi você?"

    assert mensagem.validar_mensagem(texto)


def test_mensagem_no_limite_de_160_caracteres_e_aceita():
    assert mensagem.validar_mensagem("Sicredi: " + "x" * 151)


# --- Notificações -----------------------------------------------------------------------------


def test_pedido_de_confirmacao_cria_notificacao_aguardando():
    notificacao = notificacoes.criar_notificacao(TRANSACAO, CONFIRMAR)

    assert notificacao["tipo"] == "CONFIRMACAO"
    assert notificacao["status"] == "aguardando"
    assert notificacao["id_transacao"] is None
    assert notificacao["fonte_mensagem"] == "modelo"
    assert notificacao["respondida_em"] is None
    assert notificacao["resultado"] is None


def test_bloqueio_cria_aviso_de_bloqueio_com_id_da_transacao():
    notificacao = notificacoes.criar_notificacao(TRANSACAO, BLOQUEAR, id_transacao=7)

    assert notificacao["tipo"] == "AVISO_BLOQUEIO"
    assert notificacao["id_transacao"] == 7


def test_aprovar_nao_cria_notificacao():
    with pytest.raises(ValueError, match="APROVAR"):
        notificacoes.criar_notificacao(TRANSACAO, APROVAR)

    assert notificacoes.listar() == []


@pytest.mark.parametrize(
    ("analise", "resposta", "status", "inicio_do_resultado"),
    [
        (CONFIRMAR, "sim", "confirmada", "Compra liberada"),
        (CONFIRMAR, "nao", "negada", "Compra bloqueada e cartão protegido"),
        (BLOQUEAR, "sim", "confirmada", "O associado diz que fez a compra"),
        (BLOQUEAR, "nao", "negada", "O associado não reconhece a compra"),
    ],
)
def test_resposta_do_associado_segue_a_regra_de_status_e_resultado(
    analise, resposta, status, inicio_do_resultado
):
    criada = notificacoes.criar_notificacao(TRANSACAO, analise)

    respondida = notificacoes.responder(criada["id_notificacao"], resposta)

    assert respondida["status"] == status
    assert respondida["resultado"].startswith(inicio_do_resultado)
    assert respondida["respondida_em"] is not None
    assert notificacoes.obter(criada["id_notificacao"]) == respondida


def test_notificacao_respondida_nao_aceita_nova_resposta():
    criada = notificacoes.criar_notificacao(TRANSACAO, CONFIRMAR)
    notificacoes.responder(criada["id_notificacao"], "sim")

    with pytest.raises(notificacoes.NotificacaoJaRespondida):
        notificacoes.responder(criada["id_notificacao"], "nao")


def test_responder_notificacao_desconhecida_levanta_key_error():
    with pytest.raises(KeyError):
        notificacoes.responder("nao-existe", "sim")


def test_resposta_fora_de_sim_ou_nao_e_recusada():
    criada = notificacoes.criar_notificacao(TRANSACAO, CONFIRMAR)

    with pytest.raises(ValueError, match="sim"):
        notificacoes.responder(criada["id_notificacao"], "talvez")


def test_listar_devolve_da_mais_recente_para_a_mais_antiga():
    primeira = notificacoes.criar_notificacao(TRANSACAO, CONFIRMAR)
    segunda = notificacoes.criar_notificacao(TRANSACAO, BLOQUEAR)

    ids = [n["id_notificacao"] for n in notificacoes.listar()]

    assert ids == [segunda["id_notificacao"], primeira["id_notificacao"]]


def test_obter_por_transacao_acha_so_a_notificacao_daquela_transacao():
    notificacoes.criar_notificacao(TRANSACAO, BLOQUEAR, id_transacao=7)

    assert notificacoes.obter_por_transacao(7)["id_transacao"] == 7
    assert notificacoes.obter_por_transacao(8) is None
    assert notificacoes.obter("nao-existe") is None


# --- Rotas da API (sem dados nem modelo, via monkeypatch) --------------------------------------


@pytest.fixture(scope="module")
def cliente():
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient  # noqa: PLC0415

    from src.api.app import app  # noqa: PLC0415

    with TestClient(app) as cliente_teste:
        yield cliente_teste


@pytest.fixture
def fila_inventada(monkeypatch):
    """Finge uma fila com a transação 7 bloqueada e a 8 aprovada; a 9 não existe."""
    import src.api.servicos as sv  # noqa: PLC0415

    analises = {7: BLOQUEAR, 8: APROVAR}

    def obter_transacao(id_transacao: int) -> dict:
        if id_transacao not in analises:
            raise KeyError(f"Transação {id_transacao} não encontrada na fila.")
        return {"transacao": TRANSACAO, "analise": analises[id_transacao]}

    monkeypatch.setattr(sv, "dados_carregados", lambda: True)
    monkeypatch.setattr(sv, "obter_transacao", obter_transacao)


def test_rota_cria_a_notificacao_com_201_e_repete_a_mesma_com_200(cliente, fila_inventada):
    primeira = cliente.post("/api/transacoes/7/notificacao")
    segunda = cliente.post("/api/transacoes/7/notificacao")

    assert primeira.status_code == 201
    assert segunda.status_code == 200
    assert primeira.json()["id_notificacao"] == segunda.json()["id_notificacao"]
    assert primeira.json()["tipo"] == "AVISO_BLOQUEIO"


def test_rota_recusa_transacao_aprovada_com_422(cliente, fila_inventada):
    resposta = cliente.post("/api/transacoes/8/notificacao")

    assert resposta.status_code == 422
    assert "APROVAR" in resposta.json()["detail"]


def test_rota_devolve_404_fora_da_fila(cliente, fila_inventada):
    assert cliente.post("/api/transacoes/9/notificacao").status_code == 404


def test_rota_devolve_503_sem_dados(cliente, monkeypatch):
    import src.api.servicos as sv  # noqa: PLC0415

    monkeypatch.setattr(sv, "dados_carregados", lambda: False)

    assert cliente.post("/api/transacoes/7/notificacao").status_code == 503


def test_resposta_duplicada_devolve_409(cliente):
    criada = notificacoes.criar_notificacao(TRANSACAO, CONFIRMAR)
    rota = f"/api/notificacoes/{criada['id_notificacao']}/resposta"

    primeira = cliente.post(rota, json={"resposta": "sim"})
    segunda = cliente.post(rota, json={"resposta": "nao"})

    assert primeira.status_code == 200
    assert primeira.json()["status"] == "confirmada"
    assert segunda.status_code == 409


def test_resposta_invalida_devolve_422_e_desconhecida_404(cliente):
    criada = notificacoes.criar_notificacao(TRANSACAO, CONFIRMAR)
    rota = f"/api/notificacoes/{criada['id_notificacao']}/resposta"

    assert cliente.post(rota, json={"resposta": "talvez"}).status_code == 422
    assert cliente.post("/api/notificacoes/x/resposta", json={"resposta": "sim"}).status_code == 404
    assert cliente.get("/api/notificacoes/x").status_code == 404


def test_listagem_e_consulta_por_id_devolvem_a_notificacao(cliente):
    criada = notificacoes.criar_notificacao(TRANSACAO, BLOQUEAR)

    lista = cliente.get("/api/notificacoes").json()["itens"]
    uma = cliente.get(f"/api/notificacoes/{criada['id_notificacao']}").json()

    assert lista == [criada]
    assert uma == criada


@pytest.mark.parametrize(("analise", "tem_notificacao"), [(BLOQUEAR, True), (APROVAR, False)])
def test_analisar_avisa_o_associado_so_quando_a_decisao_pede(
    cliente, monkeypatch, analise, tem_notificacao
):
    import src.api.servicos as sv  # noqa: PLC0415

    monkeypatch.setattr(sv, "modelo_carregado", lambda: True)
    monkeypatch.setattr(sv, "analisar_transacao", lambda _: {**analise, "sinais": []})

    corpo = cliente.post("/api/analisar", json={"valor": 50.0, "auditar": False}).json()

    assert (corpo["id_notificacao"] is not None) == tem_notificacao
    if tem_notificacao:
        assert cliente.get(f"/api/notificacoes/{corpo['id_notificacao']}").status_code == 200
