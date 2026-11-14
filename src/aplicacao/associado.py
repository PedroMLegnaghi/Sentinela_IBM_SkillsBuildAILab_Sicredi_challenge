"""Casos de uso do associado (ESPECIFICACAO, seção 17; Issue #94).

Recebem os repositórios por parâmetro e nunca importam adaptadores. Devolvem dicionários no
formato do contrato (seção 17.3), sem sinais, nota, contribuições nem parecer da IA.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any

from src.associado import notificacoes
from src.config import HORA_FIM_MADRUGADA, VARIAVEIS_MODELO
from src.dominio import regras
from src.dominio.entidades import SITUACOES, Associado, Bloqueio, Cartao, Compra
from src.portas.repositorios import Repositorios

MOTIVO_GENERICO = "A compra fugiu do seu padrão de uso e foi bloqueada por segurança."
MOTIVO_NAO_RECONHECIDA = "O associado não reconheceu a compra no aviso."
QUANTIDADE_ULTIMAS_COMPRAS = 3
FORMATO_DATA = "%Y-%m-%dT%H:%M:%S"


class NaoEncontrado(Exception):  # noqa: N818 (nome em português, ADR-001)
    """Recurso inexistente ou de outro associado: a API responde 404 sem revelar que existe."""


class Conflito(Exception):  # noqa: N818 (nome em português, ADR-001)
    """Operação que o estado atual não permite: a API responde 409."""


def _agora() -> str:
    return datetime.now().strftime(FORMATO_DATA)


def _normalizar_data_hora(texto: Any) -> str | None:
    """Data em ISO 8601 sem fuso, ou None se vazia ou inválida."""
    try:
        return datetime.fromisoformat(str(texto)).strftime(FORMATO_DATA)
    except ValueError:
        return None


# --- Leitura ----------------------------------------------------------------------------------


def _associado_ou_erro(repos: Repositorios, id_associado: str) -> Associado:
    associado = repos.associados.obter(id_associado)
    if associado is None or not associado.tem_login:
        raise NaoEncontrado("Associado não encontrado.")
    return associado


def _compra_do_associado(repos: Repositorios, id_associado: str, id_compra: str) -> Compra:
    compra = repos.compras.obter(id_compra)
    if compra is None or compra.id_associado != id_associado:
        raise NaoEncontrado("Compra não encontrada no seu extrato.")
    return compra


def _extrato_ordenado(compras: list[Compra]) -> list[Compra]:
    """Simuladas primeiro, na ordem em que foram feitas; depois as de março, da mais recente."""
    simuladas = [c for c in compras if c.simulada]
    de_marco = sorted((c for c in compras if not c.simulada), key=lambda c: c.data_hora or "")
    return simuladas + de_marco[::-1]


def cartao_para_dict(cartao: Cartao) -> dict[str, Any]:
    """Cartao do contrato (seção 17.3)."""
    return {
        "id": cartao.id_cartao,
        "tipo": cartao.tipo,
        "final": cartao.final,
        "bloqueado": cartao.bloqueado,
    }


def compra_para_extrato(repos: Repositorios, compra: Compra) -> dict[str, Any]:
    """CompraExtrato do contrato (seção 17.3), sem nada técnico."""
    cartao = repos.cartoes.obter(compra.id_cartao) if compra.id_cartao else None
    return {
        "id_compra": compra.id_compra,
        "estabelecimento": compra.estabelecimento,
        "data_hora": compra.data_hora,
        "valor": compra.valor,
        "tipo_transacao": compra.tipo_transacao,
        "modalidade_transacao": compra.modalidade_transacao,
        "final_cartao": cartao.final if cartao else "",
        "situacao": compra.situacao,
        "id_notificacao": compra.id_notificacao,
        "simulada": compra.simulada,
    }


def _bloqueio_para_associado(repos: Repositorios, bloqueio: Bloqueio | None) -> dict | None:
    """Bloqueio como o associado vê: "Sentinela" ou "Analista da agência X" e motivo genérico."""
    if bloqueio is None:
        return None
    por = "Sentinela"
    auditor = repos.perfis.obter(bloqueio.id_auditor) if bloqueio.id_auditor else None
    if auditor is not None:
        filial = repos.filiais.obter(auditor.id_filial)
        por = f"Analista da agência {filial.nome if filial else auditor.id_filial}"
    return {"por": por, "em": bloqueio.em, "motivo": MOTIVO_GENERICO}


def _pendente(compra: Compra) -> dict[str, Any] | None:
    """Aviso ainda sem resposta de uma compra AGUARDANDO, ou None."""
    if compra.situacao != "AGUARDANDO" or compra.id_notificacao is None:
        return None
    notificacao = notificacoes.obter(compra.id_notificacao)
    if notificacao is None or notificacao["status"] != "aguardando":
        return None
    return {
        "id_notificacao": compra.id_notificacao,
        "id_compra": compra.id_compra,
        "valor": compra.valor,
        "data_hora": compra.data_hora,
    }


def ver_inicio(repos: Repositorios, id_associado: str) -> dict[str, Any]:
    """Tela inicial: saldo, limites, cartões, avisos pendentes e as 3 compras mais recentes.

    Args:
        repos: Repositórios da aplicação.
        id_associado: Associado da sessão.

    Returns:
        Corpo de ``GET /api/associado/inicio``.

    Raises:
        NaoEncontrado: Se o associado não existe ou não tem login.
    """
    associado = _associado_ou_erro(repos, id_associado)
    filial = repos.filiais.obter(associado.id_filial)
    compras = _extrato_ordenado(repos.compras.listar_por_associado(id_associado))
    pendentes = [p for p in (_pendente(c) for c in compras) if p is not None]
    return {
        "associado": {"nome": associado.nome, "filial": filial.nome if filial else ""},
        "saldo": associado.saldo,
        "limite_total": associado.limite_total,
        "limite_disponivel": associado.limite_disponivel,
        "cartoes": [cartao_para_dict(c) for c in repos.cartoes.listar_por_associado(id_associado)],
        "pendentes": pendentes,
        "ultimas_compras": [
            compra_para_extrato(repos, c) for c in compras[:QUANTIDADE_ULTIMAS_COMPRAS]
        ],
    }


def situacoes_do_filtro(texto: str | None) -> set[str] | None:
    """Converte ``situacao=APROVADA,BLOQUEADA`` num conjunto; None sem filtro.

    Raises:
        ValueError: Se alguma situação é desconhecida.
    """
    if not texto:
        return None
    pedidas = {parte.strip() for parte in texto.split(",") if parte.strip()}
    desconhecidas = sorted(pedidas - set(SITUACOES))
    if desconhecidas:
        raise ValueError(f"Situação inválida: {desconhecidas}. Use {', '.join(SITUACOES)}.")
    return pedidas


def ver_extrato(repos: Repositorios, id_associado: str, situacao: str | None) -> dict[str, Any]:
    """Extrato do associado, com filtro opcional por situação.

    Args:
        repos: Repositórios da aplicação.
        id_associado: Associado da sessão.
        situacao: Situações separadas por vírgula, ou None.

    Returns:
        Corpo de ``GET /api/associado/extrato``.

    Raises:
        NaoEncontrado: Se o associado não existe ou não tem login.
        ValueError: Se o filtro tem situação desconhecida.
    """
    _associado_ou_erro(repos, id_associado)
    filtro = situacoes_do_filtro(situacao)
    compras = _extrato_ordenado(repos.compras.listar_por_associado(id_associado))
    itens = [c for c in compras if filtro is None or c.situacao in filtro]
    return {"total": len(itens), "itens": [compra_para_extrato(repos, c) for c in itens]}


def ver_compra(repos: Repositorios, id_associado: str, id_compra: str) -> dict[str, Any]:
    """Detalhe de uma compra do próprio associado, com motivo genérico de bloqueio.

    Args:
        repos: Repositórios da aplicação.
        id_associado: Associado da sessão.
        id_compra: Compra pedida.

    Returns:
        CompraExtrato mais ``bloqueio``, ``resposta_associado`` e ``pode_contestar``.

    Raises:
        NaoEncontrado: Se a compra não existe ou é de outro associado.
    """
    compra = _compra_do_associado(repos, id_associado, id_compra)
    resposta = compra.resposta_associado
    return {
        **compra_para_extrato(repos, compra),
        "bloqueio": _bloqueio_para_associado(repos, compra.bloqueio),
        "resposta_associado": (
            {"resposta": resposta.resposta, "em": resposta.em} if resposta else None
        ),
        "pode_contestar": compra.situacao == "APROVADA",
    }


# --- Escrita ----------------------------------------------------------------------------------


def montar_transacao(entrada: dict[str, Any], cartao: Cartao) -> dict[str, Any]:
    """Transação para o modelo: crédito e tipo vêm do cartão; hora e madrugada, da data.

    Args:
        entrada: Corpo de ``POST /api/associado/compras``.
        cartao: Cartão escolhido.

    Returns:
        Dicionário com as variáveis do modelo, ``data_hora``, ``tipo_transacao`` e
        ``modalidade_transacao``; nunca identificadores.
    """
    transacao = {variavel: entrada.get(variavel) for variavel in VARIAVEIS_MODELO}
    transacao["credito"] = 1 if cartao.tipo == "credito" else 0
    modalidade = entrada.get("modalidade_transacao") or "cartao_presente"
    if transacao["nao_presente"] is None:
        transacao["nao_presente"] = 1 if modalidade == "cartao_nao_presente" else 0
    data_hora = _normalizar_data_hora(entrada.get("data_hora"))
    if data_hora is not None:
        hora = datetime.fromisoformat(data_hora).hour
        if transacao["hora"] is None:
            transacao["hora"] = float(hora)
        if transacao["madrugada"] is None:
            transacao["madrugada"] = 1 if hora < HORA_FIM_MADRUGADA else 0
    transacao["data_hora"] = data_hora
    transacao["tipo_transacao"] = cartao.tipo
    transacao["modalidade_transacao"] = modalidade
    return transacao


def _publica(compra: Compra) -> dict[str, Any]:
    """O que a mensagem ao associado pode ver: valor, data e tipo; nunca identificadores."""
    return {
        "valor": compra.valor,
        "data_hora": compra.data_hora,
        "tipo_transacao": compra.tipo_transacao,
    }


def simular_compra(
    repos: Repositorios,
    id_associado: str,
    entrada: dict[str, Any],
    analisar: Callable[[dict[str, Any]], dict[str, Any]],
) -> tuple[Compra, dict[str, Any], dict[str, Any]]:
    """Passa uma compra simulada pelo Sentinela e grava o resultado.

    Args:
        repos: Repositórios da aplicação.
        id_associado: Associado da sessão.
        entrada: Corpo de ``POST /api/associado/compras`` já validado.
        analisar: ``servicos.analisar_transacao`` ou um dublê com a mesma assinatura.

    Returns:
        ``(compra, transacao, analise)``; a rota usa os dois últimos para a auditoria por IA.

    Raises:
        NaoEncontrado: Se o cartão não existe ou é de outro associado.
        Conflito: Se o cartão está bloqueado.
    """
    associado = _associado_ou_erro(repos, id_associado)
    cartao = repos.cartoes.obter(str(entrada.get("cartao")))
    if cartao is None or cartao.id_associado != id_associado:
        raise NaoEncontrado("Cartão não encontrado entre os seus cartões.")
    if cartao.bloqueado:
        raise Conflito("Este cartão está bloqueado e não aceita compra nova.")
    transacao = montar_transacao(entrada, cartao)
    analise = analisar(transacao)
    compra = Compra(
        id_compra=repos.compras.proximo_id(),
        id_associado=id_associado,
        id_filial=associado.id_filial,
        id_cartao=cartao.id_cartao,
        estabelecimento=str(entrada.get("estabelecimento") or ""),
        data_hora=transacao["data_hora"],
        valor=transacao.get("valor"),
        tipo_transacao=cartao.tipo,
        modalidade_transacao=transacao["modalidade_transacao"],
        situacao=regras.situacao_inicial(analise["decisao"]),
        decisao=analise["decisao"],
        simulada=True,
        analise=analise,
    )
    if compra.situacao == "APROVADA":
        regras.aplicar_no_saldo(associado, cartao, compra)
        repos.associados.salvar(associado)
    else:
        aviso = notificacoes.criar_notificacao(_publica(compra), analise)
        compra.id_notificacao = aviso["id_notificacao"]
    if compra.situacao == "BLOQUEADA":
        compra.bloqueio = Bloqueio(em=_agora(), motivo=analise.get("explicacao") or MOTIVO_GENERICO)
    repos.compras.salvar(compra)
    return compra, transacao, analise


def contestar_compra(
    repos: Repositorios, id_associado: str, id_compra: str
) -> tuple[Compra, Cartao]:
    """Aplica "Não reconheço esta compra": bloqueia o cartão e devolve o valor.

    Args:
        repos: Repositórios da aplicação.
        id_associado: Associado da sessão.
        id_compra: Compra APROVADA do próprio associado.

    Returns:
        ``(compra, cartao)`` já atualizados.

    Raises:
        NaoEncontrado: Se a compra não é do associado.
        Conflito: Se a compra não está APROVADA.
    """
    associado = _associado_ou_erro(repos, id_associado)
    compra = _compra_do_associado(repos, id_associado, id_compra)
    cartao = repos.cartoes.obter(compra.id_cartao) if compra.id_cartao else None
    if compra.situacao != "APROVADA" or cartao is None:
        raise Conflito("Só uma compra aprovada pode ser contestada.")
    contestacao = regras.contestar(compra, cartao, _agora(), repos.contestacoes.proximo_id())
    # As compras de março já estão descontadas no saldo inicial: a devolução vale para elas também.
    compra.saldo_aplicado = compra.saldo_aplicado or not compra.simulada
    regras.devolver_ao_saldo(associado, cartao, compra)
    repos.contestacoes.salvar(contestacao)
    repos.cartoes.salvar(cartao)
    repos.associados.salvar(associado)
    repos.compras.salvar(compra)
    return compra, cartao


def aplicar_resposta_do_aviso(
    repos: Repositorios, id_notificacao: str, resposta: str
) -> Compra | None:
    """Liga a resposta ao aviso (seção 15) à compra: "sim" aprova e aplica no saldo; "nao" bloqueia.

    Args:
        repos: Repositórios da aplicação.
        id_notificacao: Aviso respondido.
        resposta: "sim" ou "nao".

    Returns:
        A compra atualizada, ou None se o aviso não está ligado a nenhuma compra.
    """
    compra = repos.compras.obter_por_notificacao(id_notificacao)
    if compra is None:
        return None
    situacao = regras.aplicar_resposta(compra, resposta, _agora())
    associado = repos.associados.obter(compra.id_associado)
    cartao = repos.cartoes.obter(compra.id_cartao) if compra.id_cartao else None
    if situacao == "APROVADA" and associado is not None and cartao is not None:
        regras.aplicar_no_saldo(associado, cartao, compra)
        repos.associados.salvar(associado)
    elif situacao == "BLOQUEADA" and compra.bloqueio is None:
        compra.bloqueio = Bloqueio(em=_agora(), motivo=MOTIVO_NAO_RECONHECIDA)
    repos.compras.salvar(compra)
    return compra


def avisar_compras_de_marco(repos: Repositorios) -> int:
    """Cria o aviso das compras de março AGUARDANDO ou BLOQUEADA dos associados com login.

    Args:
        repos: Repositórios recém-carregados.

    Returns:
        Quantidade de avisos criados.
    """
    criados = 0
    for perfil in repos.perfis.listar():
        if perfil.papel != "associado":
            continue
        for compra in repos.compras.listar_por_associado(perfil.id_perfil):
            if compra.situacao not in ("AGUARDANDO", "BLOQUEADA") or compra.id_notificacao:
                continue
            aviso = notificacoes.criar_notificacao(_publica(compra), {"decisao": compra.decisao})
            compra.id_notificacao = aviso["id_notificacao"]
            if compra.situacao == "BLOQUEADA" and compra.bloqueio is None:
                compra.bloqueio = Bloqueio(em=compra.data_hora or _agora(), motivo=MOTIVO_GENERICO)
            repos.compras.salvar(compra)
            criados += 1
    return criados
