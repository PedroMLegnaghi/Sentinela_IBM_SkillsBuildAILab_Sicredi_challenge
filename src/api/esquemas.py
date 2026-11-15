"""Modelos Pydantic de entrada e saída da API do Sentinela (ESPECIFICACAO, seção 12.1)."""

from __future__ import annotations

from pydantic import BaseModel, field_validator

from src.associado.notificacoes import RESPOSTAS_VALIDAS


class EntradaAnalise(BaseModel):
    """Entrada do endpoint POST /api/analisar.

    Todas as variáveis do modelo são opcionais; ausentes viram NaN no agente.
    """

    valor: float | None = None
    hora: float | None = None
    madrugada: float | None = None
    credito: float | None = None
    nao_presente: float | None = None
    ip_pais_desconhecido: float | None = None
    vel_cartao_terminal_1h: float | None = None
    qtd_transacoes_cartao_1min: float | None = None
    qtd_token_carteira_3m: float | None = None
    dist_terminal_anterior_km: float | None = None
    risco_estabelecimento: float | None = None
    data_hora: str | None = None
    tipo_transacao: str | None = None
    modalidade_transacao: str | None = None
    auditar: bool = True


class SinalSchema(BaseModel):
    """Sinal de alerta."""

    id: str
    descricao: str


class ContribuicaoSchema(BaseModel):
    """Contribuição de uma variável para a nota."""

    variavel: str
    nome: str
    contribuicao: float


class AnaliseSchema(BaseModel):
    """Resultado da análise de uma transação (ESPECIFICACAO, seção 12.1)."""

    nota: float
    decisao: str
    decisao_legivel: str
    sinais: list[SinalSchema]
    explicacao: str
    contribuicoes: list[ContribuicaoSchema]
    latencia_ms: float


class ItemFilaSchema(BaseModel):
    """Item da fila de demonstração."""

    id_transacao: int
    nota: float
    decisao: str
    valor: float | None
    data_hora: str | None
    tipo_transacao: str
    modalidade_transacao: str
    n_sinais: int


class TransacaoSchema(BaseModel):
    """Dados completos de uma transação da fila."""

    id_transacao: int
    data_hora: str | None
    valor: float | None
    tipo_transacao: str
    modalidade_transacao: str
    hora: float | None
    madrugada: float | None
    credito: float | None
    nao_presente: float | None
    ip_pais_desconhecido: float | None
    vel_cartao_terminal_1h: float | None
    qtd_transacoes_cartao_1min: float | None
    qtd_token_carteira_3m: float | None
    dist_terminal_anterior_km: float | None
    risco_estabelecimento: float | None


class ItemHistoricoSchema(BaseModel):
    """Item do histórico do cartão."""

    data_hora: str | None
    valor: float | None
    tipo_transacao: str
    modalidade_transacao: str
    dist_terminal_anterior_km: float | None


class PerfilAssociadoSchema(BaseModel):
    """Perfil do associado (ESPECIFICACAO, seção 12.1 — Issue #64)."""

    compras_anteriores: int
    mediana_valor: float | None
    valor_atual_sobre_mediana: float | None
    hora_mais_comum: int | None
    percentual_madrugada: float | None
    percentual_credito_nao_presente: float | None


class RespostaSchema(BaseModel):
    """Resposta do analista (ESPECIFICACAO, seção 12.1)."""

    id_transacao: int
    resposta: str
    registrado_em: str


class EntradaResposta(BaseModel):
    """Entrada do endpoint POST /api/respostas."""

    id_transacao: int
    resposta: str

    @field_validator("resposta")
    @classmethod
    def validar_resposta(cls, v: str) -> str:
        """Valida que a resposta é 'fraude' ou 'legitima'."""
        if v not in ("fraude", "legitima"):
            raise ValueError("Resposta deve ser 'fraude' ou 'legitima'.")
        return v


class NotificacaoSchema(BaseModel):
    """Notificação ao associado (ESPECIFICACAO, seção 15)."""

    id_notificacao: str
    id_transacao: int | None
    tipo: str
    mensagem: str
    fonte_mensagem: str
    criada_em: str
    status: str
    respondida_em: str | None
    resultado: str | None


class EntradaRespostaAssociado(BaseModel):
    """Entrada do endpoint POST /api/notificacoes/{id_notificacao}/resposta."""

    resposta: str

    @field_validator("resposta")
    @classmethod
    def validar_resposta(cls, v: str) -> str:
        """Valida que a resposta do associado é 'sim' ou 'nao'."""
        if v not in RESPOSTAS_VALIDAS:
            raise ValueError("Resposta deve ser 'sim' ou 'nao'.")
        return v
