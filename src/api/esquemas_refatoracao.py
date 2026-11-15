"""Modelos Pydantic das rotas do associado e da filial (ESPECIFICACAO, seção 17.3)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

MODALIDADES = ("cartao_presente", "cartao_nao_presente")


class EntradaSessao(BaseModel):
    """Entrada de ``POST /api/sessao``."""

    id_perfil: str


class EntradaCompraSimulada(BaseModel):
    """Entrada de ``POST /api/associado/compras``: cartão, estabelecimento, data e variáveis."""

    cartao: str
    estabelecimento: str = Field(min_length=1, max_length=60)
    data_hora: str
    valor: float | None = None
    hora: float | None = None
    madrugada: float | None = None
    nao_presente: float | None = None
    ip_pais_desconhecido: float | None = None
    vel_cartao_terminal_1h: float | None = None
    qtd_transacoes_cartao_1min: float | None = None
    qtd_token_carteira_3m: float | None = None
    dist_terminal_anterior_km: float | None = None
    risco_estabelecimento: float | None = None
    modalidade_transacao: str | None = None

    @field_validator("data_hora")
    @classmethod
    def validar_data_hora(cls, v: str) -> str:
        """Exige data em ISO 8601 (por exemplo, 2025-03-31T14:20:00)."""
        try:
            datetime.fromisoformat(v)
        except ValueError as erro:
            raise ValueError(
                "data_hora deve estar em ISO 8601, como 2025-03-31T14:20:00."
            ) from erro
        return v

    @field_validator("modalidade_transacao")
    @classmethod
    def validar_modalidade(cls, v: str | None) -> str | None:
        """Aceita só as duas modalidades da base."""
        if v is not None and v not in MODALIDADES:
            raise ValueError(f"modalidade_transacao deve ser {' ou '.join(MODALIDADES)}.")
        return v


class FilialSchema(BaseModel):
    """Filial resumida."""

    id_filial: str
    nome: str


class PerfilSchema(BaseModel):
    """Perfil de sessão."""

    id_perfil: str
    nome: str
    papel: str
    filial: FilialSchema


class PerfisSchema(BaseModel):
    """Saída de ``GET /api/sessao/perfis``."""

    perfis: list[PerfilSchema]


class SessaoSchema(BaseModel):
    """Saída de ``POST /api/sessao``."""

    token: str
    perfil: PerfilSchema


class CartaoSchema(BaseModel):
    """Cartao do contrato."""

    id: str
    tipo: str
    final: str
    bloqueado: bool


class CompraExtratoSchema(BaseModel):
    """CompraExtrato do contrato."""

    id_compra: str
    estabelecimento: str
    data_hora: str | None
    valor: float | None
    tipo_transacao: str
    modalidade_transacao: str
    final_cartao: str
    situacao: str
    id_notificacao: str | None
    simulada: bool


class PendenteSchema(BaseModel):
    """Aviso ainda sem resposta."""

    id_notificacao: str
    id_compra: str
    valor: float | None
    data_hora: str | None


class AssociadoResumoSchema(BaseModel):
    """Nome e filial do associado."""

    nome: str
    filial: str


class InicioSchema(BaseModel):
    """Saída de ``GET /api/associado/inicio``."""

    associado: AssociadoResumoSchema
    saldo: float
    limite_total: float
    limite_disponivel: float
    cartoes: list[CartaoSchema]
    pendentes: list[PendenteSchema]
    ultimas_compras: list[CompraExtratoSchema]


class ExtratoSchema(BaseModel):
    """Saída de ``GET /api/associado/extrato``."""

    total: int
    itens: list[CompraExtratoSchema]


class BloqueioSchema(BaseModel):
    """Bloqueio como o associado vê."""

    por: str
    em: str
    motivo: str


class RespostaAssociadoSchema(BaseModel):
    """Resposta do associado ao aviso."""

    resposta: str
    em: str


class DetalheCompraSchema(CompraExtratoSchema):
    """Saída de ``GET /api/associado/compras/{id_compra}``."""

    bloqueio: BloqueioSchema | None
    resposta_associado: RespostaAssociadoSchema | None
    pode_contestar: bool


class CompraSimuladaSchema(BaseModel):
    """Saída de ``POST /api/associado/compras``."""

    compra: CompraExtratoSchema
    id_notificacao: str | None


class ContestacaoSchema(BaseModel):
    """Saída de ``POST /api/associado/compras/{id_compra}/contestacao``."""

    compra: CompraExtratoSchema
    cartao: CartaoSchema


class ItemFilaFilialSchema(BaseModel):
    """ItemFilaFilial do contrato."""

    id_compra: str
    nota: float | None
    decisao: str | None
    associado: str
    final_cartao: str
    data_hora: str | None
    valor: float | None
    tipo_transacao: str
    modalidade_transacao: str
    situacao: str
    veredito_ia: str | None


class FilaFilialSchema(BaseModel):
    """Saída de ``GET /api/filial/fila``."""

    filial: FilialSchema
    total: int
    itens: list[ItemFilaFilialSchema]


class HistoricoAssociadoSchema(BaseModel):
    """Histórico agregado que a filial pode ver."""

    compras_90d: int
    valor_mediano: float | None
    contestacoes: int


class AssociadoNaFilialSchema(BaseModel):
    """O associado como a filial vê: abreviado, final do cartão e histórico agregado."""

    nome_abreviado: str
    final_cartao: str
    historico: HistoricoAssociadoSchema


class DetalheFilialSchema(BaseModel):
    """Saída de ``GET /api/filial/compras/{id_compra}``."""

    compra: ItemFilaFilialSchema
    analise: dict[str, Any]
    auditoria: dict[str, Any] | None
    associado: AssociadoNaFilialSchema
    resposta_associado: RespostaAssociadoSchema | None
    bloqueio: BloqueioSchema | None
