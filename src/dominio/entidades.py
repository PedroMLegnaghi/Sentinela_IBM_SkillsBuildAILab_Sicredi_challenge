"""Entidades do associado e da filial (ESPECIFICACAO, seção 17; Issue #92).

Só dataclasses: nada de pandas, FastAPI ou adaptadores. Os identificadores da base ficam em
campos internos, fora do ``repr`` e da comparação, e nunca saem pela API.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

PAPEIS = ("associado", "auditor", "gerente")
TIPOS_CARTAO = ("debito", "credito")
SITUACOES = ("APROVADA", "AGUARDANDO", "BLOQUEADA", "CONTESTADA")
RESPOSTAS_ASSOCIADO = ("sim", "nao")


@dataclass(frozen=True)
class Filial:
    """Agência da cooperativa."""

    id_filial: str
    nome: str


@dataclass(frozen=True)
class Perfil:
    """Quem pode abrir sessão: um funcionário ou um associado com login."""

    id_perfil: str
    nome: str
    papel: str
    id_filial: str

    def __post_init__(self) -> None:
        """Garante um papel conhecido."""
        if self.papel not in PAPEIS:
            raise ValueError(f"Papel desconhecido: {self.papel}. Use {', '.join(PAPEIS)}.")


@dataclass(frozen=True)
class Funcionario(Perfil):
    """Auditor ou gerente de uma filial."""

    def __post_init__(self) -> None:
        """Garante que o papel é auditor ou gerente."""
        super().__post_init__()
        if self.papel == "associado":
            raise ValueError("Funcionário é auditor ou gerente, nunca associado.")


@dataclass
class Associado:
    """Cliente da carteira de uma filial; só quem tem login tem saldo e limite."""

    id_associado: str
    nome: str
    id_filial: str
    posicao: int
    tem_login: bool = False
    saldo: float = 0.0
    limite_total: float = 0.0
    limite_disponivel: float = 0.0
    id_cliente_base: str | None = field(default=None, repr=False, compare=False)

    def como_perfil(self) -> Perfil:
        """Perfil de sessão do associado (só faz sentido para quem tem login)."""
        return Perfil(self.id_associado, self.nome, "associado", self.id_filial)


@dataclass
class Cartao:
    """Cartão de débito ou crédito de um associado."""

    id_cartao: str
    id_associado: str
    tipo: str
    final: str
    bloqueado: bool = False
    ids_cartao_base: tuple[str, ...] = field(default=(), repr=False, compare=False)

    def __post_init__(self) -> None:
        """Garante um tipo conhecido."""
        if self.tipo not in TIPOS_CARTAO:
            raise ValueError(f"Tipo de cartão desconhecido: {self.tipo}.")


@dataclass
class RespostaAssociado:
    """Resposta do associado ao aviso "Foi você?"."""

    resposta: str
    em: str


@dataclass
class Bloqueio:
    """Quem bloqueou a compra, quando e por quê; sem auditor, foi o Sentinela."""

    em: str
    motivo: str
    id_auditor: str | None = None
    nota_auditor: str | None = None
    correto: bool | None = None


@dataclass
class Compra:
    """Compra de março da base ou compra simulada no site, com a situação atual."""

    id_compra: str
    id_associado: str
    id_filial: str
    id_cartao: str | None
    estabelecimento: str
    data_hora: str | None
    valor: float | None
    tipo_transacao: str
    modalidade_transacao: str
    situacao: str
    decisao: str | None = None
    simulada: bool = False
    id_notificacao: str | None = None
    resposta_associado: RespostaAssociado | None = None
    bloqueio: Bloqueio | None = None
    saldo_aplicado: bool = False
    id_transacao_base: int | None = field(default=None, repr=False, compare=False)
    analise: dict[str, Any] | None = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        """Garante uma situação conhecida."""
        if self.situacao not in SITUACOES:
            raise ValueError(f"Situação desconhecida: {self.situacao}.")


@dataclass
class Contestacao:
    """Registro de "Não reconheço esta compra"."""

    id_contestacao: str
    id_compra: str
    id_associado: str
    id_filial: str
    em: str
    valor_devolvido: float
