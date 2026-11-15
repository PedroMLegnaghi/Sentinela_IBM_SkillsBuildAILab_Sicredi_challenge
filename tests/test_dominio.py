"""Testes do domínio, das portas e do adaptador em memória (Issue #92), com dados inventados."""

from __future__ import annotations

import ast
from pathlib import Path

import pandas as pd
import pytest

from src import composicao
from src.adaptadores.memoria import dados_demo
from src.adaptadores.memoria.repositorios import criar_repositorios_vazios
from src.dominio import regras
from src.dominio.entidades import Associado, Cartao, Compra, Funcionario, Perfil
from src.portas.repositorios import RepositorioCompras, Repositorios

RAIZ = Path(__file__).resolve().parents[1]
MODULOS_PROTEGIDOS = ("pandas", "fastapi", "src.adaptadores")


def _associado(saldo: float = 1000.0, limite: float = 500.0) -> Associado:
    return Associado("asc-01", "Ana Souza", "fil-centro", 0, True, saldo, 3000.0, limite)


def _cartao(tipo: str = "debito") -> Cartao:
    return Cartao(f"car-01-{tipo[0]}", "asc-01", tipo, "1111")


def _compra(situacao: str = "APROVADA", valor: float = 100.0, tipo: str = "debito") -> Compra:
    return Compra(
        id_compra="cmp-000001",
        id_associado="asc-01",
        id_filial="fil-centro",
        id_cartao=f"car-01-{tipo[0]}",
        estabelecimento="Mercado Bom Preço",
        data_hora="2025-03-31T10:00:00",
        valor=valor,
        tipo_transacao=tipo,
        modalidade_transacao="cartao_presente",
        situacao=situacao,
        simulada=True,
    )


# --- Situação ---------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("decisao", "situacao"),
    [("APROVAR", "APROVADA"), ("PEDIR_CONFIRMACAO", "AGUARDANDO"), ("BLOQUEAR", "BLOQUEADA")],
)
def test_situacao_inicial_segue_a_decisao_do_modelo(decisao, situacao):
    assert regras.situacao_inicial(decisao) == situacao


def test_decisao_desconhecida_e_recusada():
    with pytest.raises(ValueError, match="desconhecida"):
        regras.situacao_inicial("TALVEZ")


def test_compra_nasce_so_com_situacao_conhecida():
    with pytest.raises(ValueError, match="Situação"):
        _compra(situacao="PENDENTE")


# --- Saldo e limite ---------------------------------------------------------------------------


def test_compra_aprovada_no_debito_desconta_o_saldo():
    associado = _associado(saldo=1000.0)
    compra = _compra(valor=49.9)

    assert regras.aplicar_no_saldo(associado, _cartao("debito"), compra)
    assert associado.saldo == 950.1
    assert associado.limite_disponivel == 500.0


def test_compra_aprovada_no_credito_consome_o_limite():
    associado = _associado(limite=500.0)
    compra = _compra(valor=120.0, tipo="credito")

    assert regras.aplicar_no_saldo(associado, _cartao("credito"), compra)
    assert associado.limite_disponivel == 380.0
    assert associado.saldo == 1000.0


@pytest.mark.parametrize("situacao", ["AGUARDANDO", "BLOQUEADA", "CONTESTADA"])
def test_compra_nao_aprovada_nao_mexe_em_nada(situacao):
    associado = _associado()

    assert not regras.aplicar_no_saldo(associado, _cartao(), _compra(situacao=situacao))
    assert (associado.saldo, associado.limite_disponivel) == (1000.0, 500.0)


def test_saldo_e_aplicado_uma_unica_vez():
    associado = _associado()
    compra = _compra(valor=10.0)

    regras.aplicar_no_saldo(associado, _cartao(), compra)
    assert not regras.aplicar_no_saldo(associado, _cartao(), compra)
    assert associado.saldo == 990.0


def test_compra_de_marco_aprovada_nao_desconta_de_novo():
    associado = _associado()
    compra = _compra(valor=10.0)
    compra.simulada = False

    assert not regras.aplicar_no_saldo(associado, _cartao(), compra)
    assert associado.saldo == 1000.0


def test_devolver_ao_saldo_desfaz_a_aplicacao():
    associado = _associado()
    compra = _compra(valor=10.0)
    regras.aplicar_no_saldo(associado, _cartao(), compra)

    assert regras.devolver_ao_saldo(associado, _cartao(), compra)
    assert associado.saldo == 1000.0
    assert not regras.devolver_ao_saldo(associado, _cartao(), compra)


# --- Resposta ao aviso e contestação ----------------------------------------------------------


@pytest.mark.parametrize(("resposta", "situacao"), [("sim", "APROVADA"), ("nao", "BLOQUEADA")])
def test_resposta_numa_compra_aguardando_muda_a_situacao(resposta, situacao):
    compra = _compra(situacao="AGUARDANDO")

    assert regras.aplicar_resposta(compra, resposta, "2025-03-31T10:05:00") == situacao
    assert compra.resposta_associado.resposta == resposta


def test_resposta_numa_compra_bloqueada_pelo_sentinela_nao_muda_a_situacao():
    compra = _compra(situacao="BLOQUEADA")

    assert regras.aplicar_resposta(compra, "sim", "2025-03-31T10:05:00") == "BLOQUEADA"


def test_resposta_invalida_e_recusada():
    with pytest.raises(ValueError, match="sim"):
        regras.aplicar_resposta(_compra(situacao="AGUARDANDO"), "talvez", "2025-03-31T10:05:00")


def test_contestar_bloqueia_o_cartao_e_devolve_o_valor():
    compra, cartao = _compra(valor=80.0), _cartao()

    contestacao = regras.contestar(compra, cartao, "2025-03-31T11:00:00", "ctt-0001")

    assert compra.situacao == "CONTESTADA"
    assert cartao.bloqueado
    assert contestacao.valor_devolvido == 80.0
    assert contestacao.id_compra == "cmp-000001"


@pytest.mark.parametrize("situacao", ["AGUARDANDO", "BLOQUEADA", "CONTESTADA"])
def test_so_compra_aprovada_pode_ser_contestada(situacao):
    with pytest.raises(ValueError, match="aprovada"):
        regras.contestar(_compra(situacao=situacao), _cartao(), "2025-03-31T11:00:00", "ctt-0001")


# --- Nomes e carteira -------------------------------------------------------------------------


def test_nome_abreviado_preserva_o_associado_sem_login():
    assert regras.nome_abreviado("Ana Souza") == "Ana S."
    assert regras.nome_abreviado("Associado 0421") == "Associado 0421"
    assert regras.nome_abreviado("Ana") == "Ana"


def test_carteira_e_dividida_pela_posicao_na_ordem_do_identificador():
    distribuicao = regras.distribuir_carteira(["c3", "c1", "c2", "c1", "c5", "c4", "c6", "c7"])

    assert [ident for ident, _, _ in distribuicao] == ["c1", "c2", "c3", "c4", "c5", "c6", "c7"]
    assert distribuicao[0][2] == "fil-centro"
    assert distribuicao[1][2] == "fil-norte"
    centro = sum(1 for _, _, filial in distribuicao if filial == "fil-centro")
    assert abs(centro - (len(distribuicao) - centro)) <= 1


# --- Dados de demonstração --------------------------------------------------------------------


def _base_inventada() -> pd.DataFrame:
    """Treze clientes com compras em março; 'c11' é o maior, 'c01' e 'c02' empatam em segundo."""
    linhas = []
    quantidades = {
        "c11": 6,
        "c02": 3,
        "c01": 3,
        **{f"c{n:02d}": 1 for n in range(3, 11)},
        "c12": 1,
        "c13": 1,
    }
    numero = 0
    for cliente, quantidade in quantidades.items():
        for i in range(quantidade):
            tipo = "debito" if i % 2 == 0 else "credito"
            linhas.append(
                {
                    "id_transacao": numero,
                    "data_hora": pd.Timestamp(f"2025-03-{(i % 28) + 1:02d} 10:00:00"),
                    "id_cartao": f"{cliente}-{tipo}",
                    "id_cliente": cliente,
                    "valor": 10.0 * (i + 1),
                    "tipo_transacao": tipo,
                    "modalidade_transacao": "cartao_presente",
                    "risco_estabelecimento": [5.0, 15.0, 25.0, 35.0, 50.0, float("nan")][i % 6],
                }
            )
            numero += 1
    linhas.append(
        {**linhas[0], "id_transacao": 900, "data_hora": pd.Timestamp("2025-02-10 10:00:00")}
    )
    linhas.append({**linhas[0], "id_transacao": 901, "data_hora": pd.NaT, "id_cliente": "c99"})
    return pd.DataFrame(linhas)


@pytest.fixture(scope="module")
def repos() -> Repositorios:
    decisoes = {0: "BLOQUEAR", 1: "PEDIR_CONFIRMACAO", 2: "APROVAR", 3: "APROVAR"}
    return dados_demo.montar_repositorios(_base_inventada(), decisoes)


def test_filiais_funcionarios_e_perfis_sao_os_da_especificacao(repos):
    perfis = repos.perfis.listar()

    assert {f.nome for f in repos.filiais.listar()} == {"Agência Centro", "Agência Norte"}
    assert [p.papel for p in perfis].count("gerente") == 2
    assert [p.papel for p in perfis].count("auditor") == 4
    assert [p.papel for p in perfis].count("associado") == 10
    assert repos.perfis.obter("aud-03") == Funcionario(
        "aud-03", "Tiago Nunes", "auditor", "fil-norte"
    )


def test_associados_com_login_alternam_filial_e_saldo_segue_a_regra(repos):
    ana, carlos = repos.associados.obter("asc-01"), repos.associados.obter("asc-02")

    assert (ana.nome, ana.id_filial, ana.saldo) == ("Ana Souza", "fil-centro", 4820.35)
    assert (carlos.nome, carlos.id_filial, carlos.saldo) == ("Carlos Lima", "fil-norte", 4510.35)
    assert (ana.limite_total, ana.limite_disponivel) == (3000.0, 2150.0)
    assert repos.associados.obter("asc-10").nome == "João Martins"


def test_login_vai_para_os_clientes_com_mais_compras_com_desempate_pelo_identificador(repos):
    assert repos.associados.obter("asc-01").id_cliente_base == "c11"
    assert repos.associados.obter("asc-02").id_cliente_base == "c01"
    assert repos.associados.obter("asc-03").id_cliente_base == "c02"


def test_cartoes_tem_finais_da_regra_e_ligam_aos_cartoes_reais_do_mesmo_tipo(repos):
    cartoes = {c.tipo: c for c in repos.cartoes.listar_por_associado("asc-01")}

    assert cartoes["debito"].id_cartao == "car-01-d"
    assert (cartoes["debito"].final, cartoes["credito"].final) == ("1111", "4821")
    assert cartoes["debito"].ids_cartao_base == ("c11-debito",)
    assert repos.cartoes.obter("car-02-c").final == "4828"


def test_cliente_sem_login_entra_na_carteira_pela_posicao(repos):
    sem_login = [a for a in repos.associados.listar_por_filial("fil-centro") if not a.tem_login]
    sem_login += [a for a in repos.associados.listar_por_filial("fil-norte") if not a.tem_login]

    assert len(sem_login) == 3
    assert all(a.nome == f"Associado {a.posicao:04d}" for a in sem_login)
    assert all(regras.filial_da_posicao(a.posicao) == a.id_filial for a in sem_login)
    assert "c99" not in {a.id_cliente_base for a in repos.associados.listar_por_filial("fil-norte")}


def test_compras_de_marco_entram_com_a_situacao_da_decisao_e_estabelecimento_ficticio(repos):
    compras = repos.compras.listar_por_associado("asc-01")

    assert [c.situacao for c in compras] == ["BLOQUEADA", "AGUARDANDO", "APROVADA", "APROVADA"]
    assert [c.estabelecimento for c in compras][:3] == [
        "Mercado Bom Preço",
        "Farmácia Vida",
        "Posto Avenida",
    ]
    assert compras[0].id_compra == "cmp-000001"
    assert compras[1].id_cartao == "car-01-c"
    assert compras[0].data_hora == "2025-03-01T10:00:00"
    assert repos.compras.listar_por_filial("fil-norte") == []


def test_nome_do_estabelecimento_sem_risco_e_loja_online():
    assert dados_demo.nome_do_estabelecimento(float("nan")) == "Loja online"
    assert dados_demo.nome_do_estabelecimento(None) == "Loja online"
    assert dados_demo.nome_do_estabelecimento(82) == "Eletrônicos Web"


def test_sem_parquet_a_demonstracao_sobe_so_com_os_dados_inventados(monkeypatch, tmp_path):
    monkeypatch.setattr(composicao, "CAMINHO_PREPARADO", tmp_path / "nao-existe.parquet")

    repos_sem_base = composicao.obter_repositorios()

    assert len(repos_sem_base.perfis.listar()) == 16
    assert repos_sem_base.associados.obter("asc-01").id_cliente_base is None
    assert len(repos_sem_base.cartoes.listar_por_associado("asc-10")) == 2


# --- Arquitetura e privacidade ----------------------------------------------------------------


def _imports(arquivo: Path) -> set[str]:
    arvore = ast.parse(arquivo.read_text(encoding="utf-8"))
    nomes: set[str] = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            nomes |= {alias.name for alias in no.names}
        elif isinstance(no, ast.ImportFrom) and no.module:
            nomes.add(no.module)
    return nomes


@pytest.mark.parametrize("pasta", ["src/dominio", "src/portas"])
def test_dominio_e_portas_nao_dependem_de_pandas_fastapi_nem_adaptadores(pasta):
    for arquivo in (RAIZ / pasta).glob("*.py"):
        proibidos = [
            m
            for m in _imports(arquivo)
            if m.split(".")[0] in ("pandas", "fastapi") or m.startswith("src.adaptadores")
        ]
        assert not proibidos, f"{arquivo.name} importa {proibidos}"


def test_identificadores_da_base_ficam_fora_do_repr_das_entidades(repos):
    associado = repos.associados.obter("asc-01")
    cartao = repos.cartoes.obter("car-01-d")
    compra = repos.compras.listar_por_associado("asc-01")[0]

    assert "c11" not in repr(associado) and "c11" not in str(associado)
    assert "c11-debito" not in repr(cartao)
    assert "id_transacao_base" not in repr(compra)


class _ComprasDuble:
    """Dublê mínimo da porta de compras, para mostrar que as regras não dependem do adaptador."""

    def __init__(self) -> None:
        self.gravadas: list[Compra] = []

    def obter(self, id_compra: str) -> Compra | None:
        return next((c for c in self.gravadas if c.id_compra == id_compra), None)

    def obter_por_notificacao(self, id_notificacao: str) -> Compra | None:
        return None

    def listar_por_associado(self, id_associado: str) -> list[Compra]:
        return list(self.gravadas)

    def listar_por_filial(self, id_filial: str) -> list[Compra]:
        return list(self.gravadas)

    def salvar(self, compra: Compra) -> None:
        self.gravadas.append(compra)

    def proximo_id(self) -> str:
        return f"cmp-{len(self.gravadas) + 1:06d}"


def test_um_duble_substitui_o_repositorio_sem_mexer_nas_regras():
    duble = _ComprasDuble()
    repos_com_duble = Repositorios(**{**vars(criar_repositorios_vazios()), "compras": duble})
    compra = _compra()
    repos_com_duble.compras.salvar(compra)

    contestacao = regras.contestar(
        repos_com_duble.compras.obter("cmp-000001"), _cartao(), "2025-03-31T11:00:00", "ctt-0001"
    )

    assert isinstance(duble, RepositorioCompras)
    assert contestacao.id_compra == "cmp-000001"
    assert duble.gravadas[0].situacao == "CONTESTADA"


def test_perfil_so_aceita_papel_conhecido():
    with pytest.raises(ValueError, match="Papel"):
        Perfil("x", "Alguém", "cliente", "fil-centro")
    with pytest.raises(ValueError, match="auditor ou gerente"):
        Funcionario("x", "Alguém", "associado", "fil-centro")
