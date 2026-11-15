"""Modo local da auditoria: as mesmas ferramentas, com uma regra simples (ESPECIFICACAO, 13).

Usado quando não há credenciais do watsonx.ai, quando ele não responde ou quando a resposta
é inválida. A regra é independente da nota do modelo, para servir de segunda opinião.
"""

from __future__ import annotations

from typing import Any

from src.auditoria.ferramentas import CaixaDeFerramentas
from src.config import AUDITORIA_SINAIS_RISCO_ALTO, AUDITORIA_SINAIS_SUSPEITO

NOME_MODELO = "regras-locais"
RAZAO_VALOR_ATIPICO = 3.0
RAZAO_VALOR_HABITUAL = 2.0

NOMES_LEGIVEIS = {
    "valor": "valor",
    "hora": "hora",
    "madrugada": "madrugada",
    "credito": "tipo da compra",
    "nao_presente": "modalidade",
    "ip_pais_desconhecido": "país do IP",
    "vel_cartao_terminal_1h": "uso do cartão em terminais na última hora",
    "qtd_transacoes_cartao_1min": "transações do cartão no último minuto",
    "qtd_token_carteira_3m": "uso do token de carteira digital",
    "dist_terminal_anterior_km": "distância do terminal anterior",
    "risco_estabelecimento": "risco do estabelecimento",
    "contribuicoes": "contribuições da nota",
    "id_cartao": "histórico do cartão",
    "id_cliente": "histórico do cliente",
    "id_estabelecimento": "histórico do estabelecimento",
    "base de dados": "base de dados",
}


def _risco(n_sinais: int, ip_desconhecido: bool) -> str:
    """Regra local: IP desconhecido ou 4 sinais ou mais → ALTO; 2 ou 3 → SUSPEITO."""
    if ip_desconhecido or n_sinais >= AUDITORIA_SINAIS_RISCO_ALTO:
        return "ALTO"
    return "SUSPEITO" if n_sinais >= AUDITORIA_SINAIS_SUSPEITO else "BAIXO"


def _evidencias_do_cliente(perfil: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Evidências a favor e contra tiradas do perfil de gasto do cliente."""
    razao = perfil.get("valor_atual_sobre_mediana")
    if razao is None:
        return [], []
    if razao >= RAZAO_VALOR_ATIPICO:
        vezes = f"{razao:.1f}".replace(".", ",")
        return [f"Valor {vezes} vezes a mediana das compras do cliente."], []
    if razao < RAZAO_VALOR_HABITUAL:
        return [], ["Valor dentro do padrão de gasto do cliente."]
    return [], []


def _evidencias_do_cartao(historico: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Evidências a favor e contra tiradas do histórico recente do cartão."""
    if not historico:
        return [], []
    if historico.get("rajada_acima_do_limiar"):
        return ["O cartão já teve rajadas de transações em compras recentes."], []
    return [], ["As compras recentes do cartão não mostram rajadas."]


def avaliar(caixa: CaixaDeFerramentas) -> dict[str, Any]:
    """Roda todas as ferramentas e monta a parte do relatório pela regra local.

    Args:
        caixa: Ferramentas já ligadas à transação, à análise e à base.

    Returns:
        Dicionário com risco_ia, confianca, explicacao e as três listas de evidências.
    """
    envelopes = {nome: caixa.executar(nome) for nome in caixa.nomes()}
    sinais = envelopes["sinais_da_transacao"]["dados"]
    risco = _risco(sinais["quantidade"], sinais["ip_pais_desconhecido"])
    favor_cliente, contra_cliente = _evidencias_do_cliente(envelopes["perfil_do_cliente"]["dados"])
    favor_cartao, contra_cartao = _evidencias_do_cartao(envelopes["historico_do_cartao"]["dados"])
    ausentes = {campo for env in envelopes.values() for campo in env["campos_ausentes"]}
    detalhe_ip = ", incluindo IP de país desconhecido" if sinais["ip_pais_desconhecido"] else ""
    return {
        "risco_ia": risco,
        "confianca": "MEDIA",
        "explicacao": (
            f"Auditoria local por regras: {sinais['quantidade']} sinal(is) de alerta"
            f"{detalhe_ip}. Pela regra independente da nota, o risco é {risco.lower()}."
        ),
        "evidencias_a_favor": sinais["sinais"] + favor_cliente + favor_cartao,
        "evidencias_contra": contra_cliente + contra_cartao,
        "dados_ausentes": sorted(NOMES_LEGIVEIS.get(campo, campo) for campo in ausentes),
    }
