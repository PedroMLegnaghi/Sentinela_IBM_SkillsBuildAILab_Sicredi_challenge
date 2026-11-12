"""Tokens visuais da interface: ícones, rótulos e proporções.

Define os estilos de cada decisão e as constantes de layout usadas em toda a interface.
Nenhum código hexadecimal aparece aqui — as cores vêm de st.error, st.warning e st.success.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class EstiloDecisao:
    """Estilo visual de uma decisão do agente.

    Args:
        rotulo_curto: Rótulo usado na fila e no filtro de decisões.
        emoji: Forma distinta para não depender de cor (acessibilidade).
        icone: Ícone Material da faixa de decisão.
        tipo_alerta: Tipo de alerta Streamlit ("error", "warning" ou "success").
    """

    rotulo_curto: str
    emoji: str
    icone: str
    tipo_alerta: str


DECISOES: dict[str, EstiloDecisao] = {
    "BLOQUEAR": EstiloDecisao("Bloquear", "⛔", ":material/block:", "error"),
    "PEDIR_CONFIRMACAO": EstiloDecisao(
        "Pedir confirmação", "⚠️", ":material/phone_in_talk:", "warning"
    ),
    "APROVAR": EstiloDecisao("Aprovar", "✅", ":material/check_circle:", "success"),
}

ORDEM_DECISOES: list[str] = ["BLOQUEAR", "PEDIR_CONFIRMACAO", "APROVAR"]

# Ícones das páginas de navegação
ICONE_FILA = ":material/list_alt:"
ICONE_DESEMPENHO = ":material/monitoring:"
ICONE_COMO_FUNCIONA = ":material/help:"

# Ícones do painel e da barra lateral
ICONE_FRAUDE = ":material/gpp_bad:"
ICONE_LEGITIMA = ":material/verified_user:"
ICONE_ERRO = ":material/error:"
ICONE_GRANITE_ON = ":material/check_circle:"
ICONE_GRANITE_OFF = ":material/cloud_off:"

# Layout
PROPORCAO_COLUNAS: tuple[int, int] = (3, 2)
ALTURA_TABELA_PX: int = 560
LINHAS_HISTORICO: int = 10
