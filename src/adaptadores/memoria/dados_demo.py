"""Dados de demonstração do associado e da filial (ESPECIFICACAO, seção 17.2; Issue #92).

Filiais, funcionários, nomes, saldos e limites são inventados. Cada associado com login é
ligado a um cliente real de março (os 10 com mais compras) para ter extrato e histórico; os
demais clientes de março entram na carteira da filial como "Associado NNNN".
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

import pandas as pd

from src.adaptadores.memoria.repositorios import criar_repositorios_vazios
from src.config import FIM_TESTE, INICIO_TESTE, VARIAVEIS_MODELO
from src.dominio.entidades import Associado, Cartao, Compra, Filial, Funcionario
from src.dominio.regras import distribuir_carteira, filial_da_posicao, situacao_inicial
from src.portas.repositorios import Repositorios

FILIAIS = (Filial("fil-centro", "Agência Centro"), Filial("fil-norte", "Agência Norte"))
FUNCIONARIOS = (
    Funcionario("ger-01", "Helena Castro", "gerente", "fil-centro"),
    Funcionario("aud-01", "Rafael Moura", "auditor", "fil-centro"),
    Funcionario("aud-02", "Júlia Prates", "auditor", "fil-centro"),
    Funcionario("ger-02", "Marcos Viana", "gerente", "fil-norte"),
    Funcionario("aud-03", "Tiago Nunes", "auditor", "fil-norte"),
    Funcionario("aud-04", "Paula Reis", "auditor", "fil-norte"),
)
NOMES_COM_LOGIN = (
    "Ana Souza",
    "Carlos Lima",
    "Bruno Teixeira",
    "Fernanda Alves",
    "Carla Mendes",
    "Gustavo Pires",
    "Diego Prado",
    "Isabela Costa",
    "Elisa Rocha",
    "João Martins",
)
SALDO_INICIAL = 4820.35
PASSO_SALDO = 310.0
LIMITE_TOTAL = 3000.0
LIMITE_DISPONIVEL = 2150.0
FINAL_DEBITO_BASE, PASSO_FINAL_DEBITO = 1111, 111
FINAL_CREDITO_BASE, PASSO_FINAL_CREDITO = 4821, 7
# Nome fictício do estabelecimento pela faixa de risco (limite superior exclusivo)
ESTABELECIMENTOS_POR_RISCO = (
    (12, "Mercado Bom Preço"),
    (19, "Farmácia Vida"),
    (29, "Posto Avenida"),
    (39, "Restaurante Sabor"),
    (math.inf, "Eletrônicos Web"),
)
ESTABELECIMENTO_SEM_RISCO = "Loja online"
FORMATO_DATA = "%Y-%m-%dT%H:%M:%S"


def clientes_de_marco(base: pd.DataFrame) -> pd.DataFrame:
    """Linhas de março (período de teste da seção 7), sem as de data vazia."""
    marco = base[(base["data_hora"] >= INICIO_TESTE) & (base["data_hora"] < FIM_TESTE)]
    return marco.dropna(subset=["id_cliente"])


def escolher_clientes_com_login(marco: pd.DataFrame) -> list[str]:
    """Os clientes de março com mais compras, desempate pelo identificador."""
    contagens = marco.groupby("id_cliente").size()
    ordenados = sorted(contagens.items(), key=lambda par: (-par[1], par[0]))
    return [str(identificador) for identificador, _ in ordenados[: len(NOMES_COM_LOGIN)]]


def nome_do_estabelecimento(risco: Any) -> str:
    """Nome fictício pela faixa de risco do estabelecimento; sem risco, "Loja online"."""
    try:
        valor = float(risco)
    except (TypeError, ValueError):
        return ESTABELECIMENTO_SEM_RISCO
    if math.isnan(valor):
        return ESTABELECIMENTO_SEM_RISCO
    return next(nome for limite, nome in ESTABELECIMENTOS_POR_RISCO if valor < limite)


def _associado_com_login(posicao: int, id_cliente: str | None, posicao_carteira: int) -> Associado:
    """Associado ``asc-NN`` com nome, saldo, limites e filial alternada (seção 17.2)."""
    return Associado(
        id_associado=f"asc-{posicao + 1:02d}",
        nome=NOMES_COM_LOGIN[posicao],
        id_filial=filial_da_posicao(posicao),
        posicao=posicao_carteira,
        tem_login=True,
        saldo=round(SALDO_INICIAL - PASSO_SALDO * posicao, 2),
        limite_total=LIMITE_TOTAL,
        limite_disponivel=LIMITE_DISPONIVEL,
        id_cliente_base=id_cliente,
    )


def _cartoes_do_associado(associado: Associado, posicao: int, do_cliente: pd.DataFrame) -> list:
    """Um cartão de débito e um de crédito, ligados aos cartões reais do mesmo tipo."""
    finais = {
        "debito": FINAL_DEBITO_BASE + PASSO_FINAL_DEBITO * posicao,
        "credito": FINAL_CREDITO_BASE + PASSO_FINAL_CREDITO * posicao,
    }
    cartoes = []
    for tipo, final in finais.items():
        reais = do_cliente.loc[do_cliente["tipo_transacao"] == tipo, "id_cartao"].dropna()
        cartoes.append(
            Cartao(
                id_cartao=f"car-{posicao + 1:02d}-{tipo[0]}",
                id_associado=associado.id_associado,
                tipo=tipo,
                final=f"{final:04d}",
                ids_cartao_base=tuple(sorted(str(c) for c in reais.unique())),
            )
        )
    return cartoes


def _compra_de_marco(
    linha: Any, associado: Associado, id_cartao: str | None, decisao: str, id_compra: str
) -> Compra:
    """Compra de março de um associado com login, com estabelecimento fictício."""
    data_hora = getattr(linha, "data_hora", None)
    valor = getattr(linha, "valor", None)
    return Compra(
        id_compra=id_compra,
        id_associado=associado.id_associado,
        id_filial=associado.id_filial,
        id_cartao=id_cartao,
        estabelecimento=nome_do_estabelecimento(getattr(linha, "risco_estabelecimento", None)),
        data_hora=None if pd.isna(data_hora) else pd.Timestamp(data_hora).strftime(FORMATO_DATA),
        valor=None if valor is None or pd.isna(valor) else float(valor),
        tipo_transacao=str(linha.tipo_transacao),
        modalidade_transacao=str(linha.modalidade_transacao),
        situacao=situacao_inicial(decisao),
        decisao=decisao,
        id_transacao_base=int(linha.id_transacao),
        variaveis={nome: _numero_ou_none(getattr(linha, nome, None)) for nome in VARIAVEIS_MODELO},
    )


def _numero_ou_none(valor: Any) -> float | None:
    """Número da base, ou None quando vazio."""
    if valor is None or pd.isna(valor):
        return None
    return float(valor)


def _carregar_compras(
    repos: Repositorios, associado: Associado, do_cliente: pd.DataFrame, decisoes: Mapping[int, str]
) -> None:
    """Grava as compras de março do cliente ligado ao associado, em ordem cronológica."""
    cartoes = repos.cartoes.listar_por_associado(associado.id_associado)
    cartao_por_tipo = {cartao.tipo: cartao.id_cartao for cartao in cartoes}
    ordenadas = do_cliente.sort_values(["data_hora", "id_transacao"], na_position="last")
    for linha in ordenadas.itertuples(index=False):
        decisao = decisoes.get(int(linha.id_transacao))
        if decisao is None:
            continue
        id_cartao = cartao_por_tipo.get(str(linha.tipo_transacao))
        compra = _compra_de_marco(linha, associado, id_cartao, decisao, repos.compras.proximo_id())
        repos.compras.salvar(compra)


def _montar_com_login(
    repos: Repositorios,
    marco: pd.DataFrame | None,
    com_login: list[str],
    posicao_por_cliente: Mapping[str, int],
    decisoes: Mapping[int, str] | None,
) -> None:
    """Cria os 10 associados com login, seus perfis, cartões e, se houver decisões, compras."""
    vazio = pd.DataFrame(columns=["tipo_transacao", "id_cartao"])
    for posicao in range(len(NOMES_COM_LOGIN)):
        id_cliente = com_login[posicao] if posicao < len(com_login) else None
        posicao_carteira = posicao_por_cliente.get(id_cliente or "", posicao)
        associado = _associado_com_login(posicao, id_cliente, posicao_carteira)
        repos.associados.salvar(associado)
        repos.perfis.salvar(associado.como_perfil())
        do_cliente = marco[marco["id_cliente"] == id_cliente] if marco is not None else vazio
        for cartao in _cartoes_do_associado(associado, posicao, do_cliente):
            repos.cartoes.salvar(cartao)
        if decisoes is not None and marco is not None:
            _carregar_compras(repos, associado, do_cliente, decisoes)


def montar_repositorios(
    base: pd.DataFrame | None, decisoes: Mapping[int, str] | None = None
) -> Repositorios:
    """Monta os repositórios em memória com filiais, funcionários, associados e cartões.

    Args:
        base: Parquet preparado, ou None para subir só com os dados inventados.
        decisoes: Decisão do modelo por ``id_transacao`` de março; quando informada, as compras
            de março dos associados com login entram no repositório com a situação inicial.

    Returns:
        Repositorios carregados.
    """
    repos = criar_repositorios_vazios()
    for filial in FILIAIS:
        repos.filiais.salvar(filial)
    for funcionario in FUNCIONARIOS:
        repos.perfis.salvar(funcionario)
    marco = None
    if base is not None:
        marco = clientes_de_marco(base).assign(id_cliente=lambda df: df["id_cliente"].astype(str))
    com_login = escolher_clientes_com_login(marco) if marco is not None else []
    carteira = distribuir_carteira(marco["id_cliente"]) if marco is not None else []
    posicao_por_cliente = {ident: posicao for ident, posicao, _ in carteira}
    _montar_com_login(repos, marco, com_login, posicao_por_cliente, decisoes)
    for ident, posicao, id_filial in carteira:
        if ident not in com_login:
            nome = f"Associado {posicao:04d}"
            associado = Associado(
                f"cli-{posicao:04d}", nome, id_filial, posicao, id_cliente_base=ident
            )
            repos.associados.salvar(associado)
    return repos
