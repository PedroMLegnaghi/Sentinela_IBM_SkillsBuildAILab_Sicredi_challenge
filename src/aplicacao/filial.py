"""Casos de uso da filial (ESPECIFICACAO, seção 17; Issue #96): fila do auditor e detalhe.

Só a carteira da própria filial, com nome abreviado e final do cartão; nunca saldo, limite,
extrato, nome completo ou identificador da base. A fonte das análises e auditorias é
injetada pela rota, para este módulo depender só das portas.
"""

from __future__ import annotations

import zlib
from collections.abc import Callable, Iterable, Mapping
from datetime import datetime
from typing import Any

from src.aplicacao.associado import Conflito, NaoEncontrado, situacoes_do_filtro
from src.dominio import regras
from src.dominio.entidades import Associado, Bloqueio, Cartao, Compra, Perfil
from src.portas.repositorios import Repositorios

SITUACOES_PADRAO_FILA = ("BLOQUEADA", "AGUARDANDO", "CONTESTADA")
ESTABELECIMENTO_DA_BASE = "Estabelecimento da base"
FILIAIS = (regras.ID_FILIAL_CENTRO, regras.ID_FILIAL_NORTE)


class AcessoNegado(Exception):  # noqa: N818 (nome em português, ADR-001)
    """Recurso de outra filial: a API responde 403."""


def _final_ficticio(id_cartao_base: str) -> str:
    """Quatro dígitos estáveis derivados do cartão da base, sem revelar o identificador."""
    return f"{zlib.crc32(id_cartao_base.encode('utf-8')) % 10000:04d}"


def _cartao_da_linha(repos: Repositorios, associado: Associado, linha: Mapping[str, Any]) -> Cartao:
    """Cartão do associado para o tipo da linha; cria um fictício para quem não tem login."""
    tipo = str(linha.get("tipo_transacao") or "debito")
    for cartao in repos.cartoes.listar_por_associado(associado.id_associado):
        if cartao.tipo == tipo:
            return cartao
    cartao = Cartao(
        id_cartao=f"car-{associado.posicao:04d}-{tipo[0]}",
        id_associado=associado.id_associado,
        tipo=tipo,
        final=_final_ficticio(str(linha.get("id_cartao") or associado.id_associado)),
        ids_cartao_base=(str(linha.get("id_cartao")),) if linha.get("id_cartao") else (),
    )
    repos.cartoes.salvar(cartao)
    return cartao


def registrar_fila_de_marco(repos: Repositorios, linhas: Iterable[Mapping[str, Any]]) -> int:
    """Garante uma Compra para cada linha da fila de demonstração cuja cliente está na carteira.

    As compras dos associados com login já existem (ligadas por ``id_transacao_base``); as dos
    demais clientes nascem aqui, com cartão fictício e a situação inicial da decisão.

    Args:
        repos: Repositórios da aplicação.
        linhas: Linhas da fila com ``id_transacao``, ``id_cliente``, ``id_cartao``, ``nota``,
            ``decisao``, ``valor``, ``data_hora``, ``tipo_transacao`` e ``modalidade_transacao``.

    Returns:
        Quantidade de compras criadas.
    """
    por_cliente = {
        a.id_cliente_base: a
        for filial in FILIAIS
        for a in repos.associados.listar_por_filial(filial)
        if a.id_cliente_base
    }
    existentes = {
        c.id_transacao_base: c
        for filial in FILIAIS
        for c in repos.compras.listar_por_filial(filial)
        if c.id_transacao_base is not None
    }
    criadas = 0
    for linha in linhas:
        id_transacao = int(linha["id_transacao"])
        associado = por_cliente.get(str(linha.get("id_cliente")))
        if id_transacao in existentes:
            # Compra de associado com login: só recebe a nota que a fila já calculou.
            existente = existentes[id_transacao]
            existente.analise = {**(existente.analise or {}), "nota": linha.get("nota")}
            repos.compras.salvar(existente)
            continue
        if associado is None:
            continue
        cartao = _cartao_da_linha(repos, associado, linha)
        decisao = str(linha["decisao"])
        repos.compras.salvar(
            Compra(
                id_compra=repos.compras.proximo_id(),
                id_associado=associado.id_associado,
                id_filial=associado.id_filial,
                id_cartao=cartao.id_cartao,
                estabelecimento=ESTABELECIMENTO_DA_BASE,
                data_hora=linha.get("data_hora"),
                valor=linha.get("valor"),
                tipo_transacao=str(linha.get("tipo_transacao") or ""),
                modalidade_transacao=str(linha.get("modalidade_transacao") or ""),
                situacao=regras.situacao_inicial(decisao),
                decisao=decisao,
                id_transacao_base=id_transacao,
                analise={"nota": linha.get("nota")},
            )
        )
        criadas += 1
    return criadas


def _veredito(auditoria: dict[str, Any] | None) -> str | None:
    """Parecer da última auditoria concluída, ou None."""
    if not auditoria or auditoria.get("status") != "concluida" or not auditoria.get("relatorio"):
        return None
    return auditoria["relatorio"].get("parecer")


def item_da_fila(
    repos: Repositorios, compra: Compra, auditoria_de: Callable[[Compra], dict | None]
) -> dict[str, Any]:
    """ItemFilaFilial do contrato (seção 17.3)."""
    associado = repos.associados.obter(compra.id_associado)
    cartao = repos.cartoes.obter(compra.id_cartao) if compra.id_cartao else None
    return {
        "id_compra": compra.id_compra,
        "nota": (compra.analise or {}).get("nota"),
        "decisao": compra.decisao,
        "associado": regras.nome_abreviado(associado.nome) if associado else "",
        "final_cartao": cartao.final if cartao else "",
        "data_hora": compra.data_hora,
        "valor": compra.valor,
        "tipo_transacao": compra.tipo_transacao,
        "modalidade_transacao": compra.modalidade_transacao,
        "situacao": compra.situacao,
        "veredito_ia": _veredito(auditoria_de(compra)),
    }


def ver_fila(
    repos: Repositorios,
    id_filial: str,
    situacao: str | None,
    ids_fila: set[int],
    auditoria_de: Callable[[Compra], dict | None],
) -> dict[str, Any]:
    """Fila da filial, por nota decrescente.

    Entram as linhas da fila de demonstração da carteira, as simuladas não aprovadas e as
    contestadas.

    Args:
        repos: Repositórios da aplicação.
        id_filial: Filial da sessão.
        situacao: Filtro separado por vírgula; None usa BLOQUEADA, AGUARDANDO e CONTESTADA.
        ids_fila: ``id_transacao`` das linhas da fila de demonstração.
        auditoria_de: Devolve a auditoria de uma compra, ou None.

    Returns:
        Corpo de ``GET /api/filial/fila``.

    Raises:
        ValueError: Se o filtro tem situação desconhecida.
    """
    filtro = situacoes_do_filtro(situacao) or set(SITUACOES_PADRAO_FILA)
    filial = repos.filiais.obter(id_filial)
    compras = [
        c
        for c in repos.compras.listar_por_filial(id_filial)
        if c.situacao in filtro
        and (c.simulada or c.situacao == "CONTESTADA" or c.id_transacao_base in ids_fila)
    ]
    itens = [item_da_fila(repos, c, auditoria_de) for c in compras]
    itens.sort(key=lambda item: (-(item["nota"] or 0.0), item["id_compra"]))
    return {
        "filial": {"id_filial": id_filial, "nome": filial.nome if filial else ""},
        "total": len(itens),
        "itens": itens,
    }


def _bloqueio_para_filial(
    repos: Repositorios, compra: Compra, analise: dict[str, Any]
) -> dict[str, Any] | None:
    """Bloqueio como a filial vê: quem (Sentinela ou auditor), quando e o motivo técnico."""
    bloqueio = compra.bloqueio
    if bloqueio is None:
        if compra.situacao != "BLOQUEADA":
            return None
        bloqueio = Bloqueio(em=compra.data_hora or "", motivo=str(analise.get("explicacao") or ""))
    por = "Sentinela"
    # Bloqueio do Sentinela: o motivo técnico é a explicação do modelo; do auditor, o gravado.
    motivo = str(analise.get("explicacao") or bloqueio.motivo)
    if bloqueio.id_auditor:
        auditor = repos.perfis.obter(bloqueio.id_auditor)
        por = auditor.nome if auditor else "Analista"
        motivo = bloqueio.motivo
    if bloqueio.nota_auditor:
        motivo = f"{motivo} Nota do analista: {bloqueio.nota_auditor}"
    return {"por": por, "em": bloqueio.em, "motivo": motivo}


def ver_compra(
    repos: Repositorios,
    id_filial: str,
    id_compra: str,
    analise_de: Callable[[Compra], dict[str, Any]],
    auditoria_de: Callable[[Compra], dict | None],
    historico_de: Callable[[Compra], tuple[int, float | None]],
) -> dict[str, Any]:
    """Detalhe técnico de uma compra da carteira, dentro da LGPD.

    Args:
        repos: Repositórios da aplicação.
        id_filial: Filial da sessão.
        id_compra: Compra pedida.
        analise_de: Devolve a Analise (seção 12) da compra.
        auditoria_de: Devolve a Auditoria (seção 13) da compra, ou None.
        historico_de: Devolve ``(compras_90d, valor_mediano)`` do cliente antes da compra.

    Returns:
        Corpo de ``GET /api/filial/compras/{id_compra}``.

    Raises:
        NaoEncontrado: Se a compra não existe.
        AcessoNegado: Se a compra é de outra filial.
    """
    compra = repos.compras.obter(id_compra)
    if compra is None:
        raise NaoEncontrado("Compra não encontrada.")
    if compra.id_filial != id_filial:
        raise AcessoNegado("Esta compra é da carteira de outra filial.")
    analise = analise_de(compra)
    item = item_da_fila(repos, compra, auditoria_de)
    compras_90d, valor_mediano = historico_de(compra)
    resposta = compra.resposta_associado
    return {
        "compra": item,
        "analise": analise,
        "auditoria": auditoria_de(compra),
        "associado": {
            "nome_abreviado": item["associado"],
            "final_cartao": item["final_cartao"],
            "historico": {
                "compras_90d": compras_90d,
                "valor_mediano": valor_mediano,
                "contestacoes": len(repos.contestacoes.listar_por_associado(compra.id_associado)),
            },
        },
        "resposta_associado": (
            {"resposta": resposta.resposta, "em": resposta.em} if resposta else None
        ),
        "bloqueio": _bloqueio_para_filial(repos, compra, analise),
    }


def _motivo_do_bloqueio(analise: dict[str, Any], auditoria: dict[str, Any] | None) -> str:
    """Explicação da IA se a auditoria terminou; senão, a explicação do modelo."""
    relatorio = (auditoria or {}).get("relatorio") or {}
    if (auditoria or {}).get("status") == "concluida" and relatorio.get("explicacao"):
        return str(relatorio["explicacao"])
    return str(analise.get("explicacao") or "")


def bloquear_compra(
    repos: Repositorios,
    auditor: Perfil,
    id_compra: str,
    nota: str | None,
    analise_de: Callable[[Compra], dict[str, Any]],
    auditoria_de: Callable[[Compra], dict | None],
) -> Compra:
    """Auditor bloqueia uma compra AGUARDANDO da própria filial (seção 17.5).

    Args:
        repos: Repositórios da aplicação.
        auditor: Perfil do auditor da sessão (dá o id e a filial).
        id_compra: Compra a bloquear.
        nota: Nota livre do auditor (até 300 caracteres), ou None.
        analise_de: Devolve a Analise da compra.
        auditoria_de: Devolve a Auditoria da compra, ou None.

    Returns:
        A compra já BLOQUEADA.

    Raises:
        NaoEncontrado: Se a compra não existe.
        AcessoNegado: Se a compra é de outra filial.
        Conflito: Se a compra não está AGUARDANDO.
    """
    compra = repos.compras.obter(id_compra)
    if compra is None:
        raise NaoEncontrado("Compra não encontrada.")
    if compra.id_filial != auditor.id_filial:
        raise AcessoNegado("Esta compra é da carteira de outra filial.")
    if compra.situacao != "AGUARDANDO":
        raise Conflito("Só uma compra que aguarda o associado pode ser bloqueada pelo auditor.")
    motivo = _motivo_do_bloqueio(analise_de(compra), auditoria_de(compra))
    em = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    regras.bloquear_pelo_auditor(
        compra, auditor.id_perfil, em, motivo, (nota or "").strip() or None
    )
    repos.compras.salvar(compra)
    return compra
