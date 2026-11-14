"""Validação do relatório da auditoria e cálculo do parecer (ESPECIFICACAO, seção 13).

O parecer é calculado aqui, em Python, comparando o risco apontado pela auditoria com a
decisão do modelo; o modelo de linguagem nunca decide o parecer (ADR-012).
"""

from __future__ import annotations

import re
from typing import Any

RISCOS = ("BAIXO", "SUSPEITO", "ALTO")
CONFIANCAS = ("BAIXA", "MEDIA", "ALTA")
RISCO_PARA_DECISAO = {"ALTO": "BLOQUEAR", "SUSPEITO": "PEDIR_CONFIRMACAO", "BAIXO": "APROVAR"}
MAX_CARACTERES_EXPLICACAO = 600
CAMPOS_LISTA = ("evidencias_a_favor", "evidencias_contra", "dados_ausentes")
RETICENCIAS = "…"
# Fim de frase: pontuação seguida de espaço ou do fim do texto (o ponto de "100.0" não conta)
_FIM_DE_FRASE = re.compile(r"[.!?](?=\s|$)")


def encurtar_explicacao(texto: str, limite: int = MAX_CARACTERES_EXPLICACAO) -> str:
    """Corta a explicação no fim de uma frase, sem quebrar palavras.

    Args:
        texto: Explicação já sem espaços nas pontas.
        limite: Tamanho máximo em caracteres.

    Returns:
        O próprio texto, se couber; senão, o trecho até a última frase completa dentro do
        limite; sem frase completa, o trecho até o último espaço, terminado em "…".
    """
    if len(texto) <= limite:
        return texto
    trecho = texto[:limite]
    fins = list(_FIM_DE_FRASE.finditer(trecho))
    if fins:
        return trecho[: fins[-1].end()]
    trecho = texto[: limite - len(RETICENCIAS)]
    espaco = trecho.rfind(" ")
    if espaco > 0:
        trecho = trecho[:espaco]
    return trecho.rstrip(" ,;:") + RETICENCIAS


def calcular_parecer(risco_ia: str | None, confianca: str, decisao_modelo: str) -> str:
    """Compara o risco da auditoria com a decisão do modelo.

    Args:
        risco_ia: "BAIXO", "SUSPEITO", "ALTO" ou None.
        confianca: "BAIXA", "MEDIA" ou "ALTA".
        decisao_modelo: Decisão do modelo ("APROVAR", "PEDIR_CONFIRMACAO" ou "BLOQUEAR").

    Returns:
        "INCONCLUSIVO" sem risco ou com confiança BAIXA; "CONFIRMA" quando o risco
        corresponde à decisão; "DIVERGE" nos demais casos.
    """
    if risco_ia is None or confianca == "BAIXA":
        return "INCONCLUSIVO"
    if RISCO_PARA_DECISAO[risco_ia] == decisao_modelo:
        return "CONFIRMA"
    return "DIVERGE"


def _validar_lista(valor: Any, campo: str) -> list[str]:
    """Garante que o campo é uma lista de textos.

    Args:
        valor: Valor recebido.
        campo: Nome do campo, para a mensagem de erro.

    Returns:
        A lista, com os itens convertidos em texto e sem itens vazios.

    Raises:
        ValueError: Se o valor não for uma lista.
    """
    if not isinstance(valor, list):
        raise ValueError(f"O campo {campo} precisa ser uma lista.")
    return [str(item).strip() for item in valor if str(item).strip()]


def validar_parcial(dados: dict[str, Any]) -> dict[str, Any]:
    """Valida a parte do relatório produzida pela auditoria (IA ou modo local).

    Args:
        dados: Dicionário com risco_ia, confianca, explicacao e as três listas.

    Returns:
        Cópia normalizada, com a explicação de até 600 caracteres terminando numa frase
        completa (``encurtar_explicacao``).

    Raises:
        ValueError: Se faltar campo ou algum valor estiver fora do permitido.
    """
    risco = dados.get("risco_ia")
    if risco is not None and risco not in RISCOS:
        raise ValueError(f"risco_ia inválido: {risco!r}")
    confianca = dados.get("confianca")
    if confianca not in CONFIANCAS:
        raise ValueError(f"confianca inválida: {confianca!r}")
    explicacao = str(dados.get("explicacao") or "").strip()
    if not explicacao:
        raise ValueError("A explicação está vazia.")
    parcial = {
        "risco_ia": risco,
        "confianca": confianca,
        "explicacao": encurtar_explicacao(explicacao),
    }
    for campo in CAMPOS_LISTA:
        parcial[campo] = _validar_lista(dados.get(campo, []), campo)
    return parcial


def finalizar_relatorio(
    parcial: dict[str, Any],
    decisao_modelo: str,
    ferramentas_usadas: list[dict[str, str]],
    fonte: str,
    modelo: str,
) -> dict[str, Any]:
    """Monta o Relatorio completo da ESPECIFICACAO, seção 13.

    Args:
        parcial: Saída de ``validar_parcial``.
        decisao_modelo: Decisão do modelo para a mesma transação.
        ferramentas_usadas: Ferramentas chamadas, na ordem, com o resumo de cada uma.
        fonte: "watsonx" ou "local".
        modelo: Nome do modelo de linguagem, ou do modo local.

    Returns:
        Dicionário com os 10 campos do Relatorio.
    """
    return {
        "parecer": calcular_parecer(parcial["risco_ia"], parcial["confianca"], decisao_modelo),
        "risco_ia": parcial["risco_ia"],
        "confianca": parcial["confianca"],
        "explicacao": parcial["explicacao"],
        "evidencias_a_favor": parcial["evidencias_a_favor"],
        "evidencias_contra": parcial["evidencias_contra"],
        "dados_ausentes": parcial["dados_ausentes"],
        "ferramentas_usadas": list(ferramentas_usadas),
        "fonte": fonte,
        "modelo": modelo,
    }
