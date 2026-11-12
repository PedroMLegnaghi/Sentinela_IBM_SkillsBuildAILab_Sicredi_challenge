"""Interface Streamlit do Sentinela — Prevenção a fraudes.

Executar: streamlit run app.py
"""

import json
from datetime import datetime

import pandas as pd
import streamlit as st

from src.agente import AgenteSentinela, calcular_sinais
from src.config import (
    CAMINHO_AVALIACAO,
    CAMINHO_FEEDBACK,
    CAMINHO_METRICAS,
    CAMINHO_MODELO,
    CAMINHO_PREPARADO,
)

# ---------------------------------------------------------------------------
# Configuração da página
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Sentinela",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS global — tipografia, cores, cartões e badges
st.markdown("""
<style>
/* Fonte e fundo */
html, body, [class*="css"] {
    font-family: "Inter", "Segoe UI", system-ui, sans-serif;
}

/* Cabeçalho principal */
.sent-page-title {
    font-size: 1.6rem;
    font-weight: 700;
    color: #1a1a2e;
    margin-bottom: 0.15rem;
    letter-spacing: -0.3px;
}
.sent-page-subtitle {
    font-size: 0.85rem;
    color: #6b7280;
    margin-bottom: 1.4rem;
}

/* Cartão de KPI */
.kpi-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    text-align: center;
    height: 100%;
}
.kpi-card .kpi-label {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #6b7280;
    margin-bottom: 0.3rem;
}
.kpi-card .kpi-value {
    font-size: 1.9rem;
    font-weight: 700;
    line-height: 1;
}
.kpi-card.kpi-total  .kpi-value { color: #1a1a2e; }
.kpi-card.kpi-block  .kpi-value { color: #dc2626; }
.kpi-card.kpi-warn   .kpi-value { color: #d97706; }
.kpi-card.kpi-ok     .kpi-value { color: #16a34a; }

/* Badge de decisão inline */
.badge {
    display: inline-block;
    padding: 0.18em 0.65em;
    border-radius: 99px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
.badge-block  { background: #fee2e2; color: #991b1b; }
.badge-warn   { background: #fef3c7; color: #92400e; }
.badge-ok     { background: #dcfce7; color: #166534; }

/* Painel de detalhe */
.detail-section {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 1rem;
}
.detail-section h4 {
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #6b7280;
    margin: 0 0 0.6rem 0;
}

/* Linha de sinal */
.sinal-row {
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
    padding: 0.35rem 0;
    border-bottom: 1px solid #f3f4f6;
    font-size: 0.9rem;
    color: #374151;
}
.sinal-row:last-child { border-bottom: none; }
.sinal-icon { font-size: 1rem; flex-shrink: 0; margin-top: 1px; }

/* Barra de nota */
.nota-wrap {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin: 0.4rem 0 0.15rem;
}
.nota-number {
    font-size: 2.2rem;
    font-weight: 700;
    min-width: 3.5rem;
    line-height: 1;
}
.nota-bar-bg {
    flex: 1;
    height: 10px;
    background: #e5e7eb;
    border-radius: 99px;
    overflow: hidden;
}
.nota-bar-fill {
    height: 100%;
    border-radius: 99px;
    transition: width 0.4s ease;
}
.nota-low    { color: #16a34a; }
.nota-mid    { color: #d97706; }
.nota-high   { color: #dc2626; }

/* Botão de feedback */
div[data-testid="stButton"] button {
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.88rem;
    padding: 0.55rem 1rem;
    transition: transform 0.1s;
}
div[data-testid="stButton"] button:active { transform: scale(0.97); }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #1a1a2e;
}
section[data-testid="stSidebar"] * { color: #e5e7eb !important; }
section[data-testid="stSidebar"] .stRadio label { font-size: 0.9rem; }
section[data-testid="stSidebar"] .stCheckbox label { font-size: 0.85rem; }

/* Separador sutil */
hr { border-color: #e5e7eb; margin: 1.2rem 0; }

/* Remove padding excessivo do st.metric padrão quando usado junto */
div[data-testid="metric-container"] { background: transparent; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Verificação de pré-requisitos
# ---------------------------------------------------------------------------

if not CAMINHO_MODELO.exists():
    st.error("⚠️ Modelo não encontrado. Rode: `python -m src.treinar_modelo`")
    st.stop()

if not CAMINHO_PREPARADO.exists():
    st.error("⚠️ Dados preparados não encontrados. Rode: `python -m src.preparar_dados`")
    st.stop()

# ---------------------------------------------------------------------------
# Carga com cache
# ---------------------------------------------------------------------------

@st.cache_resource
def carregar_agente(base: pd.DataFrame) -> AgenteSentinela:
    return AgenteSentinela(base=base)


@st.cache_data
def carregar_fila():
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


# Mapa de texto legível
_DECISAO_LEGIVEL = {
    "BLOQUEAR": "Bloquear e enviar ao analista",
    "PEDIR_CONFIRMACAO": "Pedir confirmação ao cliente",
    "APROVAR": "Aprovar",
}

# ---------------------------------------------------------------------------
# Barra lateral
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("## 🛡️ Sentinela")
    st.markdown("---")
    pagina = st.radio(
        "Navegação",
        ["Fila de alertas", "Desempenho"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    usar_llm = st.checkbox("Explicar com IBM Granite (Ollama)", value=True)
    st.markdown("---")
    st.caption("Dados 100% sintéticos (Sicredi)")

# ---------------------------------------------------------------------------
# Carregamento
# ---------------------------------------------------------------------------

fila, df_base = carregar_fila()
agente = carregar_agente(df_base)

COLUNAS_TABELA = [
    "id_transacao", "data_hora", "valor", "tipo_transacao",
    "modalidade_transacao", "nota", "n_sinais", "decisao",
]


# ---------------------------------------------------------------------------
# Auxiliares de UI
# ---------------------------------------------------------------------------

def _badge_html(decisao: str) -> str:
    cls = {"BLOQUEAR": "badge-block", "PEDIR_CONFIRMACAO": "badge-warn", "APROVAR": "badge-ok"}
    label = {"BLOQUEAR": "Bloquear", "PEDIR_CONFIRMACAO": "Confirmar", "APROVAR": "Aprovar"}
    return f'<span class="badge {cls.get(decisao, "")}">{label.get(decisao, decisao)}</span>'


def _colorir(row):
    dec = row.get("decisao", "")
    cores = {
        "BLOQUEAR": "background-color:#fee2e2; color:#7f1d1d",
        "PEDIR_CONFIRMACAO": "background-color:#fef9c3; color:#78350f",
        "APROVAR": "background-color:#f0fdf4; color:#14532d",
    }
    cor = cores.get(dec, "")
    return [cor] * len(row)


def _nota_html(nota: float) -> str:
    if nota >= 70:
        fill_color, text_cls = "#dc2626", "nota-high"
    elif nota >= 30:
        fill_color, text_cls = "#d97706", "nota-mid"
    else:
        fill_color, text_cls = "#16a34a", "nota-low"
    return f"""
    <div class="nota-wrap">
        <span class="nota-number {text_cls}">{nota:.0f}</span>
        <div style="flex:1">
            <div style="font-size:0.72rem;color:#6b7280;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px">
                Nota de risco / 100
            </div>
            <div class="nota-bar-bg">
                <div class="nota-bar-fill" style="width:{nota}%;background:{fill_color}"></div>
            </div>
        </div>
    </div>"""


def _kpi_card(label: str, value, kind: str) -> str:
    return f"""
    <div class="kpi-card kpi-{kind}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
    </div>"""


def _gravar_feedback(id_transacao, nota, decisao, resposta):
    CAMINHO_FEEDBACK.parent.mkdir(parents=True, exist_ok=True)
    cabecalho = not CAMINHO_FEEDBACK.exists()
    with open(CAMINHO_FEEDBACK, "a", encoding="utf-8") as f:
        if cabecalho:
            f.write("registrado_em,id_transacao,nota,decisao,resposta_analista\n")
        agora = datetime.now().isoformat(timespec="seconds")
        f.write(f"{agora},{id_transacao},{nota},{decisao},{resposta}\n")


# ---------------------------------------------------------------------------
# Página: Fila de alertas
# ---------------------------------------------------------------------------

if pagina == "Fila de alertas":

    st.markdown('<p class="sent-page-title">Fila de alertas</p>', unsafe_allow_html=True)
    st.markdown('<p class="sent-page-subtitle">Transações de março/2025 — ordenadas por risco decrescente</p>', unsafe_allow_html=True)

    total = len(fila)
    bloqueadas = int((fila["decisao"] == "BLOQUEAR").sum())
    confirmacoes = int((fila["decisao"] == "PEDIR_CONFIRMACAO").sum())
    aprovadas = int((fila["decisao"] == "APROVAR").sum())

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(_kpi_card("Total na fila", f"{total:,}", "total"), unsafe_allow_html=True)
    c2.markdown(_kpi_card("Bloqueadas", f"{bloqueadas:,}", "block"), unsafe_allow_html=True)
    c3.markdown(_kpi_card("Pedir confirmação", f"{confirmacoes:,}", "warn"), unsafe_allow_html=True)
    c4.markdown(_kpi_card("Aprovadas", f"{aprovadas:,}", "ok"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Filtro
    col_f1, col_f2 = st.columns([3, 1])
    with col_f1:
        filtro = st.multiselect(
            "Filtrar por decisão",
            options=["BLOQUEAR", "PEDIR_CONFIRMACAO", "APROVAR"],
            default=["BLOQUEAR", "PEDIR_CONFIRMACAO"],
        )

    fila_filtrada = fila[fila["decisao"].isin(filtro)].copy() if filtro else fila.iloc[:0].copy()

    # Tabela
    st.dataframe(
        fila_filtrada[COLUNAS_TABELA].style.apply(_colorir, axis=1),
        use_container_width=True,
        hide_index=True,
        height=280,
        column_config={
            "id_transacao": st.column_config.NumberColumn("ID", format="%d", width="small"),
            "data_hora": st.column_config.DatetimeColumn("Data/hora", format="DD/MM HH:mm"),
            "valor": st.column_config.NumberColumn("Valor (R$)", format="R$ %.2f"),
            "tipo_transacao": st.column_config.TextColumn("Tipo"),
            "modalidade_transacao": st.column_config.TextColumn("Modalidade"),
            "nota": st.column_config.ProgressColumn("Nota", min_value=0, max_value=100, format="%.1f"),
            "n_sinais": st.column_config.NumberColumn("Sinais", format="%d", width="small"),
            "decisao": st.column_config.TextColumn("Decisão"),
        },
    )

    if fila_filtrada.empty:
        st.info("Nenhuma transação no filtro selecionado.")
        st.stop()

    st.markdown("<br>", unsafe_allow_html=True)

    # Selectbox
    opcoes_select = [
        f"#{row['id_transacao']}  •  nota {row['nota']:.0f}/100  •  "
        f"{_DECISAO_LEGIVEL.get(row['decisao'], row['decisao'])}  •  R$ {row['valor']:.2f}"
        for _, row in fila_filtrada.iterrows()
    ]
    idx_escolhido = st.selectbox(
        "🔍 Escolha uma transação para analisar",
        options=range(len(opcoes_select)),
        format_func=lambda i: opcoes_select[i],
    )

    linha = fila_filtrada.iloc[idx_escolhido]
    transacao = linha.to_dict()
    decisao = transacao["decisao"]
    decisao_legivel = _DECISAO_LEGIVEL.get(decisao, decisao)
    nota = float(transacao["nota"])

    st.markdown("<br>", unsafe_allow_html=True)

    # Painel de detalhe — duas colunas
    col_esq, col_dir = st.columns([1, 1], gap="large")

    with col_esq:
        # Cabeçalho do detalhe
        st.markdown(f"""
        <div class="detail-section">
            <h4>Transação #{int(transacao["id_transacao"])}</h4>
            <table style="width:100%;font-size:0.88rem;border-collapse:collapse">
                <tr><td style="color:#6b7280;padding:3px 0;width:44%">Data/hora</td>
                    <td style="font-weight:500">{transacao.get("data_hora","—")}</td></tr>
                <tr><td style="color:#6b7280;padding:3px 0">Valor</td>
                    <td style="font-weight:500">R$ {float(transacao.get("valor",0)):.2f}</td></tr>
                <tr><td style="color:#6b7280;padding:3px 0">Tipo</td>
                    <td style="font-weight:500">{transacao.get("tipo_transacao","—")}</td></tr>
                <tr><td style="color:#6b7280;padding:3px 0">Modalidade</td>
                    <td style="font-weight:500">{transacao.get("modalidade_transacao","—")}</td></tr>
                <tr><td style="color:#6b7280;padding:3px 0">Decisão</td>
                    <td>{_badge_html(decisao)}</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

        # Nota de risco
        st.markdown(f"""
        <div class="detail-section">
            <h4>Nota de risco</h4>
            {_nota_html(nota)}
        </div>
        """, unsafe_allow_html=True)

        # Feedback
        st.markdown('<div class="detail-section"><h4>Resposta do analista</h4></div>', unsafe_allow_html=True)
        fb_c1, fb_c2 = st.columns(2)
        if fb_c1.button("🚨 Confirmar fraude", use_container_width=True, type="primary"):
            _gravar_feedback(transacao["id_transacao"], nota, decisao, "fraude")
            st.toast("✅ Resposta registrada como fraude")
        if fb_c2.button("✅ Marcar como legítima", use_container_width=True):
            _gravar_feedback(transacao["id_transacao"], nota, decisao, "legitima")
            st.toast("✅ Resposta registrada como legítima")

    with col_dir:
        # Sinais de alerta
        sinais = calcular_sinais(transacao)
        icones = {
            "velocidade_terminal": "⚡",
            "rajada_1min": "🔁",
            "token_carteira": "📱",
            "salto_geografico": "📍",
            "madrugada": "🌙",
            "valor_alto": "💰",
            "credito_nao_presente": "🌐",
            "ip_desconhecido": "🚩",
            "estabelecimento_risco": "🏪",
        }
        if sinais:
            linhas_sinais = "".join(
                f'<div class="sinal-row"><span class="sinal-icon">{icones.get(s["id"],"⚠️")}</span>'
                f'<span>{s["descricao"]}</span></div>'
                for s in sinais
            )
        else:
            linhas_sinais = '<div class="sinal-row"><span class="sinal-icon">✅</span><span>Nenhum sinal de alerta.</span></div>'

        st.markdown(f"""
        <div class="detail-section">
            <h4>Sinais de alerta ({len(sinais)})</h4>
            {linhas_sinais}
        </div>
        """, unsafe_allow_html=True)

        # Explicação
        with st.spinner("Gerando explicação..."):
            resultado = agente.analisar(transacao, usar_llm=usar_llm)

        fonte = resultado["fonte_explicacao"]
        fonte_label = "IBM Granite 4" if fonte == "granite" else "regras"
        fonte_cor = "#1d4ed8" if fonte == "granite" else "#6b7280"

        st.markdown(f"""
        <div class="detail-section">
            <h4>Explicação do agente</h4>
            <p style="font-size:0.9rem;color:#374151;line-height:1.6;margin:0 0 0.6rem 0">
                {resultado["explicacao"]}
            </p>
            <span style="font-size:0.75rem;color:{fonte_cor};font-weight:600">
                Gerado por: {fonte_label}
            </span>
        </div>
        """, unsafe_allow_html=True)

        # Histórico do cartão
        id_cartao = transacao.get("id_cartao")
        data_hora_tx = transacao.get("data_hora")
        historico = agente.historico_cartao(id_cartao, antes_de=data_hora_tx)

        st.markdown('<div style="font-size:0.78rem;font-weight:600;text-transform:uppercase;letter-spacing:0.06em;color:#6b7280;margin-bottom:0.4rem">Histórico do cartão</div>', unsafe_allow_html=True)
        if historico.empty:
            st.caption("Nenhum histórico disponível para este cartão.")
        else:
            cols_hist = [c for c in COLUNAS_TABELA if c in historico.columns]
            st.dataframe(
                historico[cols_hist],
                use_container_width=True,
                hide_index=True,
                height=200,
                column_config={
                    "data_hora": st.column_config.DatetimeColumn("Data/hora", format="DD/MM HH:mm"),
                    "valor": st.column_config.NumberColumn("Valor (R$)", format="R$ %.2f"),
                    "nota": st.column_config.ProgressColumn("Nota", min_value=0, max_value=100, format="%.1f"),
                },
            )

# ---------------------------------------------------------------------------
# Página: Desempenho
# ---------------------------------------------------------------------------

elif pagina == "Desempenho":

    st.markdown('<p class="sent-page-title">Desempenho do modelo</p>', unsafe_allow_html=True)
    st.markdown('<p class="sent-page-subtitle">Avaliação no conjunto de teste — março de 2025</p>', unsafe_allow_html=True)

    with open(CAMINHO_METRICAS, encoding="utf-8") as f:
        metricas = json.load(f)
    with open(CAMINHO_AVALIACAO, encoding="utf-8") as f:
        avaliacao = json.load(f)

    # KPIs do modelo
    c1, c2, c3 = st.columns(3)
    c1.markdown(_kpi_card("PR-AUC", f"{metricas['pr_auc']:.4f}", "ok"), unsafe_allow_html=True)
    c2.markdown(_kpi_card("ROC-AUC", f"{metricas['roc_auc']:.4f}", "ok"), unsafe_allow_html=True)
    c3.markdown(_kpi_card("Fraudes no teste", metricas["teste"]["fraudes"], "block"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Comparação Sentinela × Sistema atual
    st.markdown("### Sentinela × Sistema atual — março/2025")

    ft = avaliacao["fraudes_total"]
    s = avaliacao["sentinela"]
    sa = avaliacao["sistema_atual"]
    pct_sent  = s["fraudes_bloqueadas"]  / ft * 100 if ft > 0 else 0
    pct_atual = sa["fraudes_bloqueadas"] / ft * 100 if ft > 0 else 0
    nao_bloq_sent = ft - s["fraudes_bloqueadas"]

    tabela_comp = pd.DataFrame({
        "Sistema": ["Sistema atual", "Sentinela"],
        "Fraudes bloqueadas": [sa["fraudes_bloqueadas"], s["fraudes_bloqueadas"]],
        "Fraudes não bloqueadas": [sa["fraudes_nao_bloqueadas"], nao_bloq_sent],
        "% fraudes bloqueadas": [f"{pct_atual:.1f}%", f"{pct_sent:.1f}%"],
    })
    st.dataframe(
        tabela_comp,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Sistema": st.column_config.TextColumn("Sistema", width="medium"),
            "Fraudes bloqueadas": st.column_config.NumberColumn("Fraudes bloqueadas", format="%d"),
            "Fraudes não bloqueadas": st.column_config.NumberColumn("Fraudes não bloqueadas", format="%d"),
            "% fraudes bloqueadas": st.column_config.TextColumn("% bloqueadas"),
        },
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**Fraudes bloqueadas — comparação visual**")
    df_grafico = pd.DataFrame(
        {"Fraudes bloqueadas": [sa["fraudes_bloqueadas"], s["fraudes_bloqueadas"]]},
        index=["Sistema atual", "Sentinela"],
    )
    st.bar_chart(df_grafico, color="#dc2626")

    st.markdown("<br>", unsafe_allow_html=True)

    # Limiares
    st.markdown("### Desempenho por limiar de corte")
    df_limiares = pd.DataFrame(metricas["limiares"])
    df_limiares.columns = ["Limiar", "Alertas", "Fraudes detectadas", "Precisão", "Recall"]
    st.dataframe(
        df_limiares,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Limiar": st.column_config.NumberColumn("Limiar", format="%d"),
            "Alertas": st.column_config.NumberColumn("Alertas", format="%d"),
            "Fraudes detectadas": st.column_config.NumberColumn("Fraudes detectadas", format="%d"),
            "Precisão": st.column_config.ProgressColumn("Precisão", min_value=0.0, max_value=1.0, format="%.4f"),
            "Recall": st.column_config.ProgressColumn("Recall", min_value=0.0, max_value=1.0, format="%.4f"),
        },
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.info(
        "⚠️ **Dados sintéticos:** o resultado é otimista. "
        "Em produção o modelo precisa de monitoramento e retreino."
    )
