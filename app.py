"""Interface Streamlit do Sentinela — Prevenção a fraudes.

Executar: streamlit run app.py
"""

import json
from datetime import datetime

import pandas as pd
import streamlit as st

from src.agente import AgenteSentinela
from src.config import (
    CAMINHO_AVALIACAO,
    CAMINHO_FEEDBACK,
    CAMINHO_METRICAS,
    CAMINHO_MODELO,
    CAMINHO_PREPARADO,
)

st.set_page_config(page_title="Sentinela", layout="wide")

# ---------------------------------------------------------------------------
# Verificação de pré-requisitos
# ---------------------------------------------------------------------------

if not CAMINHO_MODELO.exists():
    st.error("Modelo não encontrado. Rode: python -m src.treinar_modelo")
    st.stop()

if not CAMINHO_PREPARADO.exists():
    st.error("Dados preparados não encontrados. Rode: python -m src.preparar_dados")
    st.stop()

# ---------------------------------------------------------------------------
# Carga com cache
# ---------------------------------------------------------------------------

@st.cache_resource
def carregar_agente(base: pd.DataFrame) -> AgenteSentinela:
    """Carrega o agente uma única vez."""
    return AgenteSentinela(base=base)


@st.cache_data
def carregar_fila() -> pd.DataFrame:
    """Lê o parquet, monta a fila de março e roda analisar_lote."""
    df = pd.read_parquet(CAMINHO_PREPARADO)

    marco = df[
        (df["data_hora"] >= "2025-03-01") & (df["data_hora"] < "2025-04-01")
    ].copy()

    fraudes = marco[marco["fraude"] == 1]
    legitimas = marco[marco["fraude"] == 0].sample(n=2000, random_state=42)
    fila_raw = pd.concat([fraudes, legitimas], ignore_index=True)

    agente = AgenteSentinela(base=df)
    fila = agente.analisar_lote(fila_raw)
    fila = fila.sort_values("nota", ascending=False).reset_index(drop=True)
    return fila, df


# Mapa de texto legível por decisão (espelha src/agente.py sem reimportar privado)
_DECISAO_LEGIVEL = {
    "BLOQUEAR": "Bloquear e enviar ao analista",
    "PEDIR_CONFIRMACAO": "Pedir confirmação ao cliente",
    "APROVAR": "Aprovar",
}

# ---------------------------------------------------------------------------
# Barra lateral
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("Sentinela")
    pagina = st.radio("Navegação", ["Fila de alertas", "Desempenho"])
    usar_llm = st.checkbox("Explicar com IBM Granite (Ollama)", value=True)
    st.caption("Dados 100% sintéticos (Sicredi)")

# ---------------------------------------------------------------------------
# Carregamento
# ---------------------------------------------------------------------------

fila, df_base = carregar_fila()
agente = carregar_agente(df_base)

# Colunas exibidas na tabela (fraude e decisao_sistema_atual nunca aparecem)
COLUNAS_TABELA = [
    "id_transacao", "data_hora", "valor", "tipo_transacao",
    "modalidade_transacao", "nota", "n_sinais", "decisao",
]

# ---------------------------------------------------------------------------
# Função auxiliar: colorir linhas
# ---------------------------------------------------------------------------

def _colorir(row):
    decisao = row.get("decisao", "")
    if decisao == "BLOQUEAR":
        cor = "background-color: #ffd5d5"
    elif decisao == "PEDIR_CONFIRMACAO":
        cor = "background-color: #fff5cc"
    else:
        cor = "background-color: #d5f5d5"
    return [cor] * len(row)

# ---------------------------------------------------------------------------
# Página: Fila de alertas
# ---------------------------------------------------------------------------

if pagina == "Fila de alertas":

    st.header("Fila de alertas")

    # 4 métricas do topo
    total = len(fila)
    bloqueadas = int((fila["decisao"] == "BLOQUEAR").sum())
    confirmacoes = int((fila["decisao"] == "PEDIR_CONFIRMACAO").sum())
    aprovadas = int((fila["decisao"] == "APROVAR").sum())

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Transações na fila", f"{total:,}")
    c2.metric("Bloqueadas", f"{bloqueadas:,}")
    c3.metric("Pedir confirmação", f"{confirmacoes:,}")
    c4.metric("Aprovadas", f"{aprovadas:,}")

    # Filtro por decisão
    opcoes = ["BLOQUEAR", "PEDIR_CONFIRMACAO", "APROVAR"]
    filtro = st.multiselect(
        "Filtrar por decisão",
        options=opcoes,
        default=["BLOQUEAR", "PEDIR_CONFIRMACAO"],
    )

    fila_filtrada = fila[fila["decisao"].isin(filtro)] if filtro else fila.iloc[:0]

    # Tabela com cores
    st.dataframe(
        fila_filtrada[COLUNAS_TABELA].style.apply(_colorir, axis=1),
        use_container_width=True,
        hide_index=True,
    )

    # Selectbox de transação
    if fila_filtrada.empty:
        st.info("Nenhuma transação no filtro selecionado.")
        st.stop()

    opcoes_select = [
        f"{row['id_transacao']} | nota {row['nota']} | "
        f"{_DECISAO_LEGIVEL.get(row['decisao'], row['decisao'])} | R$ {row['valor']:.2f}"
        for _, row in fila_filtrada.iterrows()
    ]
    idx_escolhido = st.selectbox(
        "Escolha uma transação para analisar",
        options=range(len(opcoes_select)),
        format_func=lambda i: opcoes_select[i],
    )

    linha = fila_filtrada.iloc[idx_escolhido]
    transacao = linha.to_dict()
    decisao = transacao["decisao"]
    decisao_legivel = _DECISAO_LEGIVEL.get(decisao, decisao)

    st.divider()

    # Decisão em destaque
    if decisao == "BLOQUEAR":
        st.error(f"**Decisão: {decisao_legivel}**")
    elif decisao == "PEDIR_CONFIRMACAO":
        st.warning(f"**Decisão: {decisao_legivel}**")
    else:
        st.success(f"**Decisão: {decisao_legivel}**")

    # Nota com progress
    nota = float(transacao["nota"])
    st.write(f"**Nota de risco:** {nota}/100")
    st.progress(int(nota))

    # Sinais de alerta
    from src.agente import calcular_sinais
    sinais = calcular_sinais(transacao)
    st.write("**Sinais de alerta:**")
    if sinais:
        for s in sinais:
            st.write(f"- {s['descricao']}")
    else:
        st.write("- Nenhum sinal de alerta.")

    # Explicação com spinner
    with st.spinner("Gerando explicação..."):
        resultado = agente.analisar(transacao, usar_llm=usar_llm)

    st.write("**Explicação:**")
    st.write(resultado["explicacao"])

    fonte = resultado["fonte_explicacao"]
    if fonte == "granite":
        st.caption("Explicação gerada por: IBM Granite 4")
    else:
        st.caption("Explicação gerada por: regras")

    # Histórico do cartão
    id_cartao = transacao.get("id_cartao")
    data_hora = transacao.get("data_hora")
    historico = agente.historico_cartao(id_cartao, antes_de=data_hora)
    st.write("**Histórico do cartão:**")
    if historico.empty:
        st.write("Nenhum histórico disponível.")
    else:
        cols_hist = [c for c in COLUNAS_TABELA if c in historico.columns]
        st.dataframe(historico[cols_hist], use_container_width=True, hide_index=True)

    # Botões de feedback
    st.divider()
    col_a, col_b = st.columns(2)

    def _gravar_feedback(id_transacao, nota, decisao, resposta):
        """Acrescenta uma linha em data/feedback.csv."""
        CAMINHO_FEEDBACK.parent.mkdir(parents=True, exist_ok=True)
        cabecalho = not CAMINHO_FEEDBACK.exists()
        with open(CAMINHO_FEEDBACK, "a", encoding="utf-8") as f:
            if cabecalho:
                f.write("registrado_em,id_transacao,nota,decisao,resposta_analista\n")
            agora = datetime.now().isoformat(timespec="seconds")
            f.write(f"{agora},{id_transacao},{nota},{decisao},{resposta}\n")

    if col_a.button("Confirmar fraude", use_container_width=True):
        _gravar_feedback(transacao["id_transacao"], nota, decisao, "fraude")
        st.toast("Resposta registrada")

    if col_b.button("Marcar como legítima", use_container_width=True):
        _gravar_feedback(transacao["id_transacao"], nota, decisao, "legitima")
        st.toast("Resposta registrada")

# ---------------------------------------------------------------------------
# Página: Desempenho
# ---------------------------------------------------------------------------

elif pagina == "Desempenho":

    st.header("Desempenho do modelo")

    with open(CAMINHO_METRICAS, encoding="utf-8") as f:
        metricas = json.load(f)

    with open(CAMINHO_AVALIACAO, encoding="utf-8") as f:
        avaliacao = json.load(f)

    # Métricas gerais
    c1, c2, c3 = st.columns(3)
    c1.metric("PR-AUC", f"{metricas['pr_auc']:.4f}")
    c2.metric("ROC-AUC", f"{metricas['roc_auc']:.4f}")
    c3.metric("Fraudes no teste", metricas["teste"]["fraudes"])

    st.divider()

    # Tabela comparativa Sentinela × Sistema atual em março
    st.subheader("Comparação em março de 2025")

    ft = avaliacao["fraudes_total"]
    s = avaliacao["sentinela"]
    sa = avaliacao["sistema_atual"]

    pct_sent = s["fraudes_bloqueadas"] / ft * 100 if ft > 0 else 0
    pct_atual = sa["fraudes_bloqueadas"] / ft * 100 if ft > 0 else 0
    nao_bloq_sent = ft - s["fraudes_bloqueadas"]

    tabela_comp = pd.DataFrame({
        "": ["Sistema atual", "Sentinela"],
        "Fraudes bloqueadas": [sa["fraudes_bloqueadas"], s["fraudes_bloqueadas"]],
        "Fraudes não bloqueadas": [sa["fraudes_nao_bloqueadas"], nao_bloq_sent],
        "% fraudes bloqueadas": [f"{pct_atual:.1f}%", f"{pct_sent:.1f}%"],
    })
    st.dataframe(tabela_comp, use_container_width=True, hide_index=True)

    # Gráfico de barras: fraudes bloqueadas
    st.subheader("Fraudes bloqueadas: Sistema atual × Sentinela")
    df_grafico = pd.DataFrame(
        {"Fraudes bloqueadas": [sa["fraudes_bloqueadas"], s["fraudes_bloqueadas"]]},
        index=["Sistema atual", "Sentinela"],
    )
    st.bar_chart(df_grafico)

    # Tabela de limiares
    st.subheader("Desempenho por limiar de corte")
    df_limiares = pd.DataFrame(metricas["limiares"])
    df_limiares.columns = ["Limiar", "Alertas", "Fraudes detectadas", "Precisão", "Recall"]
    st.dataframe(df_limiares, use_container_width=True, hide_index=True)

    st.info(
        "Dados sintéticos: o resultado é otimista. "
        "Em produção o modelo precisa de monitoramento e retreino."
    )
