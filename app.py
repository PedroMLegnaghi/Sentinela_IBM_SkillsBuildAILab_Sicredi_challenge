"""Ponto de entrada da interface do Sentinela.

Orquestra a navegação entre páginas e configura a barra lateral.
Nenhuma regra de negócio nem texto literal neste módulo.
"""

import streamlit as st

from src.interface import (
    dados,
    pagina_como_funciona,
    pagina_desempenho,
    pagina_fila,
    pagina_respostas,
    pagina_simulador,
    textos,
)
from src.interface.tema import (
    ICONE_COMO_FUNCIONA,
    ICONE_DESEMPENHO,
    ICONE_ERRO,
    ICONE_FILA,
    ICONE_RESPOSTAS,
    ICONE_SIMULADOR,
)

st.set_page_config(
    page_title=textos.TITULO_APP,
    page_icon=":material/shield:",
    layout="wide",
)

erros = dados.verificar_arquivos()
for erro in erros:
    st.error(erro, icon=ICONE_ERRO)
if erros:
    st.stop()

pagina = st.navigation(
    [
        st.Page(
            pagina_fila.renderizar,
            title="Fila de alertas",
            icon=ICONE_FILA,
            url_path="fila",
            default=True,
        ),
        st.Page(
            pagina_desempenho.renderizar,
            title="Desempenho",
            icon=ICONE_DESEMPENHO,
            url_path="desempenho",
        ),
        st.Page(
            pagina_como_funciona.renderizar,
            title="Como funciona",
            icon=ICONE_COMO_FUNCIONA,
            url_path="como-funciona",
        ),
        st.Page(
            pagina_simulador.renderizar,
            title=textos.TITULO_SIMULADOR,
            icon=ICONE_SIMULADOR,
            url_path="simulador",
        ),
        st.Page(
            pagina_respostas.renderizar,
            title=textos.TITULO_RESPOSTAS,
            icon=ICONE_RESPOSTAS,
            url_path="respostas",
        ),
    ]
)

with st.sidebar:
    st.toggle(
        textos.ROTULO_TOGGLE_GRANITE,
        value=True,
        key="usar_granite",
        help=textos.AJUDA_TOGGLE_GRANITE,
    )
    usar_granite = st.session_state.get("usar_granite", True)
    if not usar_granite:
        st.caption(textos.STATUS_GRANITE_DESLIGADO)
    elif dados.granite_esta_disponivel():
        st.caption(textos.STATUS_GRANITE_ON)
    else:
        st.caption(textos.STATUS_GRANITE_OFF)
    st.caption(textos.RODAPE_DADOS)

pagina.run()
