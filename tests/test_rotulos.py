"""Testes dos rótulos de retorno para o retreino (Issue #127), com dados inventados."""

from __future__ import annotations

import csv

import pandas as pd
import pytest

from src import exportar_retreino
from src.adaptadores.arquivo.rotulos import COLUNAS, RotulosEmArquivo
from src.adaptadores.memoria import dados_demo
from src.api import sessao
from src.aplicacao import associado as associado_app
from src.associado import notificacoes
from src.config import VARIAVEIS_MODELO
from src.dominio.rotulos import EventoRotulo, rotulo_do_evento

PROIBIDAS = {"nome", "id_cartao", "id_cliente", "id_estabelecimento", "associado"}
VARIAVEIS = {nome: float(i) for i, nome in enumerate(VARIAVEIS_MODELO)}


def _evento(id_compra: str = "cmp-000001", origem: str = "resposta_aviso", resposta="nao"):
    return EventoRotulo(
        registrado_em="2025-03-31T10:00:00",
        origem=origem,
        id_compra=id_compra,
        id_transacao=None,
        simulada=True,
        nota=55.0,
        decisao_modelo="PEDIR_CONFIRMACAO",
        situacao="BLOQUEADA",
        resposta=resposta,
        rotulo=rotulo_do_evento(origem, resposta),
        data_hora="2025-03-31T03:10:00",
        valor=0.0,
        tipo_transacao="credito",
        modalidade_transacao="cartao_nao_presente",
        variaveis=VARIAVEIS,
    )


# --- Regra do rótulo --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("origem", "resposta", "rotulo"),
    [
        ("resposta_aviso", "nao", "fraude"),
        ("resposta_aviso", "sim", "legitima"),
        ("contestacao", None, "fraude"),
        ("bloqueio_auditor", None, None),
        ("bloqueio_auditor", "nao", "fraude"),
    ],
)
def test_tabela_de_rotulos(origem, resposta, rotulo):
    assert rotulo_do_evento(origem, resposta) == rotulo


def test_origem_desconhecida_e_recusada():
    with pytest.raises(ValueError, match="Origem"):
        _evento(origem="palpite")


# --- Adaptador em arquivo ---------------------------------------------------------------------


def test_eventos_sobrevivem_a_recriar_o_adaptador(tmp_path):
    caminho = tmp_path / "rotulos.csv"
    RotulosEmArquivo(caminho).acrescentar(_evento("cmp-000001"))

    reiniciado = RotulosEmArquivo(caminho)
    reiniciado.acrescentar(_evento("cmp-000002", resposta="sim"))

    eventos = RotulosEmArquivo(caminho).listar()
    assert [e.id_compra for e in eventos] == ["cmp-000001", "cmp-000002"]
    assert eventos[1].rotulo == "legitima"
    assert eventos[0].variaveis == VARIAVEIS
    assert eventos[0].id_transacao is None and eventos[0].simulada is True


def test_csv_tem_cabecalho_uma_vez_e_nenhuma_coluna_proibida(tmp_path):
    caminho = tmp_path / "rotulos.csv"
    adaptador = RotulosEmArquivo(caminho)
    adaptador.acrescentar(_evento("cmp-000001"))
    adaptador.acrescentar(_evento("cmp-000002"))

    with caminho.open(encoding="utf-8") as arquivo:
        linhas = list(csv.reader(arquivo))

    assert linhas[0] == list(COLUNAS)
    assert len(linhas) == 3
    assert not PROIBIDAS & set(linhas[0])
    assert set(VARIAVEIS_MODELO) <= set(linhas[0])


def test_listar_sem_arquivo_devolve_lista_vazia(tmp_path):
    assert RotulosEmArquivo(tmp_path / "nao-existe.csv").listar() == []


# --- Exportação -------------------------------------------------------------------------------


def test_exportacao_fica_com_o_ultimo_evento_e_descarta_os_sem_rotulo():
    eventos = [
        _evento("cmp-000001", resposta="sim"),
        _evento("cmp-000002", origem="bloqueio_auditor", resposta=None),
        _evento("cmp-000001", origem="contestacao", resposta=None),
    ]

    base = exportar_retreino.montar_base_retreino(eventos)

    assert len(base) == 1
    assert base.iloc[0]["rotulo_retorno"] == 1
    assert list(base.columns) == [*VARIAVEIS_MODELO, "data_hora", "rotulo_retorno"]


def test_base_exportada_tem_as_variaveis_que_o_treino_le(tmp_path, monkeypatch):
    caminho = tmp_path / "rotulos.csv"
    adaptador = RotulosEmArquivo(caminho)
    adaptador.acrescentar(_evento("cmp-000001", resposta="nao"))
    adaptador.acrescentar(_evento("cmp-000002", resposta="sim"))
    monkeypatch.setattr(exportar_retreino, "obter_rotulos", lambda: adaptador)
    monkeypatch.setattr(exportar_retreino, "CAMINHO_RETREINO", tmp_path / "retreino.parquet")

    exportar_retreino.exportar()
    base = pd.read_parquet(tmp_path / "retreino.parquet")

    assert base[list(VARIAVEIS_MODELO)].dtypes.eq("float64").all()
    assert sorted(base["rotulo_retorno"]) == [0, 1]
    assert not PROIBIDAS & set(base.columns)


# --- Gravação pelas rotas ---------------------------------------------------------------------

pytest.importorskip("fastapi")
SUSPEITA = {
    "estabelecimento": "Loja online",
    "data_hora": "2025-03-31T03:10:00",
    "valor": 500.0,
    "nao_presente": 1,
    "modalidade_transacao": "cartao_nao_presente",
}


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
                    **{
                        v: 1.0
                        for v in VARIAVEIS_MODELO
                        if v not in ("valor", "risco_estabelecimento")
                    },
                }
            )
    return pd.DataFrame(linhas)


def _analise(transacao: dict) -> dict:
    decisao = "PEDIR_CONFIRMACAO" if (transacao.get("valor") or 0) >= 300 else "APROVAR"
    return {
        "nota": 61.5,
        "decisao": decisao,
        "decisao_legivel": decisao,
        "sinais": [],
        "explicacao": "x",
        "contribuicoes": [],
        "latencia_ms": 1.0,
    }


@pytest.fixture(scope="module")
def cliente():
    from fastapi.testclient import TestClient  # noqa: PLC0415

    from src.api.app import app  # noqa: PLC0415

    with TestClient(app) as cliente_teste:
        yield cliente_teste


@pytest.fixture
def repos(monkeypatch):
    import src.api.auditorias as auditoria_mem  # noqa: PLC0415
    import src.api.servicos as sv  # noqa: PLC0415

    monkeypatch.setattr(notificacoes, "_notificacoes", {})
    repositorios = dados_demo.montar_repositorios(_base_inventada(), {0: "APROVAR", 1: "APROVAR"})
    associado_app.avisar_compras_de_marco(repositorios)
    monkeypatch.setattr(sessao._estado, "repositorios", repositorios)
    monkeypatch.setattr(sessao._estado, "tokens", {})
    monkeypatch.setattr(sv, "modelo_carregado", lambda: True)
    monkeypatch.setattr(sv, "analisar_transacao", _analise)
    monkeypatch.setattr(auditoria_mem, "disparar_auditoria_em_segundo_plano", lambda *_: None)
    return repositorios


def _cabecalho(cliente, id_perfil: str = "asc-01") -> dict[str, str]:
    return {"X-Sessao": cliente.post("/api/sessao", json={"id_perfil": id_perfil}).json()["token"]}


def test_responder_ao_aviso_grava_um_evento_com_as_variaveis(cliente, repos):
    compra = cliente.post(
        "/api/associado/compras",
        json={"cartao": "car-01-c", **SUSPEITA},
        headers=_cabecalho(cliente),
    ).json()["compra"]

    cliente.post(f"/api/notificacoes/{compra['id_notificacao']}/resposta", json={"resposta": "nao"})
    eventos = repos.rotulos.listar()

    assert len(eventos) == 1
    evento = eventos[0]
    assert (evento.origem, evento.resposta, evento.rotulo) == ("resposta_aviso", "nao", "fraude")
    assert (evento.nota, evento.decisao_modelo, evento.situacao) == (
        61.5,
        "PEDIR_CONFIRMACAO",
        "BLOQUEADA",
    )
    assert evento.variaveis["valor"] == 500.0
    assert evento.variaveis["madrugada"] == 1
    assert evento.variaveis["credito"] == 1
    assert evento.simulada is True and evento.id_transacao is None


def test_contestar_compra_de_marco_grava_fraude_com_as_variaveis_da_base(cliente, repos):
    cabecalho = _cabecalho(cliente)
    aprovada = cliente.get("/api/associado/extrato?situacao=APROVADA", headers=cabecalho).json()[
        "itens"
    ][-1]

    cliente.post(f"/api/associado/compras/{aprovada['id_compra']}/contestacao", headers=cabecalho)
    evento = repos.rotulos.listar()[-1]

    assert (evento.origem, evento.rotulo, evento.situacao) == (
        "contestacao",
        "fraude",
        "CONTESTADA",
    )
    assert evento.id_transacao is not None and evento.simulada is False
    assert evento.variaveis["valor"] == 25.0


def test_bloqueio_do_auditor_grava_evento_sem_rotulo(cliente, repos, monkeypatch):
    from src.api import rotas_filial  # noqa: PLC0415

    monkeypatch.setattr(rotas_filial, "_ids_fila", set())
    compra = cliente.post(
        "/api/associado/compras",
        json={"cartao": "car-01-c", **SUSPEITA},
        headers=_cabecalho(cliente),
    ).json()["compra"]

    cliente.post(
        f"/api/filial/compras/{compra['id_compra']}/bloqueio",
        json={"nota": None},
        headers=_cabecalho(cliente, "aud-01"),
    )
    evento = repos.rotulos.listar()[-1]

    assert (evento.origem, evento.rotulo, evento.situacao) == (
        "bloqueio_auditor",
        None,
        "BLOQUEADA",
    )
