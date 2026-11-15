"""Portas dos repositórios (Issue #92): o domínio e a aplicação só conhecem estas interfaces.

Cada porta tem só os métodos que as regras usam. O adaptador de hoje é em memória; um de
Postgres implementa as mesmas assinaturas sem mexer nas regras.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from src.dominio.entidades import Associado, Cartao, Compra, Contestacao, Filial, Perfil
from src.dominio.rotulos import EventoRotulo


@runtime_checkable
class RepositorioFiliais(Protocol):
    """Filiais da cooperativa."""

    def obter(self, id_filial: str) -> Filial | None:
        """Filial pelo id, ou None."""
        ...

    def listar(self) -> list[Filial]:
        """Todas as filiais."""
        ...


@runtime_checkable
class RepositorioPerfis(Protocol):
    """Perfis que podem abrir sessão: funcionários e associados com login."""

    def obter(self, id_perfil: str) -> Perfil | None:
        """Perfil pelo id, ou None."""
        ...

    def listar(self) -> list[Perfil]:
        """Todos os perfis."""
        ...


@runtime_checkable
class RepositorioAssociados(Protocol):
    """Associados das carteiras, com ou sem login."""

    def obter(self, id_associado: str) -> Associado | None:
        """Associado pelo id, ou None."""
        ...

    def listar_por_filial(self, id_filial: str) -> list[Associado]:
        """Carteira de uma filial."""
        ...

    def salvar(self, associado: Associado) -> None:
        """Insere ou atualiza o associado."""
        ...


@runtime_checkable
class RepositorioCartoes(Protocol):
    """Cartões dos associados com login."""

    def obter(self, id_cartao: str) -> Cartao | None:
        """Cartão pelo id, ou None."""
        ...

    def listar_por_associado(self, id_associado: str) -> list[Cartao]:
        """Cartões de um associado."""
        ...

    def salvar(self, cartao: Cartao) -> None:
        """Insere ou atualiza o cartão."""
        ...


@runtime_checkable
class RepositorioCompras(Protocol):
    """Compras de março e compras simuladas."""

    def obter(self, id_compra: str) -> Compra | None:
        """Compra pelo id, ou None."""
        ...

    def obter_por_notificacao(self, id_notificacao: str) -> Compra | None:
        """Compra ligada a um aviso, ou None."""
        ...

    def listar_por_associado(self, id_associado: str) -> list[Compra]:
        """Compras de um associado, na ordem em que foram gravadas."""
        ...

    def listar_por_filial(self, id_filial: str) -> list[Compra]:
        """Compras da carteira de uma filial."""
        ...

    def salvar(self, compra: Compra) -> None:
        """Insere ou atualiza a compra."""
        ...

    def proximo_id(self) -> str:
        """Identificador opaco para uma compra nova."""
        ...


@runtime_checkable
class RepositorioContestacoes(Protocol):
    """Contestações ("Não reconheço esta compra")."""

    def obter(self, id_contestacao: str) -> Contestacao | None:
        """Contestação pelo id, ou None."""
        ...

    def listar_por_associado(self, id_associado: str) -> list[Contestacao]:
        """Contestações de um associado."""
        ...

    def listar_por_filial(self, id_filial: str) -> list[Contestacao]:
        """Contestações da carteira de uma filial."""
        ...

    def salvar(self, contestacao: Contestacao) -> None:
        """Insere ou atualiza a contestação."""
        ...

    def proximo_id(self) -> str:
        """Identificador opaco para uma contestação nova."""
        ...


@runtime_checkable
class RepositorioRotulos(Protocol):
    """Histórico de rótulos para o retreino: só acrescentar e listar, nunca editar ou apagar."""

    def acrescentar(self, evento: EventoRotulo) -> None:
        """Acrescenta um evento ao fim do histórico."""
        ...

    def listar(self) -> list[EventoRotulo]:
        """Todos os eventos, na ordem em que foram gravados."""
        ...


@dataclass(frozen=True)
class Repositorios:
    """Conjunto de repositórios que a aplicação recebe pronto de ``src.composicao``."""

    filiais: RepositorioFiliais
    perfis: RepositorioPerfis
    associados: RepositorioAssociados
    cartoes: RepositorioCartoes
    compras: RepositorioCompras
    contestacoes: RepositorioContestacoes
    rotulos: RepositorioRotulos
