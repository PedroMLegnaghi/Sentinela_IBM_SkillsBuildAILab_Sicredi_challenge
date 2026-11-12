"""Página Fila de alertas do Sentinela.

Exibe a fila ordenada pelo risco, o painel da transação selecionada
e os botões de resposta do analista.
"""

import logging

import pandas as pd
import streamlit as st

from src.config import CAMINHO_FEEDBACK, ROTULOS_DECISAO
from src.interface import dados, feedback, painel_contribuicoes, painel_mensagem, textos
from src.interface.formatacao import (
    escapar_markdown,
    formatar_data_hora,
    formatar_inteiro,
    formatar_modalidade,
    formatar_moeda,
    formatar_nota,
    formatar_tipo,
    rotulo_resposta,
)
from src.interface.tema import (
    ALTURA_TABELA_PX,
    DECISOES,
    ICONE_ERRO,
    ICONE_FRAUDE,
    ICONE_LEGITIMA,
    LINHAS_HISTORICO,
    ORDEM_DECISOES,
    PROPORCAO_COLUNAS,
)

logger = logging.getLogger(__name__)


def _ao_escolher_id() -> None:
    """Callback do selectbox de ID: sincroniza a seleção."""
    st.session_state["id_selecionado"] = st.session_state["busca_id"]


def _renderizar_indicadores(fila: pd.DataFrame) -> None:
    """Exibe os quatro indicadores de contagem no topo da página.

    Args:
        fila: DataFrame completo da fila (sem filtro).
    """
    contagens = dados.contar_por_decisao(fila)
    total = sum(contagens.values())
    col_fila, col_bloquear, col_confirmar, col_aprovar = st.columns(4)
    col_fila.metric(textos.METRICA_NA_FILA, formatar_inteiro(total), help=textos.AJUDA_NA_FILA)
    for col, chave in zip((col_bloquear, col_confirmar, col_aprovar), ORDEM_DECISOES, strict=True):
        col.metric(DECISOES[chave].rotulo_curto, formatar_inteiro(contagens[chave]))


def _montar_tabela_exibicao(visiveis: pd.DataFrame) -> pd.DataFrame:
    """Constrói o DataFrame de exibição com as 8 colunas do design (seção 7.3).

    Args:
        visiveis: DataFrame filtrado da fila.

    Returns:
        DataFrame pronto para st.dataframe.
    """
    return pd.DataFrame(
        {
            "ID": visiveis["id_transacao"],
            "Nota": visiveis["nota"],
            "Decisão": visiveis["decisao"].map(
                lambda d: f"{DECISOES[d].emoji} {DECISOES[d].rotulo_curto}"
            ),
            "Valor (R$)": visiveis["valor"],
            "Data e hora": visiveis["data_hora"],
            "Tipo": visiveis["tipo_transacao"].map(formatar_tipo),
            "Modalidade": visiveis["modalidade_transacao"].map(formatar_modalidade),
            "Sinais": visiveis["n_sinais"],
        }
    )


def _atualizar_selecao(
    ids_visiveis: list[int], evento, visiveis: pd.DataFrame  # noqa: ANN001
) -> None:
    """Sincroniza id_selecionado a partir do clique na tabela e do selectbox.

    Atualiza st.session_state["id_selecionado"] se o analista clicou numa
    linha diferente da última; depois renderiza o selectbox de busca por ID.

    Args:
        ids_visiveis: Lista de IDs na ordem da tabela filtrada.
        evento: Objeto de evento devolvido por st.dataframe.
        visiveis: DataFrame filtrado, usado para formatar as opções do selectbox.
    """
    linhas = evento.selection.rows
    selecao_tabela = ids_visiveis[linhas[0]] if linhas else None
    if selecao_tabela is not None and selecao_tabela != st.session_state.get(
        "ultima_selecao_tabela"
    ):
        st.session_state["id_selecionado"] = selecao_tabela
    st.session_state["ultima_selecao_tabela"] = selecao_tabela

    st.session_state["busca_id"] = st.session_state["id_selecionado"]

    def _formatar_id(id_t: int) -> str:
        nota_val = float(visiveis.loc[visiveis["id_transacao"] == id_t, "nota"].iloc[0])
        dec_val = visiveis.loc[visiveis["id_transacao"] == id_t, "decisao"].iloc[0]
        return f"ID {id_t} · {formatar_nota(nota_val)} · {DECISOES[dec_val].rotulo_curto}"

    st.selectbox(
        textos.BUSCA_ID,
        options=ids_visiveis,
        key="busca_id",
        format_func=_formatar_id,
        on_change=_ao_escolher_id,
    )


def _exibir_dataframe_fila(tabela: pd.DataFrame):  # noqa: ANN201
    """Renderiza o st.dataframe da fila com a configuração de colunas do design (seção 7.3).

    Args:
        tabela: DataFrame de exibição montado por _montar_tabela_exibicao.

    Returns:
        Objeto de evento do st.dataframe (usado para ler a seleção de linha).
    """
    return st.dataframe(
        tabela,
        key="tabela_fila",
        on_select="rerun",
        selection_mode="single-row",
        hide_index=True,
        height=ALTURA_TABELA_PX,
        column_config={
            "ID": st.column_config.NumberColumn(format="%d"),
            "Nota": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.1f"),
            "Decisão": st.column_config.TextColumn(),
            "Valor (R$)": st.column_config.NumberColumn(format="%.2f"),
            "Data e hora": st.column_config.DatetimeColumn(format="DD/MM/YYYY HH:mm"),
            "Tipo": st.column_config.TextColumn(),
            "Modalidade": st.column_config.TextColumn(),
            "Sinais": st.column_config.NumberColumn(format="%d", help=textos.AJUDA_COLUNA_SINAIS),
        },
        use_container_width=True,
    )


def _renderizar_filtro_e_tabela(fila: pd.DataFrame) -> tuple[pd.DataFrame, int | None]:
    """Renderiza o filtro, a tabela e a caixa de ID; devolve visiveis e id_selecionado.

    Args:
        fila: DataFrame completo da fila.

    Returns:
        Tupla (visiveis, id_selecionado); id_selecionado é None se visiveis estiver vazio.
    """
    filtro = st.pills(
        textos.FILTRO_DECISOES,
        options=ORDEM_DECISOES,
        selection_mode="multi",
        default=["BLOQUEAR", "PEDIR_CONFIRMACAO"],
        format_func=lambda chave: f"{DECISOES[chave].emoji} {DECISOES[chave].rotulo_curto}",
        key="filtro_decisoes",
    )

    visiveis = fila[fila["decisao"].isin(filtro)].reset_index(drop=True)

    if visiveis.empty:
        st.info(textos.VAZIO_FILTRO)
        return visiveis, None

    st.caption(
        textos.CONTAGEM_TABELA.format(
            mostradas=formatar_inteiro(len(visiveis)),
            total=formatar_inteiro(len(fila)),
        )
    )

    ids_visiveis = visiveis["id_transacao"].tolist()
    if st.session_state.get("id_selecionado") not in ids_visiveis:
        st.session_state["id_selecionado"] = ids_visiveis[0]

    evento = _exibir_dataframe_fila(_montar_tabela_exibicao(visiveis))
    _atualizar_selecao(ids_visiveis, evento, visiveis)

    return visiveis, st.session_state["id_selecionado"]


def _gravar_resposta(
    transacao: dict, id_selecionado: int, resposta_analista: str, icone: str, toast: str
) -> None:
    """Tenta gravar uma resposta do analista; exibe toast ou erro.

    Args:
        transacao: Dicionário da transação em análise.
        id_selecionado: ID da transação.
        resposta_analista: "fraude" ou "legitima".
        icone: Ícone do toast de sucesso.
        toast: Texto do toast de sucesso.
    """
    try:
        feedback.registrar_resposta(
            CAMINHO_FEEDBACK,
            feedback.RespostaAnalista(
                id_transacao=id_selecionado,
                nota=transacao.get("nota", 0.0),
                decisao=transacao.get("decisao", ""),
                resposta_analista=resposta_analista,
                registrado_em=pd.Timestamp.now().to_pydatetime(),
            ),
        )
        st.toast(toast, icon=icone)
    except OSError as erro:
        logger.error("Erro ao gravar resposta: %s", erro)
        st.error(textos.ERRO_GRAVAR, icon=ICONE_ERRO)


def _renderizar_resposta_atual(id_selecionado: int) -> None:
    """Lê e exibe a última resposta registrada para a transação.

    Args:
        id_selecionado: ID da transação a consultar.
    """
    try:
        ultima = feedback.ler_ultima_resposta(CAMINHO_FEEDBACK, id_selecionado)
        if ultima is not None:
            st.caption(
                textos.RESPOSTA_ATUAL.format(
                    resposta=rotulo_resposta(ultima.resposta_analista),
                    data_hora=formatar_data_hora(pd.Timestamp(ultima.registrado_em)),
                )
            )
        else:
            st.caption(textos.SEM_RESPOSTA)
    except ValueError:
        st.warning(textos.ERRO_LER_RESPOSTAS)


def _renderizar_resposta(transacao: dict, id_selecionado: int) -> None:
    """Renderiza os botões de resposta e a resposta atual gravada.

    Args:
        transacao: Dicionário da transação em análise.
        id_selecionado: ID da transação selecionada.
    """
    st.markdown(f"**{textos.TITULO_RESPOSTA}**")
    col_fraude, col_legitima = st.columns(2)
    if col_fraude.button(
        textos.BOTAO_FRAUDE,
        icon=ICONE_FRAUDE,
        key=f"fraude_{id_selecionado}",
        use_container_width=True,
    ):
        _gravar_resposta(transacao, id_selecionado, "fraude", ICONE_FRAUDE, textos.TOAST_FRAUDE)

    if col_legitima.button(
        textos.BOTAO_LEGITIMA,
        icon=ICONE_LEGITIMA,
        key=f"legitima_{id_selecionado}",
        use_container_width=True,
    ):
        _gravar_resposta(
            transacao, id_selecionado, "legitima", ICONE_LEGITIMA, textos.TOAST_LEGITIMA
        )

    _renderizar_resposta_atual(id_selecionado)


def _renderizar_historico(agente, transacao: dict) -> None:  # noqa: ANN001
    """Renderiza o expander de histórico do cartão.

    Args:
        agente: Instância de AgenteSentinela.
        transacao: Dicionário da transação em análise.
    """
    id_cartao = transacao.get("id_cartao")
    if not id_cartao or (isinstance(id_cartao, float) and pd.isna(id_cartao)):
        st.caption(textos.HISTORICO_SEM_CARTAO)
        return

    data_hora = transacao.get("data_hora")
    hist = agente.historico_cartao(
        id_cartao, antes_de=data_hora if pd.notna(data_hora) else None, n=LINHAS_HISTORICO
    )
    with st.expander(textos.TITULO_HISTORICO.format(n=len(hist))):
        if hist.empty:
            st.caption(textos.HISTORICO_VAZIO)
        else:
            st.table(
                pd.DataFrame(
                    {
                        "Data e hora": hist["data_hora"].map(formatar_data_hora),
                        "Valor": hist["valor"].map(formatar_moeda),
                        "Tipo": hist["tipo_transacao"].map(formatar_tipo),
                        "Modalidade": hist["modalidade_transacao"].map(formatar_modalidade),
                        "Distância do terminal anterior (km)": hist[
                            "dist_terminal_anterior_km"
                        ].map(lambda v: f"{v:.0f}" if pd.notna(v) else "—"),
                    }
                )
            )


def _renderizar_cabecalho_painel(transacao_base: dict, analise: dict) -> None:
    """Exibe cabeçalho, resumo, faixa de decisão e barra de nota do painel.

    Args:
        transacao_base: Campos brutos da transação selecionada.
        analise: Resultado de agente.analisar com nota, decisao e sinais.
    """
    id_selecionado = transacao_base["id_transacao"]
    decisao = analise["decisao"]
    nota = analise["nota"]
    estilo = DECISOES[decisao]

    st.header(textos.TITULO_PAINEL.format(id=id_selecionado))
    st.caption(
        escapar_markdown(
            textos.RESUMO_PAINEL.format(
                data_hora=formatar_data_hora(
                    pd.Timestamp(transacao_base["data_hora"])
                    if pd.notna(transacao_base.get("data_hora"))
                    else None
                ),
                tipo=formatar_tipo(transacao_base.get("tipo_transacao", "")),
                modalidade=formatar_modalidade(transacao_base.get("modalidade_transacao", "")),
                valor=formatar_moeda(transacao_base.get("valor")),
            )
        )
    )
    getattr(st, estilo.tipo_alerta)(f"**{ROTULOS_DECISAO[decisao]}**", icon=estilo.icone)
    st.progress(nota / 100, text=textos.NOTA_TEXTO.format(nota=formatar_nota(nota)))


def _renderizar_sinais(sinais: list[dict]) -> None:
    """Exibe o título e a lista de sinais de alerta, ou a mensagem de ausência.

    Args:
        sinais: Lista de dicts com chave "descricao" retornada pelo agente.
    """
    if sinais:
        st.markdown(f"**{textos.TITULO_SINAIS.format(quantidade=len(sinais))}**")
        st.markdown("\n".join(f"- {escapar_markdown(s['descricao'])}" for s in sinais))
    else:
        st.markdown(f"**{textos.TITULO_SINAIS.format(quantidade=0)}**")
        st.markdown(textos.SEM_SINAIS)


def _renderizar_painel(visiveis: pd.DataFrame, id_selecionado: int) -> None:
    """Renderiza o painel lateral com análise da transação selecionada.

    Args:
        visiveis: DataFrame filtrado.
        id_selecionado: ID da transação a exibir.
    """
    agente = dados.carregar_agente()
    usar_llm = st.session_state["usar_granite"]
    chave = (id_selecionado, usar_llm)
    analises = st.session_state.setdefault("analises", {})

    transacao_base = visiveis[visiveis["id_transacao"] == id_selecionado].iloc[0].to_dict()

    if chave not in analises:
        msg = textos.GERANDO_EXPLICACAO if usar_llm else textos.MONTANDO_EXPLICACAO
        with st.spinner(msg):
            analises[chave] = agente.analisar(transacao_base, usar_llm=usar_llm)

    analise = analises[chave]
    _renderizar_cabecalho_painel(transacao_base, analise)
    _renderizar_sinais(analise["sinais"])
    painel_contribuicoes.renderizar(transacao_base)

    fonte = analise["fonte_explicacao"]
    st.markdown(f"**{textos.TITULO_EXPLICACAO}**")
    st.markdown(escapar_markdown(analise["explicacao"]))
    if fonte == "granite":
        st.caption(textos.FONTE_GRANITE)
    elif usar_llm:
        st.caption(textos.FONTE_REGRAS_INDISPONIVEL)
    else:
        st.caption(textos.FONTE_REGRAS)
    painel_mensagem.renderizar(transacao_base, analise)

    _renderizar_resposta({**transacao_base, **analise}, id_selecionado)
    _renderizar_historico(agente, transacao_base)


def renderizar() -> None:
    """Renderiza a página Fila de alertas."""
    st.title(textos.TITULO_FILA)
    st.caption(textos.LEGENDA_FILA)

    fila = dados.carregar_fila()

    _renderizar_indicadores(fila)

    esquerda, direita = st.columns(PROPORCAO_COLUNAS, gap="large")

    with esquerda:
        visiveis, id_selecionado = _renderizar_filtro_e_tabela(fila)

    if id_selecionado is not None:
        with direita, st.container(border=True):
            _renderizar_painel(visiveis, id_selecionado)
