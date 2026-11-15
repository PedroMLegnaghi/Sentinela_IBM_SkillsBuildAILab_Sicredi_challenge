"""Regras puras do associado e da filial (ESPECIFICACAO, seção 17.1; Issue #92).

Funções sem estado nem acesso a repositório: recebem entidades, mudam o que a regra manda e
devolvem o resultado. Quem grava é a aplicação.
"""

from __future__ import annotations

from collections.abc import Iterable

from src.dominio.entidades import (
    RESPOSTAS_ASSOCIADO,
    Associado,
    Bloqueio,
    Cartao,
    Compra,
    Contestacao,
    Filial,
    RespostaAssociado,
)

SITUACAO_POR_DECISAO = {
    "APROVAR": "APROVADA",
    "PEDIR_CONFIRMACAO": "AGUARDANDO",
    "BLOQUEAR": "BLOQUEADA",
}
# Resposta ao aviso numa compra AGUARDANDO; numa BLOQUEADA pelo Sentinela a situação não muda
SITUACAO_POR_RESPOSTA = {"sim": "APROVADA", "nao": "BLOQUEADA"}
ID_FILIAL_CENTRO = "fil-centro"
ID_FILIAL_NORTE = "fil-norte"
# A matriz vê todas as filiais e não tem carteira própria.
MATRIZ = Filial("matriz", "Matriz Sicredi")


def situacao_inicial(decisao: str) -> str:
    """Situação com que a compra nasce, a partir da decisão do modelo.

    Args:
        decisao: APROVAR, PEDIR_CONFIRMACAO ou BLOQUEAR.

    Returns:
        APROVADA, AGUARDANDO ou BLOQUEADA.

    Raises:
        ValueError: Se a decisão é desconhecida.
    """
    if decisao not in SITUACAO_POR_DECISAO:
        raise ValueError(f"Decisão desconhecida: {decisao}.")
    return SITUACAO_POR_DECISAO[decisao]


def aplicar_no_saldo(associado: Associado, cartao: Cartao, compra: Compra) -> bool:
    """Desconta uma compra APROVADA do saldo (débito) ou do limite disponível (crédito).

    Só aplica uma vez por compra; AGUARDANDO, BLOQUEADA e CONTESTADA não mexem em nada. As
    compras de março já estão no saldo inicial (seção 17.1): só as simuladas são aplicadas.

    Args:
        associado: Dono do cartão; tem o saldo e o limite alterados no lugar.
        cartao: Cartão da compra, que define se é saldo ou limite.
        compra: Compra a aplicar; fica marcada com ``saldo_aplicado``.

    Returns:
        True se descontou; False se não havia o que aplicar.
    """
    if compra.situacao != "APROVADA" or compra.saldo_aplicado or compra.valor is None:
        return False
    if not compra.simulada:
        return False
    if cartao.tipo == "debito":
        associado.saldo = round(associado.saldo - compra.valor, 2)
    else:
        associado.limite_disponivel = round(associado.limite_disponivel - compra.valor, 2)
    compra.saldo_aplicado = True
    return True


def devolver_ao_saldo(associado: Associado, cartao: Cartao, compra: Compra) -> bool:
    """Devolve ao saldo ou ao limite o valor de uma compra que já tinha sido aplicada.

    Args:
        associado: Dono do cartão.
        cartao: Cartão da compra.
        compra: Compra contestada; perde a marca ``saldo_aplicado``.

    Returns:
        True se devolveu; False se a compra nunca foi aplicada.
    """
    if not compra.saldo_aplicado or compra.valor is None:
        return False
    if cartao.tipo == "debito":
        associado.saldo = round(associado.saldo + compra.valor, 2)
    else:
        associado.limite_disponivel = round(associado.limite_disponivel + compra.valor, 2)
    compra.saldo_aplicado = False
    return True


def aplicar_resposta(compra: Compra, resposta: str, em: str) -> str:
    """Registra a resposta do associado ao aviso e muda a situação quando cabe.

    Args:
        compra: Compra avisada.
        resposta: "sim" (fui eu) ou "nao" (não fui eu).
        em: Momento da resposta em ISO 8601.

    Returns:
        Situação da compra depois da resposta.

    Raises:
        ValueError: Se a resposta não é "sim" nem "nao".
    """
    if resposta not in RESPOSTAS_ASSOCIADO:
        raise ValueError('A resposta do associado deve ser "sim" ou "nao".')
    compra.resposta_associado = RespostaAssociado(resposta=resposta, em=em)
    if compra.situacao == "AGUARDANDO":
        compra.situacao = SITUACAO_POR_RESPOSTA[resposta]
    elif compra.situacao == "BLOQUEADA" and _bloqueada_por_auditor(compra):
        # O aviso continua valendo depois do bloqueio do auditor (seção 17.5).
        compra.bloqueio.correto = resposta == "nao"
        if resposta == "sim":
            compra.situacao = "APROVADA"
    return compra.situacao


def _bloqueada_por_auditor(compra: Compra) -> bool:
    return compra.bloqueio is not None and compra.bloqueio.id_auditor is not None


def bloquear_pelo_auditor(
    compra: Compra, id_auditor: str, em: str, motivo: str, nota: str | None
) -> Bloqueio:
    """Auditor bloqueia uma compra que ainda espera o associado.

    Args:
        compra: Compra AGUARDANDO; vira BLOQUEADA.
        id_auditor: Perfil do auditor que bloqueou.
        em: Momento do bloqueio em ISO 8601.
        motivo: Explicação da IA (ou do modelo) que embasa o bloqueio.
        nota: Nota livre do auditor, ou None.

    Returns:
        O Bloqueio gravado na compra.

    Raises:
        ValueError: Se a compra não está AGUARDANDO.
    """
    if compra.situacao != "AGUARDANDO":
        raise ValueError("Só uma compra que aguarda o associado pode ser bloqueada pelo auditor.")
    compra.situacao = "BLOQUEADA"
    compra.bloqueio = Bloqueio(em=em, motivo=motivo, id_auditor=id_auditor, nota_auditor=nota)
    return compra.bloqueio


def contestar(compra: Compra, cartao: Cartao, em: str, id_contestacao: str) -> Contestacao:
    """Aplica "Não reconheço esta compra": só numa APROVADA; bloqueia o cartão.

    Args:
        compra: Compra contestada; vira CONTESTADA.
        cartao: Cartão da compra; fica bloqueado.
        em: Momento da contestação em ISO 8601.
        id_contestacao: Identificador opaco gerado pelo repositório.

    Returns:
        A Contestacao a gravar, com o valor a devolver.

    Raises:
        ValueError: Se a compra não está APROVADA.
    """
    if compra.situacao != "APROVADA":
        raise ValueError("Só uma compra aprovada pode ser contestada.")
    compra.situacao = "CONTESTADA"
    cartao.bloqueado = True
    return Contestacao(
        id_contestacao=id_contestacao,
        id_compra=compra.id_compra,
        id_associado=compra.id_associado,
        id_filial=compra.id_filial,
        em=em,
        valor_devolvido=float(compra.valor or 0.0),
    )


def nome_abreviado(nome: str) -> str:
    """Nome que a filial vê: "Ana Souza" vira "Ana S."; "Associado 0421" fica como está."""
    partes = nome.split()
    if len(partes) < 2 or partes[1].isdigit():  # noqa: PLR2004 (duas partes: nome e sobrenome)
        return nome
    return f"{partes[0]} {partes[1][0]}."


def filial_da_posicao(posicao: int) -> str:
    """Posição par vai para a Agência Centro; ímpar, para a Agência Norte."""
    return ID_FILIAL_CENTRO if posicao % 2 == 0 else ID_FILIAL_NORTE


def distribuir_carteira(identificadores: Iterable[str]) -> list[tuple[str, int, str]]:
    """Divide os clientes entre as filiais pela posição na ordem do identificador.

    Args:
        identificadores: Identificadores dos clientes (repetidos são contados uma vez).

    Returns:
        Lista de ``(identificador, posicao, id_filial)`` na ordem dos identificadores.
    """
    ordenados = sorted(set(identificadores))
    return [(ident, posicao, filial_da_posicao(posicao)) for posicao, ident in enumerate(ordenados)]
