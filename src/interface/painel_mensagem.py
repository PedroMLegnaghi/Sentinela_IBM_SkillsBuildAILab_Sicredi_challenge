"""Painel da mensagem de confirmação ao cliente.

Exibe a mensagem SMS que seria enviada ao cliente quando a decisão
é PEDIR_CONFIRMACAO, com a opção de simular o envio.
Implementado na Issue #23.
"""


def renderizar(transacao: dict, analise: dict) -> None:
    """Renderiza o painel com a mensagem de confirmação ao cliente.

    Só exibido quando a decisão é PEDIR_CONFIRMACAO.

    Args:
        transacao: Dicionário com os dados da transação selecionada.
        analise: Dicionário com nota, decisao, sinais e explicação.
    """
    # TODO(#23, 2026-11-13): implementar a geração da mensagem SMS com IBM Granite
    # ou modelo fixo, e o botão "Simular envio" (Issue #23)
    pass
