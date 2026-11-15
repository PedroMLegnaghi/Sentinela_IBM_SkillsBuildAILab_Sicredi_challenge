"""Sessão simulada e estado da refatoração (ESPECIFICACAO, seção 17.1; Issue #94).

Não há senha: ``POST /api/sessao`` devolve um token opaco guardado em memória, e as rotas do
associado e da filial exigem o cabeçalho ``X-Sessao``. Este módulo também guarda os
repositórios da refatoração, montados uma única vez na primeira chamada.
"""

from __future__ import annotations

import logging
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

import pandas as pd
from fastapi import APIRouter, Header, HTTPException

from src import composicao
from src.agente import AgenteSentinela
from src.api import servicos
from src.api.esquemas_refatoracao import EntradaSessao, PerfisSchema, SessaoSchema
from src.aplicacao import associado as associado_app
from src.config import FIM_TESTE, INICIO_TESTE
from src.dominio.entidades import Perfil
from src.dominio.regras import MATRIZ
from src.portas.repositorios import Repositorios

logger = logging.getLogger(__name__)
router = APIRouter(tags=["sessao"])


@dataclass
class _Estado:
    """Repositórios e tokens vivos; mutável via atributos (sem global)."""

    repositorios: Repositorios | None = None
    tokens: dict[str, Perfil] = field(default_factory=dict)


_estado = _Estado()
_lock = threading.Lock()


def _decisoes_de_marco(base: pd.DataFrame, agente: AgenteSentinela) -> dict[int, str]:
    """Decisão do modelo para cada transação de março, calculada uma vez na subida."""
    marco = base[(base["data_hora"] >= INICIO_TESTE) & (base["data_hora"] < FIM_TESTE)]
    resultado = agente.analisar_lote(marco)
    return dict(zip(resultado["id_transacao"].astype(int), resultado["decisao"], strict=True))


def _montar_repositorios() -> Repositorios:
    """Repositórios da demonstração ligados à base e ao agente carregados pela API."""
    base = servicos._estado.base  # noqa: SLF001 (estado carregado na subida da API)
    agente = servicos._estado.agente  # noqa: SLF001
    decisoes = _decisoes_de_marco(base, agente) if base is not None and agente is not None else None
    repos = composicao.obter_repositorios(base, decisoes)
    avisos = associado_app.avisar_compras_de_marco(repos)
    logger.info(
        "Refatoração pronta: %d perfis, %d avisos de março.", len(repos.perfis.listar()), avisos
    )
    return repos


def obter_repositorios() -> Repositorios:
    """Repositórios da refatoração, montados na primeira chamada e reaproveitados depois."""
    with _lock:
        if _estado.repositorios is None:
            _estado.repositorios = _montar_repositorios()
        return _estado.repositorios


def perfil_para_dict(repos: Repositorios, perfil: Perfil) -> dict[str, Any]:
    """Perfil do contrato (seção 17.3), com a filial resumida."""
    filial = repos.filiais.obter(perfil.id_filial)
    if filial is None and perfil.id_filial == MATRIZ.id_filial:
        filial = MATRIZ
    return {
        "id_perfil": perfil.id_perfil,
        "nome": perfil.nome,
        "papel": perfil.papel,
        "filial": {"id_filial": perfil.id_filial, "nome": filial.nome if filial else ""},
    }


def sessao_com_papel(*papeis: str) -> Callable[..., Perfil]:
    """Dependência do FastAPI: lê ``X-Sessao`` e devolve o perfil; 401 sem sessão, 403 sem papel.

    Args:
        papeis: Papéis aceitos na rota ("associado", "auditor", "gerente", "matriz").

    Returns:
        Função a passar em ``Depends``.
    """

    def dependencia(x_sessao: str | None = Header(default=None, alias="X-Sessao")) -> Perfil:
        if not x_sessao:
            raise HTTPException(
                status_code=401,
                detail="Sessão ausente. Abra uma sessão em POST /api/sessao e envie X-Sessao.",
            )
        with _lock:
            perfil = _estado.tokens.get(x_sessao)
        if perfil is None:
            raise HTTPException(
                status_code=401, detail="Sessão desconhecida ou expirada. Entre de novo."
            )
        if perfil.papel not in papeis:
            raise HTTPException(status_code=403, detail=f"Esta área é só para {', '.join(papeis)}.")
        return perfil

    return dependencia


@router.get("/api/sessao/perfis", response_model=PerfisSchema)
def listar_perfis() -> dict[str, Any]:
    """Perfis do login simulado: 1 matriz, 2 gerentes, 4 auditores e 10 associados."""
    repos = obter_repositorios()
    return {"perfis": [perfil_para_dict(repos, p) for p in repos.perfis.listar()]}


@router.post("/api/sessao", response_model=SessaoSchema)
def abrir_sessao(entrada: EntradaSessao) -> dict[str, Any]:
    """Abre uma sessão para o perfil e devolve o token; perfil desconhecido → 404."""
    repos = obter_repositorios()
    perfil = repos.perfis.obter(entrada.id_perfil)
    if perfil is None:
        raise HTTPException(
            status_code=404,
            detail=f"Perfil '{entrada.id_perfil}' não existe. Veja GET /api/sessao/perfis.",
        )
    token = uuid4().hex
    with _lock:
        _estado.tokens[token] = perfil
    return {"token": token, "perfil": perfil_para_dict(repos, perfil)}
