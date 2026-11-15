"""Repositórios em memória (Issue #92): dicionários protegidos por ``threading.Lock``.

Reiniciar a API apaga tudo, como as auditorias e as notificações; aceitável no protótipo.
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from typing import Generic, TypeVar

from src.dominio.entidades import Associado, Cartao, Compra, Contestacao, Filial, Perfil
from src.dominio.rotulos import EventoRotulo
from src.portas.repositorios import Repositorios

T = TypeVar("T")


class _Tabela(Generic[T]):
    """Dicionário ``id → entidade`` com lock; base dos repositórios concretos."""

    def __init__(self, chave: Callable[[T], str], prefixo_id: str = "", digitos_id: int = 6):
        self._itens: dict[str, T] = {}
        self._lock = threading.Lock()
        self._chave = chave
        self._prefixo_id = prefixo_id
        self._digitos_id = digitos_id
        self._contador = 0

    def obter(self, identificador: str) -> T | None:
        """Entidade pelo id, ou None."""
        with self._lock:
            return self._itens.get(identificador)

    def salvar(self, item: T) -> None:
        """Insere ou atualiza a entidade pela sua chave."""
        with self._lock:
            self._itens[self._chave(item)] = item

    def listar(self) -> list[T]:
        """Todas as entidades, na ordem em que foram gravadas."""
        with self._lock:
            return list(self._itens.values())

    def filtrar(self, predicado: Callable[[T], bool]) -> list[T]:
        """Entidades que satisfazem o predicado, na ordem em que foram gravadas."""
        with self._lock:
            return [item for item in self._itens.values() if predicado(item)]

    def proximo_id(self) -> str:
        """Identificador opaco sequencial (``<prefixo><número com zeros à esquerda>``)."""
        with self._lock:
            self._contador += 1
            return f"{self._prefixo_id}{self._contador:0{self._digitos_id}d}"

    def __len__(self) -> int:
        """Quantidade de entidades gravadas."""
        with self._lock:
            return len(self._itens)


class FiliaisEmMemoria(_Tabela[Filial]):
    """Filiais."""

    def __init__(self) -> None:
        super().__init__(lambda filial: filial.id_filial)


class PerfisEmMemoria(_Tabela[Perfil]):
    """Perfis de sessão."""

    def __init__(self) -> None:
        super().__init__(lambda perfil: perfil.id_perfil)


class AssociadosEmMemoria(_Tabela[Associado]):
    """Associados das carteiras."""

    def __init__(self) -> None:
        super().__init__(lambda associado: associado.id_associado)

    def listar_por_filial(self, id_filial: str) -> list[Associado]:
        """Carteira de uma filial."""
        return self.filtrar(lambda associado: associado.id_filial == id_filial)


class CartoesEmMemoria(_Tabela[Cartao]):
    """Cartões."""

    def __init__(self) -> None:
        super().__init__(lambda cartao: cartao.id_cartao)

    def listar_por_associado(self, id_associado: str) -> list[Cartao]:
        """Cartões de um associado."""
        return self.filtrar(lambda cartao: cartao.id_associado == id_associado)


class ComprasEmMemoria(_Tabela[Compra]):
    """Compras de março e simuladas; ids ``cmp-000001``, ``cmp-000002``..."""

    def __init__(self) -> None:
        super().__init__(lambda compra: compra.id_compra, prefixo_id="cmp-", digitos_id=6)

    def obter_por_notificacao(self, id_notificacao: str) -> Compra | None:
        """Compra ligada a um aviso, ou None."""
        encontradas = self.filtrar(lambda compra: compra.id_notificacao == id_notificacao)
        return encontradas[0] if encontradas else None

    def listar_por_associado(self, id_associado: str) -> list[Compra]:
        """Compras de um associado."""
        return self.filtrar(lambda compra: compra.id_associado == id_associado)

    def listar_por_filial(self, id_filial: str) -> list[Compra]:
        """Compras da carteira de uma filial."""
        return self.filtrar(lambda compra: compra.id_filial == id_filial)


class ContestacoesEmMemoria(_Tabela[Contestacao]):
    """Contestações; ids ``ctt-0001``, ``ctt-0002``..."""

    def __init__(self) -> None:
        super().__init__(lambda c: c.id_contestacao, prefixo_id="ctt-", digitos_id=4)

    def listar_por_associado(self, id_associado: str) -> list[Contestacao]:
        """Contestações de um associado."""
        return self.filtrar(lambda c: c.id_associado == id_associado)

    def listar_por_filial(self, id_filial: str) -> list[Contestacao]:
        """Contestações da carteira de uma filial."""
        return self.filtrar(lambda c: c.id_filial == id_filial)


class RotulosEmMemoria:
    """Histórico de rótulos em memória (testes e demonstração sem disco)."""

    def __init__(self) -> None:
        self._eventos: list[EventoRotulo] = []
        self._lock = threading.Lock()

    def acrescentar(self, evento: EventoRotulo) -> None:
        """Acrescenta um evento ao fim do histórico."""
        with self._lock:
            self._eventos.append(evento)

    def listar(self) -> list[EventoRotulo]:
        """Todos os eventos, na ordem em que foram gravados."""
        with self._lock:
            return list(self._eventos)


def criar_repositorios_vazios() -> Repositorios:
    """Conjunto de repositórios em memória, ainda sem dados."""
    return Repositorios(
        filiais=FiliaisEmMemoria(),
        perfis=PerfisEmMemoria(),
        associados=AssociadosEmMemoria(),
        cartoes=CartoesEmMemoria(),
        compras=ComprasEmMemoria(),
        contestacoes=ContestacoesEmMemoria(),
        rotulos=RotulosEmMemoria(),
    )
