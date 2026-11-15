"""Canal do associado (ESPECIFICACAO, seção 15; ADR-015).

Quando a decisão é PEDIR_CONFIRMACAO ou BLOQUEAR, o Sentinela avisa o associado e registra a
resposta dele. É uma simulação: nada é enviado por SMS ou push; o "App do associado" do site
faz o papel do celular.
"""

from src.associado.mensagem import redigir_mensagem, validar_mensagem
from src.associado.notificacoes import (
    NotificacaoJaRespondida,
    criar_notificacao,
    listar,
    obter,
    obter_por_transacao,
    responder,
)

__all__ = [
    "NotificacaoJaRespondida",
    "criar_notificacao",
    "listar",
    "obter",
    "obter_por_transacao",
    "redigir_mensagem",
    "responder",
    "validar_mensagem",
]
