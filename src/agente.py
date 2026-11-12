"""Agente Sentinela: sinais, decisão, pontuação e explicação de transações.

Uso: importar AgenteSentinela de src.agente
"""

import logging
import math
from http import HTTPStatus

import joblib
import pandas as pd
import requests

from src.config import (
    CAMINHO_MODELO,
    LIMIAR_DISTANCIA_KM,
    LIMIAR_RAJADA_1MIN,
    LIMIAR_RISCO_ESTABELECIMENTO,
    LIMIAR_TOKEN_CARTEIRA,
    LIMIAR_VALOR_ALTO,
    LIMIAR_VELOCIDADE_TERMINAL,
    MIN_SINAIS_CONFIRMAR,
    NOTA_BLOQUEAR,
    NOTA_CONFIRMAR,
    OLLAMA_MODELO,
    OLLAMA_TIMEOUT_DISPONIBILIDADE_S,
    OLLAMA_TIMEOUT_S,
    OLLAMA_URL,
    ROTULOS_DECISAO,
    VARIAVEIS_MODELO,
)

logger = logging.getLogger(__name__)


def granite_disponivel(timeout_s: float = OLLAMA_TIMEOUT_DISPONIBILIDADE_S) -> bool:
    """Verifica se o IBM Granite (Ollama) está disponível.

    Faz GET em {OLLAMA_URL}/api/tags e devolve True só se o status for 200.
    Qualquer requests.RequestException devolve False (registrado em log).
    """
    try:
        resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=timeout_s)
        return resp.status_code == HTTPStatus.OK
    except requests.RequestException as erro:
        logger.warning("Granite indisponível: %s", erro)
        return False


def _valor_valido(v) -> bool:
    """Retorna True se o valor não for None, NaN ou string vazia."""
    if v is None:
        return False
    try:
        if math.isnan(float(v)):
            return False
    except (TypeError, ValueError):
        pass
    return True


def calcular_sinais(transacao: dict) -> list[dict]:
    """Calcula os sinais de alerta de uma transação.

    Retorna lista de dicts {"id": ..., "descricao": ...}.
    Campos vazios, None ou NaN nunca disparam sinal e nunca geram erro.
    Ordem fixa conforme seção 8.2.
    """
    sinais = []

    v = transacao.get("vel_cartao_terminal_1h")
    if _valor_valido(v) and float(v) >= LIMIAR_VELOCIDADE_TERMINAL:
        sinais.append(
            {
                "id": "velocidade_terminal",
                "descricao": (
                    f"Cartão usado {float(v):.0f} vezes em terminais"
                    " na última hora (normal: até 5)."
                ),
            }
        )

    v = transacao.get("qtd_transacoes_cartao_1min")
    if _valor_valido(v) and float(v) >= LIMIAR_RAJADA_1MIN:
        sinais.append(
            {
                "id": "rajada_1min",
                "descricao": (
                    f"{float(v):.0f} transações do cartão" " no último minuto (normal: 1 ou 2)."
                ),
            }
        )

    v = transacao.get("qtd_token_carteira_3m")
    if _valor_valido(v) and float(v) >= LIMIAR_TOKEN_CARTEIRA:
        sinais.append(
            {
                "id": "token_carteira",
                "descricao": (
                    f"Token de carteira digital usado {float(v):.0f} vezes"
                    " em 3 meses (normal: até 14)."
                ),
            }
        )

    v = transacao.get("dist_terminal_anterior_km")
    if _valor_valido(v) and float(v) > LIMIAR_DISTANCIA_KM:
        sinais.append(
            {
                "id": "salto_geografico",
                "descricao": f"Terminal a {float(v):.0f} km do anterior em menos de uma hora.",
            }
        )

    mad = transacao.get("madrugada")
    hora = transacao.get("hora")
    if _valor_valido(mad) and int(mad) == 1:
        hora_val = float(hora) if _valor_valido(hora) else 0
        sinais.append(
            {
                "id": "madrugada",
                "descricao": f"Compra feita de madrugada, às {hora_val:.0f}h.",
            }
        )

    v = transacao.get("valor")
    if _valor_valido(v) and float(v) > LIMIAR_VALOR_ALTO:
        sinais.append(
            {
                "id": "valor_alto",
                "descricao": (
                    f"Valor de R$ {float(v):.2f}," " acima do padrão (mediana das compras: R$ 35)."
                ),
            }
        )

    cred = transacao.get("credito")
    nao_pres = transacao.get("nao_presente")
    if _valor_valido(cred) and _valor_valido(nao_pres) and int(cred) == 1 and int(nao_pres) == 1:
        sinais.append(
            {
                "id": "credito_nao_presente",
                "descricao": "Compra no crédito sem cartão presente (online).",
            }
        )

    v = transacao.get("ip_pais_desconhecido")
    if _valor_valido(v) and int(v) == 1:
        sinais.append(
            {
                "id": "ip_desconhecido",
                "descricao": "Endereço IP de país desconhecido.",
            }
        )

    v = transacao.get("risco_estabelecimento")
    if _valor_valido(v) and float(v) >= LIMIAR_RISCO_ESTABELECIMENTO:
        sinais.append(
            {
                "id": "estabelecimento_risco",
                "descricao": (f"Estabelecimento com risco {float(v):.0f} (normal: abaixo de 37)."),
            }
        )

    return sinais


def decidir(nota: float, sinais: list[dict]) -> str:
    """Decide a ação para a transação.

    Ordem: BLOQUEAR > PEDIR_CONFIRMACAO > APROVAR.
    """
    ids_sinais = {s["id"] for s in sinais}

    if nota >= NOTA_BLOQUEAR or "ip_desconhecido" in ids_sinais:
        return "BLOQUEAR"

    if nota >= NOTA_CONFIRMAR or len(sinais) >= MIN_SINAIS_CONFIRMAR:
        return "PEDIR_CONFIRMACAO"

    return "APROVAR"


class AgenteSentinela:
    """Agente principal de detecção de fraudes."""

    def __init__(self, caminho_modelo=CAMINHO_MODELO, base: pd.DataFrame | None = None):
        """Carrega o pipeline salvo em caminho_modelo.

        Levanta FileNotFoundError se o arquivo não existir.
        base: DataFrame preparado, usado apenas por historico_cartao.
        """
        if not caminho_modelo.exists():
            raise FileNotFoundError("Modelo não encontrado. Rode: python -m src.treinar_modelo")
        self._pipeline = joblib.load(caminho_modelo)
        self._base = base

    def pontuar(self, transacao: dict) -> float:
        """Pontua a transação de 0 a 100 (1 casa decimal).

        Chaves ausentes ou None viram NaN no DataFrame de entrada.
        """
        dados = {col: transacao.get(col) for col in VARIAVEIS_MODELO}
        df = pd.DataFrame([dados], columns=VARIAVEIS_MODELO)
        prob = self._pipeline.predict_proba(df)[0, 1]
        return round(float(prob) * 100, 1)

    def historico_cartao(self, id_cartao, antes_de=None, n: int = 10) -> pd.DataFrame:
        """Retorna as últimas n transações do cartão em self._base.

        Ordena da mais recente para a mais antiga.
        Se antes_de (datetime) for fornecido, filtra transações anteriores a ele.
        Retorna DataFrame vazio se base for None, id_cartao for vazio ou não houver registros.
        """
        if self._base is None:
            return pd.DataFrame()
        if not id_cartao or (isinstance(id_cartao, float) and math.isnan(id_cartao)):
            return pd.DataFrame()

        mask = self._base["id_cartao"] == id_cartao
        sub = self._base[mask].copy()

        if antes_de is not None:
            sub = sub[sub["data_hora"] < antes_de]

        if sub.empty:
            return pd.DataFrame()

        sub = sub.sort_values("data_hora", ascending=False).head(n)
        return sub.reset_index(drop=True)

    def explicar(
        self, transacao: dict, nota: float, sinais: list[dict], decisao: str, usar_llm: bool = True
    ) -> tuple[str, str]:
        """Gera explicação textual da decisão.

        Retorna (texto, fonte) onde fonte é "granite" ou "regras".
        Nunca levanta exceção de rede.
        """
        decisao_legivel = ROTULOS_DECISAO.get(decisao, decisao)

        if usar_llm:
            texto_llm = self._chamar_ollama(transacao, nota, sinais, decisao_legivel)
            if texto_llm:
                return texto_llm, "granite"

        texto = _texto_reserva(decisao_legivel, nota, sinais)
        return texto, "regras"

    def _chamar_ollama(
        self, transacao: dict, nota: float, sinais: list[dict], decisao_legivel: str
    ) -> str:
        """Tenta chamar o Ollama. Retorna string vazia em caso de qualquer falha."""
        if not granite_disponivel():
            return ""

        if sinais:
            linhas_sinais = "\n".join(f"- {s['descricao']}" for s in sinais)
        else:
            linhas_sinais = "- nenhum sinal de alerta"

        tipo = transacao.get("tipo_transacao", "")
        modalidade = transacao.get("modalidade_transacao", "")
        prompt = (
            "Você é um assistente de prevenção a fraudes de uma cooperativa de crédito.\n"
            "Explique para um analista, em exatamente 3 frases curtas em português do Brasil,\n"
            "por que a transação abaixo recebeu a decisão indicada. Use apenas os dados\n"
            "fornecidos. Não invente informações. Não use listas nem markdown.\n\n"
            f"Decisão: {decisao_legivel}\n"
            f"Nota de risco: {nota}/100\n"
            f"Valor: R$ {transacao.get('valor', '')}\n"
            f"Data e hora: {transacao.get('data_hora', '')}\n"
            f"Tipo: {tipo}, {modalidade}\n"
            f"Sinais de alerta:\n{linhas_sinais}"
        )

        try:
            resp = requests.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": OLLAMA_MODELO,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.2, "num_predict": 200},
                },
                timeout=OLLAMA_TIMEOUT_S,
            )
            if resp.status_code != HTTPStatus.OK:
                return ""
            texto = resp.json().get("response", "").strip()
            return texto if texto else ""
        except (requests.RequestException, ValueError, KeyError) as erro:
            logger.warning("Falha ao chamar o Ollama: %s", erro)
            return ""

    def analisar(self, transacao: dict, usar_llm: bool = True) -> dict:
        """Analisa uma transação e devolve o dicionário completo de resultado.

        Chaves devolvidas: nota, sinais, decisao, decisao_legivel,
        explicacao, fonte_explicacao.
        """
        sinais = calcular_sinais(transacao)
        nota = self.pontuar(transacao)
        decisao = decidir(nota, sinais)
        decisao_legivel = ROTULOS_DECISAO.get(decisao, decisao)
        explicacao, fonte_explicacao = self.explicar(
            transacao, nota, sinais, decisao, usar_llm=usar_llm
        )
        return {
            "nota": nota,
            "sinais": sinais,
            "decisao": decisao,
            "decisao_legivel": decisao_legivel,
            "explicacao": explicacao,
            "fonte_explicacao": fonte_explicacao,
        }

    def analisar_lote(self, df: pd.DataFrame) -> pd.DataFrame:
        """Versão rápida para múltiplas linhas, sem LLM.

        Devolve cópia de df com colunas novas: nota (float, 1 casa),
        n_sinais (int) e decisao (str).
        """
        resultado = df.copy()

        entradas = df[VARIAVEIS_MODELO].copy()
        probas = self._pipeline.predict_proba(entradas)[:, 1]
        resultado["nota"] = (probas * 100).round(1)

        n_sinais_list = []
        decisao_list = []
        for _, row in df.iterrows():
            transacao = row.to_dict()
            sinais = calcular_sinais(transacao)
            dec = decidir(float(resultado.at[row.name, "nota"]), sinais)
            n_sinais_list.append(len(sinais))
            decisao_list.append(dec)

        resultado["n_sinais"] = n_sinais_list
        resultado["decisao"] = decisao_list

        return resultado


def _texto_reserva(decisao_legivel: str, nota: float, sinais: list[dict]) -> str:
    """Gera o texto de reserva quando o LLM não está disponível."""
    if sinais:
        descricoes = " ".join(s["descricao"] for s in sinais)
        return f"Decisão: {decisao_legivel} (nota {nota}/100). Motivos: {descricoes}"
    return (
        f"Decisão: {decisao_legivel} (nota {nota}/100). "
        "Nenhum sinal de alerta foi encontrado; "
        "a transação segue o padrão de compras legítimas."
    )
