"""Testes das rotas da filial (Issue #96) sem ``data/`` nem modelo: fila e base inventadas."""

from __future__ import annotations

import pandas as pd
import pytest

from src.adaptadores.memoria import dados_demo
from src.api import rotas_filial, sessao
from src.aplicacao import associado as associado_app
from src.associado import notificacoes

CHAVES_PROIBIDAS = {"id_cartao", "id_cliente", "id_estabelecimento", "id_transacao", "fraude"}
CHAVES_LGPD = {"saldo", "limite_total", "limite_disponivel", "extrato"}
CHAVES_ITEM = {
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
SUSPEITA = {
    "estabelecimento": "Loja online",
    "data_hora": "2025-03-31T03:10:00",
    "valor": 500.0,
    "modalidade_transacao": "cartao_nao_presente",
}
EXPLICACAO = "Explicação técnica do modelo."

pytest.importorskip("fastapi")


def _base_inventada() -> pd.DataFrame:
    """Dez clientes de março (c01 é a Ana) mais compras de janeiro para o histórico."""
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
    for extra in ("c11", "c12", "c13"):  # uma compra só: ficam sem login
        linhas.append(
            {**linhas[1], "id_transacao": numero, "id_cliente": extra, "id_cartao": f"{extra}-c"}
        )
        numero += 1
    linhas.append(
        {
            **linhas[0],
            "id_transacao": 900,
            "data_hora": pd.Timestamp("2025-01-20 09:00:00"),
            "valor": 80.0,
        }
    )
    return pd.DataFrame(linhas)


# A fila de demonstração: a transação 0 (Ana, BLOQUEAR), a 5 (Carlos, PEDIR_CONFIRMACAO), a 23
# (c11, sem login, BLOQUEAR) e a 24 (c12, sem login, APROVAR). Ana é do Centro e Carlos do Norte
# pela alternação; c11 (posição 10) cai no Centro e c12 (posição 11) no Norte.
FILA = pd.DataFrame(
    [
        {
            "id_transacao": 0,
            "id_cliente": "c01",
            "id_cartao": "c01-debito",
            "nota": 97.5,
            "decisao": "BLOQUEAR",
            "valor": 20.0,
            "data_hora": pd.Timestamp("2025-03-01 09:00:00"),
            "tipo_transacao": "debito",
            "modalidade_transacao": "cartao_presente",
        },
        {
            "id_transacao": 5,
            "id_cliente": "c02",
            "id_cartao": "c02-credito",
            "nota": 55.0,
            "decisao": "PEDIR_CONFIRMACAO",
            "valor": 40.0,
            "data_hora": pd.Timestamp("2025-03-02 09:00:00"),
            "tipo_transacao": "credito",
            "modalidade_transacao": "cartao_presente",
        },
        {
            "id_transacao": 23,
            "id_cliente": "c11",
            "id_cartao": "c11-c",
            "nota": 88.0,
            "decisao": "BLOQUEAR",
            "valor": 40.0,
            "data_hora": pd.Timestamp("2025-03-02 09:00:00"),
            "tipo_transacao": "credito",
            "modalidade_transacao": "cartao_presente",
        },
        {
            "id_transacao": 24,
            "id_cliente": "c12",
            "id_cartao": "c12-c",
            "nota": 3.0,
            "decisao": "APROVAR",
            "valor": 40.0,
            "data_hora": pd.Timestamp("2025-03-02 09:00:00"),
            "tipo_transacao": "credito",
            "modalidade_transacao": "cartao_presente",
        },
    ]
)


def _analise(decisao: str, nota: float) -> dict:
    return {
        "nota": nota,
        "decisao": decisao,
        "decisao_legivel": decisao,
        "sinais": [],
        "explicacao": EXPLICACAO,
        "contribuicoes": [],
        "latencia_ms": 1.0,
    }


def _obter_transacao_falso(id_transacao: int) -> dict:
    linha = FILA[FILA["id_transacao"] == id_transacao]
    if linha.empty:
        raise KeyError(f"Transação {id_transacao} não encontrada na fila.")
    return {"analise": _analise(str(linha.iloc[0]["decisao"]), float(linha.iloc[0]["nota"]))}


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
    import src.api.auditorias as auditoria_mem  # noqa: PLC0415
    import src.api.servicos as sv  # noqa: PLC0415

    decisoes = {0: "BLOQUEAR", 1: "PEDIR_CONFIRMACAO", 2: "APROVAR", 3: "APROVAR", 4: "APROVAR"}
    base = _base_inventada()
    monkeypatch.setattr(notificacoes, "_notificacoes", {})
    monkeypatch.setattr(auditoria_mem, "_auditorias", {})
    repos = dados_demo.montar_repositorios(base, decisoes)
    associado_app.avisar_compras_de_marco(repos)
    monkeypatch.setattr(sessao._estado, "repositorios", repos)
    monkeypatch.setattr(sessao._estado, "tokens", {})
    monkeypatch.setattr(rotas_filial, "_ids_fila", None)
    monkeypatch.setattr(sv._estado, "fila", FILA)
    monkeypatch.setattr(sv._estado, "base", base)
    monkeypatch.setattr(sv, "modelo_carregado", lambda: True)
    monkeypatch.setattr(sv, "obter_transacao", _obter_transacao_falso)
    monkeypatch.setattr(
        sv, "transacao_para_auditoria", lambda id_transacao: {"id_transacao": id_transacao}
    )
    monkeypatch.setattr(sv, "analisar_transacao", lambda t: _analise("PEDIR_CONFIRMACAO", 55.0))
    monkeypatch.setattr(auditoria_mem, "disparar_auditoria_em_segundo_plano", lambda *_: None)
    return repos


def _cabecalho(cliente, id_perfil: str) -> dict[str, str]:
    token = cliente.post("/api/sessao", json={"id_perfil": id_perfil}).json()["token"]
    return {"X-Sessao": token}


def _fila(cliente, id_perfil: str, situacao: str | None = None) -> dict:
    caminho = "/api/filial/fila" + (f"?situacao={situacao}" if situacao else "")
    return cliente.get(caminho, headers=_cabecalho(cliente, id_perfil)).json()


# --- Fila -------------------------------------------------------------------------------------


def test_associado_nao_entra_na_fila_da_filial(cliente):
    assert cliente.get("/api/filial/fila", headers=_cabecalho(cliente, "asc-01")).status_code == 403
    assert cliente.get("/api/filial/fila").status_code == 401


def test_filas_do_centro_e_do_norte_nao_se_cruzam_e_somadas_dao_a_fila_inteira(cliente):
    centro = _fila(cliente, "aud-01")
    norte = _fila(cliente, "ger-02")

    ids_centro = {i["id_compra"] for i in centro["itens"]}
    ids_norte = {i["id_compra"] for i in norte["itens"]}
    assert centro["filial"] == {"id_filial": "fil-centro", "nome": "Agência Centro"}
    assert not ids_centro & ids_norte
    assert centro["total"] + norte["total"] == 3  # as 3 linhas da fila que não foram aprovadas
    assert all(set(i) == CHAVES_ITEM for i in centro["itens"] + norte["itens"])
    assert not _chaves_recursivas(centro) & CHAVES_PROIBIDAS


def test_fila_vem_por_nota_decrescente_com_nome_abreviado_e_final_do_cartao(cliente):
    centro = _fila(cliente, "aud-01")["itens"]

    assert [i["nota"] for i in centro] == [97.5, 88.0]
    assert centro[0]["associado"] == "Ana S."
    assert centro[0]["final_cartao"] == "1111"
    assert centro[1]["associado"] == "Associado 0010"
    assert len(centro[1]["final_cartao"]) == 4 and centro[1]["final_cartao"].isdigit()
    assert centro[0]["veredito_ia"] is None


def test_filtro_de_situacao_e_validado_e_mostra_aprovadas_da_fila(cliente):
    aprovadas = _fila(cliente, "aud-03", "APROVADA")

    assert [i["associado"] for i in aprovadas["itens"]] == ["Associado 0011"]
    assert _fila(cliente, "aud-01", "APROVADA")["total"] == 0
    assert (
        cliente.get(
            "/api/filial/fila?situacao=XYZ", headers=_cabecalho(cliente, "aud-01")
        ).status_code
        == 422
    )


def test_compra_simulada_que_pediu_confirmacao_aparece_na_fila_da_filial_certa(cliente):
    cabecalho = _cabecalho(cliente, "asc-02")  # Carlos, Agência Norte
    cartoes = cliente.get("/api/associado/inicio", headers=cabecalho).json()["cartoes"]
    credito = next(c["id"] for c in cartoes if c["tipo"] == "credito")
    compra = cliente.post(
        "/api/associado/compras", json={"cartao": credito, **SUSPEITA}, headers=cabecalho
    ).json()["compra"]

    norte = _fila(cliente, "aud-03")["itens"]
    centro = _fila(cliente, "aud-01")["itens"]

    item = next(i for i in norte if i["id_compra"] == compra["id_compra"])
    assert item["situacao"] == "AGUARDANDO"
    assert item["associado"] == "Carlos L."
    assert item["nota"] == 55.0
    assert compra["id_compra"] not in {i["id_compra"] for i in centro}


def test_veredito_da_ia_aparece_quando_a_auditoria_conclui(cliente):
    import src.api.auditorias as auditoria_mem  # noqa: PLC0415

    auditoria_mem.registrar_auditoria(
        "trans_0",
        {
            "id_auditoria": "trans_0",
            "status": "concluida",
            "relatorio": {"parecer": "CONFIRMA"},
            "latencia_ms": 1.0,
            "mensagem": None,
        },
    )

    centro = _fila(cliente, "aud-01")["itens"]

    assert centro[0]["veredito_ia"] == "CONFIRMA"


# --- Detalhe ----------------------------------------------------------------------------------


def test_detalhe_traz_analise_historico_agregado_e_bloqueio_tecnico_sem_dados_do_saldo(cliente):
    cabecalho = _cabecalho(cliente, "aud-01")
    item = _fila(cliente, "aud-01")["itens"][0]

    corpo = cliente.get(f"/api/filial/compras/{item['id_compra']}", headers=cabecalho).json()

    assert set(corpo) == {
        "compra",
        "analise",
        "auditoria",
        "associado",
        "resposta_associado",
        "bloqueio",
    }
    assert corpo["analise"]["decisao"] == "BLOQUEAR"
    assert corpo["associado"] == {
        "nome_abreviado": "Ana S.",
        "final_cartao": "1111",
        "historico": {"compras_90d": 1, "valor_mediano": 80.0, "contestacoes": 0},
    }
    assert corpo["bloqueio"] == {
        "por": "Sentinela",
        "em": corpo["bloqueio"]["em"],
        "motivo": EXPLICACAO,
    }
    assert corpo["auditoria"]["status"] == "pendente"
    assert not _chaves_recursivas(corpo) & (CHAVES_PROIBIDAS | CHAVES_LGPD)


def test_detalhe_dispara_a_auditoria_da_compra_de_marco_uma_unica_vez(cliente, monkeypatch):
    import src.api.auditorias as auditoria_mem  # noqa: PLC0415

    disparos: list[str] = []
    monkeypatch.setattr(
        auditoria_mem,
        "disparar_auditoria_em_segundo_plano",
        lambda id_auditoria, *_: disparos.append(id_auditoria),
    )
    cabecalho = _cabecalho(cliente, "aud-01")
    item = _fila(cliente, "aud-01")["itens"][0]

    cliente.get(f"/api/filial/compras/{item['id_compra']}", headers=cabecalho)
    cliente.get(f"/api/filial/compras/{item['id_compra']}", headers=cabecalho)

    assert disparos == ["trans_0"]


def test_compra_de_outra_filial_403_e_inexistente_404(cliente):
    item = _fila(cliente, "aud-01")["itens"][0]

    assert (
        cliente.get(
            f"/api/filial/compras/{item['id_compra']}", headers=_cabecalho(cliente, "aud-03")
        ).status_code
        == 403
    )
    assert (
        cliente.get(
            "/api/filial/compras/cmp-999999", headers=_cabecalho(cliente, "aud-01")
        ).status_code
        == 404
    )
    assert (
        cliente.get(
            f"/api/filial/compras/{item['id_compra']}", headers=_cabecalho(cliente, "asc-01")
        ).status_code
        == 403
    )


def test_detalhe_mostra_a_resposta_do_associado_e_a_contestacao_entra_na_fila(cliente):
    cabecalho_ana = _cabecalho(cliente, "asc-01")
    pendente = cliente.get("/api/associado/inicio", headers=cabecalho_ana).json()["pendentes"][0]
    cliente.post(
        f"/api/notificacoes/{pendente['id_notificacao']}/resposta", json={"resposta": "nao"}
    )
    aprovada = cliente.get(
        "/api/associado/extrato?situacao=APROVADA", headers=cabecalho_ana
    ).json()["itens"][0]
    cliente.post(
        f"/api/associado/compras/{aprovada['id_compra']}/contestacao", headers=cabecalho_ana
    )

    detalhe = cliente.get(
        f"/api/filial/compras/{pendente['id_compra']}", headers=_cabecalho(cliente, "aud-02")
    ).json()
    fila = _fila(cliente, "ger-01")["itens"]

    assert detalhe["resposta_associado"]["resposta"] == "nao"
    assert detalhe["compra"]["situacao"] == "BLOQUEADA"
    assert detalhe["associado"]["historico"]["contestacoes"] == 1
    assert any(
        i["id_compra"] == aprovada["id_compra"] and i["situacao"] == "CONTESTADA" for i in fila
    )


# --- Bloqueio pelo auditor (Issue #102) -------------------------------------------------------
# cmp-000002 é a compra de março da Ana que aguarda o associado, com aviso, na Agência Centro.


def _bloquear(cliente, id_perfil: str = "aud-01", id_compra: str = "cmp-000002", nota=None):
    return cliente.post(
        f"/api/filial/compras/{id_compra}/bloqueio",
        json={"nota": nota},
        headers=_cabecalho(cliente, id_perfil),
    )


def test_auditor_bloqueia_compra_aguardando_com_nome_data_e_motivo(cliente):
    resposta = _bloquear(cliente, nota="Associado viaja pouco.")

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["compra"]["situacao"] == "BLOQUEADA"
    assert corpo["bloqueio"]["por"] == "Rafael Moura"
    assert corpo["bloqueio"]["motivo"] == f"{EXPLICACAO} Nota do analista: Associado viaja pouco."
    assert corpo["bloqueio"]["em"]


def test_motivo_usa_a_explicacao_da_ia_quando_a_auditoria_ja_terminou(cliente):
    import src.api.auditorias as auditoria_mem  # noqa: PLC0415

    auditoria_mem.registrar_auditoria(
        "trans_1",
        {
            "id_auditoria": "trans_1",
            "status": "concluida",
            "relatorio": {"parecer": "CONFIRMA", "explicacao": "A IA viu um padrão estranho."},
            "latencia_ms": 1.0,
            "mensagem": None,
        },
    )

    corpo = _bloquear(cliente).json()

    assert corpo["bloqueio"]["motivo"] == "A IA viu um padrão estranho."


def test_associado_ve_analista_da_agencia_e_motivo_generico_nunca_o_nome(cliente):
    _bloquear(cliente, nota="Nota interna.")

    detalhe = cliente.get(
        "/api/associado/compras/cmp-000002", headers=_cabecalho(cliente, "asc-01")
    ).json()

    assert detalhe["situacao"] == "BLOQUEADA"
    assert detalhe["bloqueio"]["por"] == "Analista da agência Agência Centro"
    assert detalhe["bloqueio"]["motivo"] == associado_app.MOTIVO_GENERICO
    assert "Rafael" not in str(detalhe)
    assert "Nota interna" not in str(detalhe)


@pytest.mark.parametrize("id_perfil", ["ger-01", "asc-01"])
def test_so_o_auditor_bloqueia(cliente, id_perfil):
    assert _bloquear(cliente, id_perfil).status_code == 403


def test_auditor_de_outra_filial_recebe_403_e_compra_inexistente_404(cliente):
    assert _bloquear(cliente, "aud-03").status_code == 403
    assert _bloquear(cliente, id_compra="cmp-999999").status_code == 404


def test_compra_que_nao_aguarda_o_associado_responde_409(cliente):
    assert _bloquear(cliente, id_compra="cmp-000001").status_code == 409  # já BLOQUEADA
    assert _bloquear(cliente, id_compra="cmp-000003").status_code == 409  # APROVADA
    assert _bloquear(cliente).status_code == 201
    assert _bloquear(cliente).status_code == 409  # bloquear duas vezes


def test_nota_com_mais_de_300_caracteres_responde_422(cliente):
    assert _bloquear(cliente, nota="x" * 301).status_code == 422
    assert _bloquear(cliente, nota="x" * 300).status_code == 201


def _responder_aviso(cliente, resposta: str) -> None:
    aviso = notificacoes.listar()
    id_aviso = next(
        a["id_notificacao"]
        for a in aviso
        if a["status"] == "aguardando" and a["tipo"] == "CONFIRMACAO"
    )
    cliente.post(f"/api/notificacoes/{id_aviso}/resposta", json={"resposta": resposta})


def test_fui_eu_depois_do_bloqueio_libera_sozinho_e_conta_incorreto(cliente, ambiente):
    limite_antes = ambiente.associados.obter("asc-01").limite_disponivel
    _bloquear(cliente)

    _responder_aviso(cliente, "sim")
    compra = ambiente.compras.obter("cmp-000002")

    assert compra.situacao == "APROVADA"
    assert compra.bloqueio.correto is False
    # Compra de março: já está no saldo inicial, então o limite não muda (seção 17.1).
    assert ambiente.associados.obter("asc-01").limite_disponivel == limite_antes


def test_liberacao_de_compra_simulada_aplica_o_saldo_uma_unica_vez(cliente, ambiente):
    cabecalho = _cabecalho(cliente, "asc-01")
    compra = cliente.post(
        "/api/associado/compras", json={"cartao": "car-01-c", **SUSPEITA}, headers=cabecalho
    ).json()["compra"]
    limite_antes = ambiente.associados.obter("asc-01").limite_disponivel
    _bloquear(cliente, id_compra=compra["id_compra"])

    rota = f"/api/notificacoes/{compra['id_notificacao']}/resposta"
    cliente.post(rota, json={"resposta": "sim"})
    cliente.post(rota, json={"resposta": "sim"})

    assert ambiente.compras.obter(compra["id_compra"]).situacao == "APROVADA"
    assert ambiente.associados.obter("asc-01").limite_disponivel == pytest.approx(
        limite_antes - SUSPEITA["valor"]
    )


def test_nao_fui_eu_depois_do_bloqueio_mantem_bloqueada_e_conta_correto(cliente, ambiente):
    _bloquear(cliente)

    _responder_aviso(cliente, "nao")
    compra = ambiente.compras.obter("cmp-000002")

    assert compra.situacao == "BLOQUEADA"
    assert compra.bloqueio.correto is True
