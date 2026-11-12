# 08 — Design da interface

A interface é uma mesa de trabalho para o analista: uma fila ordenada pelo risco à esquerda e
o painel da transação escolhida à direita, com decisão, motivos e os dois botões de resposta
sempre visíveis. Duas páginas de apoio mostram o desempenho e como o agente decide.

Toda decisão abaixo é rastreável a uma condição de uso (seção 1), a uma história
([02-user-stories.md](02-user-stories.md)) ou a uma regra do Manual da IDE (capítulo 2.3).

---

## 1. Usuário, objetivo e contexto de uso

| Condição real de uso | Decisão de design |
| --- | --- |
| Analista sentado, em estação de trabalho com tela grande, por horas | Layout largo (`layout="wide"`), fila e painel lado a lado, sem trocar de tela |
| Revisa dezenas de alertas por turno, com pressa | Fila já ordenada pela nota; filtro padrão mostra só o que exige ação; primeira linha já aberta |
| Precisa entender o motivo em segundos | Decisão em faixa com cor, ícone e texto; sinais em frases curtas; explicação em 3 frases |
| Decisão errada custa caro (fraude aprovada ou cliente bloqueado) | Botões de resposta com o mesmo peso visual, para não induzir a resposta (viés de automação) |
| Usa teclado para ganhar tempo | Alternativa de escolha por ID numa caixa de seleção acessível por teclado |
| Avaliador assiste a um vídeo de 3 minutos | Fluxo principal cabe numa tela; página de desempenho com a comparação em destaque |
| O Granite pode não estar instalado ou demorar | Estado da conexão sempre visível na barra lateral; explicação de reserva sem mensagem técnica |

Contexto dominante: desktop, 1280 px de largura ou mais. Em telas estreitas, as colunas se
empilham (seção 16).

## 2. Referências e antipadrões

Referências observadas: filas de revisão manual de plataformas de pagamento (por exemplo, a
fila de revisão do Stripe Radar) e consoles de análise de fraude. O que funciona nelas e foi
aproveitado:

- **Lista e detalhe na mesma tela:** o analista não perde a posição na fila.
- **Nota acompanhada dos motivos:** uma nota sozinha não sustenta a decisão do analista.
- **Veredito com dois botões explícitos:** a resposta vira dado para o modelo.

Antipadrões descartados de propósito:

- **Painel cheio de gráficos na tela principal:** distrai da tarefa de revisar; os números ficam
  na página "Desempenho".
- **Status só por cor:** falha para daltônicos e em telas com reflexo.
- **Abrir cada transação numa janela modal:** esconde a fila e obriga a fechar e reabrir.
- **Avançar sozinho para a próxima transação depois da resposta:** o analista perde o contexto
  da resposta que acabou de dar.

## 3. Navegação

Três páginas com `st.navigation` e `st.Page`, na barra lateral:

| Ordem | Título | Ícone (`src/interface/tema.py`) | Função | `url_path` | Padrão |
| --- | --- | --- | --- | --- | --- |
| 1 | Fila de alertas | `:material/list_alt:` | `pagina_fila.renderizar` | `fila` | sim |
| 2 | Desempenho | `:material/monitoring:` | `pagina_desempenho.renderizar` | `desempenho` | não |
| 3 | Como funciona | `:material/help:` | `pagina_como_funciona.renderizar` | `como-funciona` | não |

O `url_path` é obrigatório: as três funções se chamam `renderizar`, e sem ele o Streamlit 1.67
recusa a navegação com o erro "Two pages resolve to the URL pathname `/renderizar`".

A barra lateral, abaixo do menu, tem nesta ordem: o interruptor "Explicar com IBM Granite", o
estado do Granite e o rodapé sobre os dados.

## 4. Wireframes (baixa fidelidade)

### 4.1 Fila de alertas

```text
┌ Barra lateral ──────────────┐┌ Fila de alertas (h1) ─────────────────────────────────────────────┐
│ ▸ Fila de alertas           ││ Transações de março de 2025, da mais arriscada para a menos…      │
│   Desempenho                ││ ┌Na fila┐ ┌Bloquear┐ ┌Pedir confirmação┐ ┌Aprovar┐                 │
│   Como funciona             ││ │ 2.054 │ │   54   │ │       23        │ │ 1.977 │                 │
│                             ││ └───────┘ └────────┘ └─────────────────┘ └───────┘                 │
│ [■] Explicar com IBM Granite││ ┌ coluna esquerda (3/5) ──────────────┐┌ painel (2/5, borda) ─────┐│
│ ✔ IBM Granite: conectado    ││ │ Mostrar decisões                     ││ Transação 123456 (h2)    ││
│                             ││ │ (⛔ Bloquear) (⚠️ Pedir conf.) (✅…)  ││ 15/03/2025 03:12 · Créd… ││
│                             ││ │ Mostrando 77 de 2.054 transações.    ││ ⛔ Bloquear e enviar…    ││
│                             ││ │ ┌──────────────────────────────────┐ ││ ▓▓▓▓▓▓▓▓▓▓ Nota 97,3/100 ││
│                             ││ │ │ID │Nota▓▓│Decisão │Valor│Data│… │ ││ Sinais de alerta (8)     ││
│                             ││ │ │…  │      │⛔ Bloq. │     │    │  │ ││ • Cartão usado 45 vezes… ││
│                             ││ │ │   (15 linhas visíveis, rolagem) │ ││ Explicação do agente     ││
│                             ││ │ └──────────────────────────────────┘ ││ "A compra foi bloqueada…"││
│                             ││ │ Ou escolha pelo ID da transação [▼] ││ Gerada por: IBM Granite 4││
│ Dados 100% sintéticos…      ││ └──────────────────────────────────────┘│ Sua avaliação            ││
└─────────────────────────────┘│                                         │ [Confirmar fraude][Marcar││
                               │                                         │  como legítima]          ││
                               │                                         │ Ainda sem resposta…      ││
                               │                                         │ ▸ Histórico do cartão    ││
                               │                                         └──────────────────────────┘│
                               └────────────────────────────────────────────────────────────────────┘
```

### 4.2 Desempenho

```text
┌ Desempenho em março de 2025 (h1) ─────────────────────────────────────────────────────────────┐
│ Comparação entre o Sentinela e o sistema atual da Sicredi nas 13.608 transações de teste.      │
│ [Fraudes em março 54] [Bloqueadas pelo Sentinela 54 de 54 ↑+28] [Bloqueadas pelo sistema atual  │
│  26 de 54] [Compras legítimas bloqueadas 0] [Pedidos de confirmação 159]                       │
│ Fraudes de março bloqueadas (h2)                                                               │
│   Sistema atual ▓▓▓▓▓▓▓▓▓▓▓▓ 26                                                                │
│   Sentinela     ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 54                                                   │
│ Comparação (h2)  tabela: Indicador | Sistema atual | Sentinela                                 │
│ ▸ Detalhes do modelo (regressão logística)                                                     │
│ ℹ Dados sintéticos: o resultado é otimista…                                                    │
└────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 4.3 Como funciona

```text
┌ Como o Sentinela decide (h1) ──────────────────────────────────────┐
│ Lead: a IA explica; quem decide são regras e um modelo auditáveis.  │
│ Os passos do agente (h2): lista numerada de 5 passos                │
│ Os 9 sinais de alerta (h2): tabela Sinal | Dispara quando           │
│ Como a decisão é tomada (h2): 3 itens                               │
│ Sobre os dados (h2): 2 frases com números calculados na hora        │
│ Limitações (h2): 4 itens                                            │
└─────────────────────────────────────────────────────────────────────┘
```

## 5. Tokens

### 5.1 Tema (`.streamlit/config.toml`)

| Token | Valor | Uso | Contraste medido |
| --- | --- | --- | --- |
| `primaryColor` | `#0F62FE` | Interruptor, foco, botão primário | Branco sobre ele: 5,0:1; ele sobre branco: 5,0:1 |
| `backgroundColor` | `#FFFFFF` | Fundo das páginas | — |
| `secondaryBackgroundColor` | `#F2F4F8` | Barra lateral e campos | Texto `#161616` sobre ele: 16,4:1 |
| `textColor` | `#161616` | Texto | Sobre o fundo: 18,1:1 |
| `font` | `sans-serif` | Toda a interface | Corpo de 16 px (padrão do Streamlit) |

As cores das faixas de decisão são as de `st.error`, `st.warning` e `st.success`, do próprio
Streamlit. Nenhum código hexadecimal aparece no código Python.

### 5.2 Decisões (`src/interface/tema.py`)

```python
@dataclass(frozen=True)
class EstiloDecisao:
    rotulo_curto: str   # usado na fila e no filtro
    emoji: str          # forma distinta para não depender de cor
    icone: str          # ícone Material da faixa de decisão
    tipo_alerta: str    # "error", "warning" ou "success"

DECISOES = {
    "BLOQUEAR": EstiloDecisao("Bloquear", "⛔", ":material/block:", "error"),
    "PEDIR_CONFIRMACAO": EstiloDecisao("Pedir confirmação", "⚠️", ":material/phone_in_talk:", "warning"),
    "APROVAR": EstiloDecisao("Aprovar", "✅", ":material/check_circle:", "success"),
}
ORDEM_DECISOES = ["BLOQUEAR", "PEDIR_CONFIRMACAO", "APROVAR"]
```

O rótulo longo ("Bloquear e enviar ao analista") vem de `ROTULOS_DECISAO` em `src/config.py`,
o mesmo que o agente usa. Nunca repita esses textos na interface.

Outros tokens em `tema.py`: `ICONE_FILA`, `ICONE_DESEMPENHO`, `ICONE_COMO_FUNCIONA`,
`ICONE_FRAUDE = ":material/gpp_bad:"`, `ICONE_LEGITIMA = ":material/verified_user:"`,
`ICONE_ERRO = ":material/error:"`, `ICONE_GRANITE_ON = ":material/check_circle:"`,
`ICONE_GRANITE_OFF = ":material/cloud_off:"`, `PROPORCAO_COLUNAS = (3, 2)`,
`ALTURA_TABELA_PX = 560`, `LINHAS_HISTORICO = 10`.

## 6. Componentes e padrões

| Elemento | Componente Streamlit | Regra |
| --- | --- | --- |
| Título da página | `st.title` (h1) | Um por página |
| Seção | `st.header` (h2) | Nunca simule título com texto grande ou negrito |
| Rótulo dentro do painel | `st.markdown("**…**")` | |
| Indicador | `st.metric` com `help=` | Valores formatados em pt-BR |
| Filtro de decisões | `st.pills(selection_mode="multi")` | Rótulo visível |
| Tabela | `st.dataframe` com `column_config`, `hide_index=True` | Largura total da coluna |
| Faixa de decisão | `st.error` / `st.warning` / `st.success` com `icon=` | Texto em negrito com o rótulo longo |
| Nota | `st.progress(nota / 100, text=…)` | |
| Botão | `st.button` com `icon=` e largura total da coluna | Parâmetro `width="stretch"`, ou `use_container_width=True` se a versão instalada não aceitar `width` |
| Aviso efêmero | `st.toast` | Só para sucesso de ação |
| Erro | `st.error` com `ICONE_ERRO` | Texto de `textos.py`; nunca `st.exception` |
| Informação | `st.info` | |
| Carregamento | `show_spinner=` do cache, ou `st.spinner` | Texto de `textos.py` |
| Bloco recolhível | `st.expander` | |

Textos que contêm "R$" ou vêm do Granite passam por `escapar_markdown` antes de
`st.markdown`, `st.caption` ou `st.toast`: no Streamlit, dois "$" na mesma linha viram fórmula
matemática.

## 7. Página "Fila de alertas" (`src/interface/pagina_fila.py`)

### 7.1 Ordem dos elementos

1. `st.title(textos.TITULO_FILA)` e `st.caption(textos.LEGENDA_FILA)`.
2. `fila = dados.carregar_fila()` (o cache mostra `textos.CARREGANDO_FILA` só na primeira vez).
3. Quatro `st.metric` em `st.columns(4)`: "Na fila", "Bloquear", "Pedir confirmação",
   "Aprovar", com contagens de `dados.contar_por_decisao(fila)` sobre a fila inteira (o filtro não
   muda os indicadores). `help=textos.AJUDA_NA_FILA` no primeiro.
4. `esquerda, direita = st.columns(tema.PROPORCAO_COLUNAS, gap="large")`.
5. Na coluna esquerda: filtro, contagem, tabela e caixa de ID (7.2 a 7.4).
6. Na coluna direita: `st.container(border=True)` com o painel (7.5).

### 7.2 Filtro

`st.pills(textos.FILTRO_DECISOES, options=tema.ORDEM_DECISOES, selection_mode="multi",
default=["BLOQUEAR", "PEDIR_CONFIRMACAO"], format_func=<emoji + " " + rotulo_curto>,
key="filtro_decisoes")`.
Depois: `visiveis = fila[fila["decisao"].isin(filtro)].reset_index(drop=True)`.
Se `visiveis` estiver vazio: `st.info(textos.VAZIO_FILTRO)` e a função retorna (sem tabela e
sem painel). Senão: `st.caption(textos.CONTAGEM_TABELA.format(mostradas=…, total=…))`, com
números formatados por `formatar_inteiro`.

### 7.3 Tabela

DataFrame de exibição montado a partir de `visiveis`, nesta ordem de colunas:

| Coluna | Origem | `column_config` |
| --- | --- | --- |
| ID | `id_transacao` | `NumberColumn(format="%d")` |
| Nota | `nota` | `ProgressColumn(min_value=0, max_value=100, format="%.1f")` |
| Decisão | `decisao` → emoji + rótulo curto | `TextColumn` |
| Valor (R$) | `valor` | `NumberColumn(format="%.2f")` |
| Data e hora | `data_hora` | `DatetimeColumn(format="DD/MM/YYYY HH:mm")` |
| Tipo | `tipo_transacao` → `formatar_tipo` | `TextColumn` |
| Modalidade | `modalidade_transacao` → `formatar_modalidade` | `TextColumn` |
| Sinais | `n_sinais` | `NumberColumn(format="%d", help=textos.AJUDA_COLUNA_SINAIS)` |

`st.dataframe(tabela, key="tabela_fila", on_select="rerun", selection_mode="single-row",
hide_index=True, height=tema.ALTURA_TABELA_PX, column_config=…)` ocupando a largura da coluna.
Valores numéricos ficam numéricos na tabela para a ordenação por clique no cabeçalho funcionar
(o ponto decimal em "Valor (R$)" é limitação conhecida do componente).

### 7.4 Escolha da transação (uma única fonte da verdade)

A transação aberta é sempre `st.session_state["id_selecionado"]`. Algoritmo, nesta ordem:

```python
ids_visiveis = visiveis["id_transacao"].tolist()
if st.session_state.get("id_selecionado") not in ids_visiveis:
    st.session_state["id_selecionado"] = ids_visiveis[0]          # US006, cenário 3

evento = st.dataframe(...)                                         # 7.3
linhas = evento.selection.rows
selecao_tabela = ids_visiveis[linhas[0]] if linhas else None
if selecao_tabela is not None and selecao_tabela != st.session_state.get("ultima_selecao_tabela"):
    st.session_state["id_selecionado"] = selecao_tabela            # US006, cenário 1
st.session_state["ultima_selecao_tabela"] = selecao_tabela

st.session_state["busca_id"] = st.session_state["id_selecionado"]  # antes de criar o widget
st.selectbox(textos.BUSCA_ID, options=ids_visiveis, key="busca_id",
             format_func=<"ID · nota · rótulo curto">, on_change=_ao_escolher_id)
# _ao_escolher_id(): st.session_state["id_selecionado"] = st.session_state["busca_id"]  (cenário 2)
```

Não passe `index=` ao `selectbox`: o valor vem do `session_state`.

### 7.5 Painel da transação

`linha = visiveis[visiveis["id_transacao"] == id_selecionado].iloc[0]`;
`transacao = linha.to_dict()`. Elementos, nesta ordem:

1. `st.header(textos.TITULO_PAINEL.format(id=…))` e
   `st.caption(escapar_markdown(textos.RESUMO_PAINEL.format(data_hora=…, tipo=…, modalidade=…, valor=…)))`.
2. **Análise com cache.** `usar_llm = st.session_state["usar_granite"]`;
   `chave = (id_selecionado, usar_llm)`; `analises = st.session_state.setdefault("analises", {})`.
   Se `chave` não estiver em `analises`: `with st.spinner(textos.GERANDO_EXPLICACAO if usar_llm
   else textos.MONTANDO_EXPLICACAO): analises[chave] = agente.analisar(transacao, usar_llm=usar_llm)`.
   `agente = dados.carregar_agente()`.
3. Faixa de decisão: `getattr(st, estilo.tipo_alerta)(f"**{ROTULOS_DECISAO[decisao]}**",
   icon=estilo.icone)`.
4. `st.progress(nota / 100, text=textos.NOTA_TEXTO.format(nota=formatar_nota(nota)))`.
5. `st.markdown(f"**{textos.TITULO_SINAIS.format(quantidade=n)}**")` e uma linha
   `- descrição` por sinal, num único `st.markdown`, com `escapar_markdown`; sem sinais:
   `textos.SEM_SINAIS`.
6. `st.markdown(f"**{textos.TITULO_EXPLICACAO}**")`, `st.markdown(escapar_markdown(explicacao))`
   e `st.caption` com a fonte: `"granite"` → `FONTE_GRANITE`; `"regras"` com `usar_llm` ligado →
   `FONTE_REGRAS_INDISPONIVEL`; `"regras"` com `usar_llm` desligado → `FONTE_REGRAS`.
7. `st.markdown(f"**{textos.TITULO_RESPOSTA}**")`, dois botões em `st.columns(2)`:
   `BOTAO_FRAUDE` (`ICONE_FRAUDE`, `key=f"fraude_{id}"`) e `BOTAO_LEGITIMA` (`ICONE_LEGITIMA`,
   `key=f"legitima_{id}"`), ambos do tipo padrão (nenhum `type="primary"`; seção 1).
   Clique: `feedback.registrar_resposta(CAMINHO_FEEDBACK, RespostaAnalista(...))` dentro de
   `try`; sucesso → `st.toast(TOAST_FRAUDE ou TOAST_LEGITIMA, icon=…)`; `OSError` → log e
   `st.error(textos.ERRO_GRAVAR, icon=ICONE_ERRO)`.
   Depois dos botões: `feedback.ler_ultima_resposta(CAMINHO_FEEDBACK, id)` dentro de `try`;
   resposta → `st.caption(textos.RESPOSTA_ATUAL.format(resposta=rotulo_resposta(…),
   data_hora=formatar_data_hora(…)))`; `None` → `st.caption(textos.SEM_RESPOSTA)`;
   `ValueError` → `st.warning(textos.ERRO_LER_RESPOSTAS)`.
8. Histórico: se `id_cartao` vazio → `st.caption(textos.HISTORICO_SEM_CARTAO)`. Senão,
   `hist = agente.historico_cartao(id_cartao, antes_de=data_hora ou None, n=tema.LINHAS_HISTORICO)`
   e `st.expander(textos.TITULO_HISTORICO.format(n=len(hist)))` com uma tabela de colunas
   "Data e hora", "Valor", "Tipo", "Modalidade", "Distância do terminal anterior (km)", com
   valores já formatados em pt-BR; vazio → `textos.HISTORICO_VAZIO` dentro do expander.

## 8. Página "Desempenho" (`src/interface/pagina_desempenho.py`)

1. `metricas = dados.carregar_json(CAMINHO_METRICAS)` e
   `avaliacao = dados.carregar_json(CAMINHO_AVALIACAO)`. Algum `None` →
   `st.error(textos.ERRO_SEM_METRICAS, icon=ICONE_ERRO)` e retorna.
2. `st.title(textos.TITULO_DESEMPENHO)` e `st.caption(textos.LEGENDA_DESEMPENHO.format(transacoes=…))`.
3. Cinco `st.metric` em `st.columns(5)`:
   - "Fraudes em março": `fraudes_total`.
   - "Bloqueadas pelo Sentinela": `"{s} de {total}"`, `delta=textos.DELTA_SENTINELA.format(diferenca=s - a)`.
   - "Bloqueadas pelo sistema atual": `"{a} de {total}"`.
   - "Compras legítimas bloqueadas": `sentinela.bloqueadas - sentinela.fraudes_bloqueadas`,
     `help=textos.AJUDA_LEGITIMAS_BLOQUEADAS`.
   - "Pedidos de confirmação": `sentinela.confirmacoes`,
     `help=textos.AJUDA_CONFIRMACOES.format(percentual=…)` (sobre `transacoes`).
4. `st.header(textos.TITULO_GRAFICO)` e `st.bar_chart` horizontal com duas barras ("Sistema
   atual" e "Sentinela") e o eixo "Fraudes bloqueadas".
5. `st.header(textos.TITULO_COMPARACAO)` e `st.table` com as colunas "Indicador", "Sistema atual",
   "Sentinela" e as linhas: "Fraudes bloqueadas" ("26 de 54"), "Fraudes não bloqueadas",
   "Percentual das fraudes bloqueadas", "Compras legítimas bloqueadas".
6. `st.expander(textos.TITULO_DETALHES_MODELO)` com dois `st.metric` (PR-AUC e ROC-AUC, 3 casas
   decimais em pt-BR) e `st.table` dos limiares: "Nota de corte", "Alertas", "Fraudes
   detectadas", "Precisão", "Recall" (percentuais pt-BR).
7. `st.info(textos.AVISO_SINTETICO)`.

## 9. Página "Como funciona" (`src/interface/pagina_como_funciona.py`)

1. `st.title(textos.TITULO_COMO)` e `st.markdown(textos.LEAD_COMO)`.
2. `st.header(textos.TITULO_PASSOS)` e lista numerada com `textos.PASSOS`.
3. `st.header(textos.TITULO_SINAIS_COMO)` e `st.table` com colunas "Sinal" e "Dispara quando",
   montada de `textos.SINAIS_EXPLICADOS`, formatando as chaves com as constantes de
   `src/config.py` (`LIMIAR_*`, `HORA_FIM_MADRUGADA`).
4. `st.header(textos.TITULO_DECISAO)` e os três itens de `textos.REGRAS_DECISAO`, formatados com
   `NOTA_BLOQUEAR`, `NOTA_CONFIRMAR` e `MIN_SINAIS_CONFIRMAR`.
5. `st.header(textos.TITULO_DADOS)` e `textos.SOBRE_DADOS` formatado com o total de linhas e de
   fraudes de `dados.carregar_base()` e `TAMANHO_AMOSTRA_LEGITIMAS`.
6. `st.header(textos.TITULO_LIMITACOES)` e a lista `textos.LIMITACOES`.

## 10. Estados

| Estado | Onde | Quando | Como aparece |
| --- | --- | --- | --- |
| Carregando a fila | Fila | Primeira montagem da fila na sessão | `show_spinner=textos.CARREGANDO_FILA` em `carregar_fila` |
| Gerando explicação | Painel | Transação sem análise em cache | `st.spinner(GERANDO_EXPLICACAO)` ou `MONTANDO_EXPLICACAO` |
| Vazio: filtro | Fila | Nenhuma decisão marcada | `st.info(VAZIO_FILTRO)`, sem tabela e sem painel |
| Vazio: sinais | Painel | Transação sem sinais | `SEM_SINAIS` |
| Vazio: histórico | Painel | Cartão sem transações anteriores | `HISTORICO_VAZIO` |
| Vazio: resposta | Painel | Transação nunca respondida | `SEM_RESPOSTA` |
| Indisponível: histórico | Painel | Transação sem `id_cartao` | `HISTORICO_SEM_CARTAO` |
| Indisponível: Granite | Barra lateral e painel | Ollama não responde | `STATUS_GRANITE_OFF` e `FONTE_REGRAS_INDISPONIVEL` |
| Erro: dados ou modelo | Todas | Arquivo ausente ao abrir | `st.error` com `ERRO_SEM_DADOS` ou `ERRO_SEM_MODELO`, depois `st.stop()` |
| Erro: métricas | Desempenho | JSON ausente | `st.error(ERRO_SEM_METRICAS)` |
| Erro: gravar resposta | Painel | `OSError` ao gravar | `st.error(ERRO_GRAVAR)` |
| Erro: ler respostas | Painel | `feedback.csv` com cabeçalho inválido | `st.warning(ERRO_LER_RESPOSTAS)` |
| Sucesso: resposta | Painel | Gravação concluída | `st.toast(TOAST_FRAUDE ou TOAST_LEGITIMA)` e `RESPOSTA_ATUAL` |
| Permissão | — | Não se aplica: uso local de uma pessoa, sem login (RF015 é Won't) | — |

## 11. Textos (`src/interface/textos.py`)

Todos os textos da tela, com estes nomes e valores exatos. Formate com `str.format`.

```python
# Aplicação e barra lateral
TITULO_APP = "Sentinela"
ROTULO_TOGGLE_GRANITE = "Explicar com IBM Granite"
AJUDA_TOGGLE_GRANITE = ("Usa o modelo IBM Granite 4 rodando no seu computador pelo Ollama. "
                        "Desligado, a explicação é montada a partir dos sinais de alerta.")
STATUS_GRANITE_ON = "IBM Granite: conectado"
STATUS_GRANITE_OFF = "IBM Granite: indisponível. As explicações serão montadas a partir dos sinais."
STATUS_GRANITE_DESLIGADO = "IBM Granite: desligado nesta sessão."
RODAPE_DADOS = ("Sentinela · agente antifraude do Desafio Sicredi. Dados 100% sintéticos "
                "fornecidos pela Sicredi. Protótipo do IBM SkillsBuild AI Lab.")

# Erros de inicialização
ERRO_SEM_DADOS = ("Dados preparados não encontrados. Coloque o arquivo da Sicredi em data/ "
                  "e rode no terminal: python -m src.preparar_dados")
ERRO_SEM_MODELO = "Modelo não encontrado. Rode no terminal: python -m src.treinar_modelo"
ERRO_SEM_METRICAS = ("Métricas não encontradas. Rode no terminal: python -m src.treinar_modelo "
                     "e depois python -m src.avaliar_agente")

# Página Fila de alertas
TITULO_FILA = "Fila de alertas"
LEGENDA_FILA = ("Transações de março de 2025, da mais arriscada para a menos arriscada. "
                "Clique numa linha para analisar.")
CARREGANDO_FILA = "Carregando e analisando as transações de março…"
METRICA_NA_FILA = "Na fila"
AJUDA_NA_FILA = "Todas as fraudes de março mais 2.000 compras legítimas sorteadas, para demonstração."
FILTRO_DECISOES = "Mostrar decisões"
CONTAGEM_TABELA = "Mostrando {mostradas} de {total} transações."
VAZIO_FILTRO = ("Nenhuma transação com os filtros escolhidos. "
                "Marque ao menos uma decisão em “Mostrar decisões”.")
AJUDA_COLUNA_SINAIS = "Quantidade de sinais de alerta disparados."
BUSCA_ID = "Ou escolha pelo ID da transação"

# Painel da transação
TITULO_PAINEL = "Transação {id}"
RESUMO_PAINEL = "{data_hora} · {tipo} · {modalidade} · {valor}"
NOTA_TEXTO = "Nota de risco: {nota} de 100"
TITULO_SINAIS = "Sinais de alerta ({quantidade})"
SEM_SINAIS = "Nenhum sinal de alerta: a transação segue o padrão das compras legítimas."
TITULO_EXPLICACAO = "Explicação do agente"
GERANDO_EXPLICACAO = "O IBM Granite está escrevendo a explicação… A primeira pode levar até 1 minuto."
MONTANDO_EXPLICACAO = "Montando a explicação…"
FONTE_GRANITE = "Explicação gerada por: IBM Granite 4"
FONTE_REGRAS = "Explicação gerada por: regras"
FONTE_REGRAS_INDISPONIVEL = "Explicação gerada por: regras (IBM Granite indisponível no momento)"
TITULO_RESPOSTA = "Sua avaliação"
BOTAO_FRAUDE = "Confirmar fraude"
BOTAO_LEGITIMA = "Marcar como legítima"
TOAST_FRAUDE = "Resposta registrada: fraude confirmada."
TOAST_LEGITIMA = "Resposta registrada: transação legítima."
RESPOSTA_ATUAL = "Sua resposta: {resposta} em {data_hora}. Você pode mudar; vale a última."
SEM_RESPOSTA = "Ainda sem resposta para esta transação."
ROTULOS_RESPOSTA = {"fraude": "Fraude confirmada", "legitima": "Transação legítima"}
ERRO_GRAVAR = ("Não foi possível salvar a resposta em data/feedback.csv. Feche o arquivo se ele "
               "estiver aberto em outro programa e tente de novo.")
ERRO_LER_RESPOSTAS = ("O arquivo data/feedback.csv está com formato inválido. Renomeie ou apague "
                      "o arquivo e registre as respostas de novo.")
TITULO_HISTORICO = "Histórico do cartão (últimas {n} transações antes desta)"
HISTORICO_VAZIO = "Nenhuma transação anterior deste cartão na base."
HISTORICO_SEM_CARTAO = "Esta transação não tem identificação de cartão; o histórico não está disponível."
ROTULOS_TIPO = {"credito": "Crédito", "debito": "Débito"}
ROTULOS_MODALIDADE = {"cartao_presente": "Presente", "cartao_nao_presente": "Não presente"}

# Página Desempenho
TITULO_DESEMPENHO = "Desempenho em março de 2025"
LEGENDA_DESEMPENHO = ("Comparação entre o Sentinela e o sistema atual da Sicredi nas "
                      "{transacoes} transações de teste.")
DELTA_SENTINELA = "{diferenca:+d} em relação ao sistema atual"
AJUDA_LEGITIMAS_BLOQUEADAS = "Compras legítimas que o Sentinela bloqueou por engano."
AJUDA_CONFIRMACOES = "{percentual} das transações de março."
TITULO_GRAFICO = "Fraudes de março bloqueadas"
TITULO_COMPARACAO = "Comparação"
TITULO_DETALHES_MODELO = "Detalhes do modelo (regressão logística)"
AVISO_SINTETICO = ("Dados sintéticos: o resultado é otimista. Em produção, o modelo precisaria "
                   "de monitoramento e retreino com as respostas dos analistas.")

# Página Como funciona
TITULO_COMO = "Como o Sentinela decide"
LEAD_COMO = ("Para cada compra, o agente usa suas ferramentas e um analista humano dá a palavra "
             "final. A IA explica; quem decide são regras e um modelo auditáveis.")
TITULO_PASSOS = "Os passos do agente"
PASSOS = [
    "Calcula 9 sinais de alerta com regras simples, como rajadas de uso e saltos geográficos.",
    "Dá uma nota de risco de 0 a 100 com um modelo de regressão logística.",
    "Decide entre aprovar, pedir confirmação ao cliente ou bloquear e enviar ao analista.",
    "Explica a decisão em português com o IBM Granite, ou a partir dos sinais.",
    "O analista confirma a fraude ou marca como legítima, e a resposta fica registrada.",
]
TITULO_SINAIS_COMO = "Os 9 sinais de alerta"
SINAIS_EXPLICADOS = [
    ("Uso acelerado em terminais", "Cartão usado {LIMIAR_VELOCIDADE_TERMINAL} vezes ou mais em terminais na última hora"),
    ("Rajada de transações", "{LIMIAR_RAJADA_1MIN} transações ou mais do cartão no último minuto"),
    ("Token de carteira digital", "Token usado {LIMIAR_TOKEN_CARTEIRA} vezes ou mais em 3 meses"),
    ("Salto geográfico", "Terminal a mais de {LIMIAR_DISTANCIA_KM} km do anterior em menos de uma hora"),
    ("Madrugada", "Compra feita antes das {HORA_FIM_MADRUGADA}h da manhã"),
    ("Valor alto", "Valor acima de R$ {LIMIAR_VALOR_ALTO}"),
    ("Crédito sem cartão presente", "Compra online no crédito"),
    ("IP de país desconhecido", "Endereço IP sem país identificado (código ZZ)"),
    ("Estabelecimento de risco", "Risco do estabelecimento igual ou acima de {LIMIAR_RISCO_ESTABELECIMENTO}"),
]
TITULO_DECISAO = "Como a decisão é tomada"
REGRAS_DECISAO = [
    "Bloquear e enviar ao analista: nota de {NOTA_BLOQUEAR} ou mais, ou IP de país desconhecido.",
    "Pedir confirmação ao cliente: nota de {NOTA_CONFIRMAR} ou mais, ou {MIN_SINAIS_CONFIRMAR} sinais ou mais.",
    "Aprovar: nos demais casos.",
]
TITULO_DADOS = "Sobre os dados"
SOBRE_DADOS = ("A base tem {linhas} transações sintéticas de 2025, das quais {fraudes} são fraude "
               "({percentual}). A fila de demonstração tem todas as fraudes de março e {amostra} "
               "compras legítimas de março sorteadas.")
TITULO_LIMITACOES = "Limitações"
LIMITACOES = [
    "Os dados são sintéticos e fáceis de separar; em dados reais o desempenho seria menor.",
    "Todas as fraudes da base estão entre janeiro e março de 2025; em uso real, o modelo precisa de monitoramento.",
    "Pedir confirmação ao cliente é só indicado na tela; nenhuma notificação é enviada.",
    "As respostas do analista ficam salvas, mas ainda não retreinam o modelo automaticamente.",
]
```

Os rótulos dos indicadores da Fila usam `METRICA_NA_FILA` e o `rotulo_curto` de cada decisão;
os da página Desempenho e os cabeçalhos de tabela são os escritos nas seções 7.3, 7.5 e 8.

## 12. Formatação pt-BR (`src/interface/formatacao.py`)

Funções puras, todas com teste em `tests/test_formatacao.py`. Os exemplos são os casos de teste.

| Função | Entrada | Saída |
| --- | --- | --- |
| `formatar_moeda(valor)` | `1234.5` · `None` ou `NaN` | `"R$ 1.234,50"` · `"valor indisponível"` |
| `formatar_nota(nota)` | `97.34` · `100` | `"97,3"` · `"100,0"` |
| `formatar_inteiro(n)` | `2054` | `"2.054"` |
| `formatar_decimal(valor, casas)` | `0.99812, 3` | `"0,998"` |
| `formatar_percentual(fracao)` | `0.4815` · `0.0117` | `"48,1%"` · `"1,2%"` |
| `formatar_data_hora(momento)` | `Timestamp("2025-03-15 03:12:40")` · `NaT` ou `None` | `"15/03/2025 03:12"` · `"data indisponível"` |
| `formatar_tipo(tipo)` | `"credito"` · `"xyz"` | `"Crédito"` · `"xyz"` |
| `formatar_modalidade(m)` | `"cartao_nao_presente"` | `"Não presente"` |
| `rotulo_resposta(r)` | `"legitima"` | `"Transação legítima"` |
| `escapar_markdown(texto)` | `"R$ 10 e R$ 20"` | `"R\$ 10 e R\$ 20"` |

## 13. Módulos de apoio

### 13.1 `src/interface/dados.py`

| Função | Cache | Regra |
| --- | --- | --- |
| `verificar_arquivos(caminho_dados=CAMINHO_PREPARADO, caminho_modelo=CAMINHO_MODELO) -> list[str]` | não | Lista os textos de erro dos arquivos ausentes, na ordem dados e modelo. Testada com caminhos temporários |
| `carregar_base() -> pd.DataFrame` | `st.cache_data(show_spinner=False)` | Lê `CAMINHO_PREPARADO` |
| `carregar_agente() -> AgenteSentinela` | `st.cache_resource(show_spinner=False)` | `AgenteSentinela(base=carregar_base())` |
| `montar_fila(base, analisar_lote, tamanho_amostra=TAMANHO_AMOSTRA_LEGITIMAS, semente=SEMENTE) -> pd.DataFrame` | não (pura) | Filtra março (`INICIO_TESTE` ≤ data < `FIM_TESTE`); junta todas as fraudes e uma amostra de legítimas (`min(tamanho, disponíveis)`, `random_state=semente`); aplica `analisar_lote`; ordena por `nota` decrescente e `id_transacao` crescente; remove `fraude` e `decisao_sistema_atual`; `reset_index(drop=True)` |
| `carregar_fila() -> pd.DataFrame` | `st.cache_data(show_spinner=textos.CARREGANDO_FILA)` | `montar_fila(carregar_base(), carregar_agente().analisar_lote)` |
| `contar_por_decisao(fila) -> dict[str, int]` | não (pura) | Uma chave por item de `ORDEM_DECISOES`, zero quando não houver |
| `carregar_json(caminho) -> dict | None` | `st.cache_data(show_spinner=False)` | `None` se o arquivo não existir |
| `granite_esta_disponivel() -> bool` | `st.cache_data(ttl=30, show_spinner=False)` | Chama `src.agente.granite_disponivel()` |

`montar_fila` recebe `analisar_lote` como parâmetro (injeção de dependência) para ser testada sem
o modelo, com uma função falsa.

### 13.2 `src/interface/feedback.py`

```python
COLUNAS_FEEDBACK = ["registrado_em", "id_transacao", "nota", "decisao", "resposta_analista"]
RESPOSTAS_VALIDAS = ("fraude", "legitima")

@dataclass(frozen=True)
class RespostaAnalista:
    id_transacao: int
    nota: float
    decisao: str
    resposta_analista: str
    registrado_em: datetime

def registrar_resposta(caminho: Path, resposta: RespostaAnalista) -> None: ...
def ler_ultima_resposta(caminho: Path, id_transacao: int) -> RespostaAnalista | None: ...
```

- `registrar_resposta`: `ValueError` se `resposta_analista` não estiver em `RESPOSTAS_VALIDAS`;
  cria a pasta se faltar; acrescenta uma linha com o módulo `csv` (`encoding="utf-8"`,
  `newline=""`), escrevendo o cabeçalho só se o arquivo não existir; `registrado_em` em ISO 8601
  com segundos. `OSError` sobe para a página tratar.
- `ler_ultima_resposta`: arquivo ausente → `None`; cabeçalho diferente de `COLUNAS_FEEDBACK` →
  `ValueError`; devolve a última linha daquele `id_transacao`, ou `None`.
- Testes em `tests/test_feedback.py`, todos com `tmp_path`: grava e lê; arquivo ausente;
  a última resposta vale; resposta inválida; cabeçalho escrito uma única vez; cabeçalho inválido.

### 13.3 `app.py`

1. `st.set_page_config(page_title=textos.TITULO_APP, page_icon=":material/shield:", layout="wide")`.
2. `erros = dados.verificar_arquivos()`; para cada erro, `st.error(erro, icon=ICONE_ERRO)`;
   se houver erro, `st.stop()`.
3. `pagina = st.navigation([...])` com as três páginas da seção 3, cada `st.Page` com `title`,
   `icon` e `url_path` da tabela (a primeira com `default=True`).
4. Barra lateral: `st.toggle(ROTULO_TOGGLE_GRANITE, value=True, key="usar_granite",
   help=AJUDA_TOGGLE_GRANITE)`; estado com `st.caption` e o ícone correspondente
   (`STATUS_GRANITE_ON`, `STATUS_GRANITE_OFF` ou `STATUS_GRANITE_DESLIGADO`); `st.caption(RODAPE_DADOS)`.
5. `pagina.run()`.

`app.py` só orquestra: nenhuma regra de negócio, nenhum texto literal.

## 14. Acessibilidade (WCAG 2.2 AA, checklist do Manual 2.3.11)

| # | Item | Como o design atende | Como verificar |
| --- | --- | --- | --- |
| 1 | Contraste | Tokens da seção 5.1, todos acima de 4,5:1 (medidos) | Lighthouse no Chrome; faixas de decisão medidas na auditoria (Issue #6) |
| 2 | Alvos de toque | Botões e pílulas nativos do Streamlit, acima de 24×24 px | Inspecionar no navegador |
| 3 | Cor não é o único sinal | Decisão com emoji de forma distinta e texto; gráfico com tabela dos mesmos números; estado do Granite em texto | Ver a tela em escala de cinza |
| 4 | Teclado | Todos os widgets nativos recebem foco; escolha por ID como alternativa ao clique na tabela | Percorrer a Fila só com Tab, setas e Enter |
| 5 | Rótulos explícitos | Todo widget com rótulo visível; nunca `label_visibility="collapsed"`; botões com texto e ícone | Revisão do código |
| 6 | Textos alternativos | Sem imagens; o gráfico tem tabela equivalente | — |
| 7 | Estrutura semântica | Um `st.title` por página e seções com `st.header` | Lighthouse |
| 8 | Tipografia | Corpo de 16 px; layout se reorganiza com zoom de 200% | Zoom do navegador |
| 9 | Erros recuperáveis | Toda mensagem de erro diz como resolver | Seção 10 |
| 10 | Movimento | Nenhuma animação própria; proibido `st.balloons` e `st.snow` | Revisão do código |

## 15. Heurísticas de Nielsen (revisão)

| # | Heurística | Como o design atende |
| --- | --- | --- |
| 1 | Visibilidade do status | Spinners com texto, estado do Granite, "Mostrando N de M", resposta atual no painel |
| 2 | Mundo real | Linguagem do analista ("Bloquear", "Sinais de alerta"), valores em R$ e datas pt-BR |
| 3 | Controle e liberdade | Resposta pode ser mudada (vale a última); filtro reversível; Granite pode ser desligado |
| 4 | Consistência | Decisões sempre com o mesmo emoji, ícone e rótulo, vindos de `tema.py` e `config.py` |
| 5 | Prevenção de erros | Resposta inválida é recusada no módulo; botões com chave por transação evitam gravar na transação errada |
| 6 | Reconhecer em vez de lembrar | Fila e painel juntos; histórico do cartão no próprio painel |
| 7 | Eficiência | Primeira linha já aberta; fila ordenada; escolha por ID |
| 8 | Minimalismo | Tela principal sem gráficos; histórico recolhido por padrão |
| 9 | Recuperação de erros | Mensagens com a causa e o comando ou ação para resolver |
| 10 | Ajuda | Página "Como funciona" e textos de ajuda (`help=`) nos indicadores e no interruptor |

Na Issue #6, duas pessoas percorrem os fluxos de [03-user-flows.md](03-user-flows.md)
separadamente, anotam violações com severidade alta, média ou baixa e só depois comparam. Achados
de severidade alta são corrigidos antes da versão de entrega.

## 16. Responsividade

Contexto dominante: desktop com 1280 px ou mais. Abaixo de cerca de 640 px o Streamlit empilha as
colunas: o painel vai para baixo da tabela, e a tabela rola na horizontal. Isso é aceitável para
um console de analista e é verificado na auditoria estreitando a janela.

## 17. Proibido na interface

- Texto literal fora de `textos.py`; cor, ícone ou rótulo de decisão fora de `tema.py` e `config.py`.
- Regra do agente reimplementada na interface.
- `st.exception`, stack trace, `st.balloons`, `st.snow`, `unsafe_allow_html=True`.
- Linhas coloridas por decisão com `df.style` (a decisão já tem emoji e texto).
- Colunas `fraude` ou `decisao_sistema_atual` em qualquer tabela ou texto.
- Chamar o Granite fora do painel ou mais de uma vez por transação na sessão.
