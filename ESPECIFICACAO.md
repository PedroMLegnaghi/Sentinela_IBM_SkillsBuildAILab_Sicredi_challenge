# ESPECIFICACAO.md — Projeto Sentinela (Desafio Sicredi, IBM SkillsBuild AI Lab)

Este arquivo é a fonte da verdade do projeto. Quem escreve o código é o IBM Bob.
Bob: leia este arquivo inteiro antes de qualquer tarefa e siga-o à risca. Se um pedido
do usuário conflitar com este arquivo, avise e siga este arquivo. Não invente colunas,
arquivos, bibliotecas ou números que não estejam aqui.

## 1. Objetivo

Sentinela é um agente de IA para prevenção a fraudes em transações de cartão. Para cada
transação ele: (1) calcula sinais de alerta por regras; (2) dá uma nota de risco de 0 a
100 com um modelo de machine learning; (3) decide entre APROVAR, PEDIR_CONFIRMACAO ou
BLOQUEAR; (4) explica a decisão em português para um analista humano, usando o modelo
IBM Granite local (Ollama), com texto automático de reserva; (5) registra a resposta do
analista para retreino futuro.

## 2. Regras gerais

- Python 3.11 ou mais novo. Bibliotecas permitidas (requirements.txt, sem fixar versão):
  pandas, pyarrow, scikit-learn, joblib, streamlit, requests, pytest. Nenhuma outra.
- Todo texto visível ao usuário, comentários e docstrings em português do Brasil.
  Nomes de arquivos, funções e colunas sem acento.
- Caminhos sempre com pathlib, relativos à raiz do repositório (RAIZ = pasta que contém
  este arquivo). O código deve funcionar em Windows, macOS e Linux.
- Arquivos de texto sempre com encoding="utf-8".
- Toda aleatoriedade usa a semente 42.
- `src/` é um pacote (tem `__init__.py`). Scripts são executados da raiz com
  `python -m src.nome_do_modulo`. Existe um `conftest.py` vazio na raiz para o pytest.
- A pasta `data/` nunca vai para o Git (está no .gitignore). A pasta `modelos/` vai.
- Não altere arquivos de etapas anteriores sem necessidade. Se precisar, explique o
  motivo antes.
- Ao terminar cada etapa: rode os comandos de verificação da etapa, mostre a saída,
  compare com os critérios de aceite da seção 11 e só então faça commit e push.

## 3. Estrutura de pastas (exata)

    ESPECIFICACAO.md
    README.md
    requirements.txt
    .gitignore
    conftest.py
    app.py
    src/__init__.py
    src/config.py
    src/preparar_dados.py
    src/treinar_modelo.py
    src/agente.py
    src/avaliar_agente.py
    tests/test_agente.py
    modelos/sentinela.joblib
    modelos/metricas.json
    modelos/avaliacao_agente.json
    data/case_transacoes_cartoes_sintetico_900k.csv.gz    (não versionado)
    data/transacoes_preparadas.parquet                     (não versionado)
    data/feedback.csv                                      (não versionado)

## 4. Dados de entrada

Arquivo: `data/case_transacoes_cartoes_sintetico_900k.csv.gz` (CSV com vírgula, cabeçalho,
compactado em gzip; 900.000 linhas; 297 colunas; dados 100% sintéticos da Sicredi).

Carregar SOMENTE estas 16 colunas (parâmetro usecols), nunca o arquivo inteiro:

| Coluna original | Tipo | Observações |
| --- | --- | --- |
| event_occurred_at | texto ISO "2025-07-22T13:57:56" | cerca de 0,2% vazio |
| card_id | texto | cerca de 0,4% vazio |
| customer_id | texto | pode ter vazios |
| acceptor_id | texto | pode ter vazios |
| amount | decimal | valor em reais; cerca de 0,4% vazio |
| tipo_transacao | texto | "debito" ou "credito"; sem vazios |
| modalidade_transacao | texto | "cartao_presente" ou "cartao_nao_presente"; sem vazios |
| device_ip_country_code | texto | valores "BR", "No" e "ZZ"; "ZZ" = país desconhecido |
| cp_card_term_vel_1h | número | cerca de 8% vazio |
| cardid_count_1m | número | cerca de 8% vazio |
| digitalwallettoken_count_3m | número | cerca de 8% vazio |
| cp_card_prev_term_dist_1h | decimal (km) | cerca de 8% vazio |
| acceptor_risk | número | cerca de 8% vazio |
| mcc | número | cerca de 1% vazio |
| decision | texto | "approve", "deny" ou vazio (8%); decisão do sistema atual |
| feedback_label | booleano | True = fraude. É O RÓTULO. |

## 5. Colunas proibidas (vazamento de informação)

Estas colunas entregam a resposta ou só existem depois da decisão. Nunca usar como
entrada do modelo nem das regras:
`fraud`, `fraud_score`, `visa_fraud_score`, `mc_fraud_score`, `decision`,
`transaction_status`, `action_code`, `reason_code`, `alert_id`, e todas que começam com
`dispute_`, `fdz_` ou `oob_`.

Atenção: a coluna `fraud` NÃO é o rótulo (ela está errada em quase todas as linhas).
O rótulo é `feedback_label`. A coluna `decision` é carregada apenas para comparar o
Sentinela com o sistema atual, nunca como entrada.

## 6. Dados preparados: `data/transacoes_preparadas.parquet`

Gerado por `python -m src.preparar_dados`. Uma linha por transação, todas as 900.000
linhas (não descartar linhas). Colunas exatas, nesta ordem:

| Coluna | Tipo | Como calcular |
| --- | --- | --- |
| id_transacao | int64 | número da linha no CSV original, começando em 0 |
| data_hora | datetime64 | pd.to_datetime(event_occurred_at, errors="coerce") |
| id_cartao | texto | card_id |
| id_cliente | texto | customer_id |
| id_estabelecimento | texto | acceptor_id |
| valor | float64 | amount |
| tipo_transacao | texto | igual ao original |
| modalidade_transacao | texto | igual ao original |
| hora | float64 | hora de data_hora (0 a 23); vazio se data_hora for vazia |
| madrugada | int64 | 1 se hora < 5; senão 0 (0 também quando hora é vazia) |
| credito | int64 | 1 se tipo_transacao == "credito"; senão 0 |
| nao_presente | int64 | 1 se modalidade_transacao == "cartao_nao_presente"; senão 0 |
| ip_pais_desconhecido | int64 | 1 se device_ip_country_code == "ZZ"; senão 0 |
| vel_cartao_terminal_1h | float64 | cp_card_term_vel_1h |
| qtd_transacoes_cartao_1min | float64 | cardid_count_1m |
| qtd_token_carteira_3m | float64 | digitalwallettoken_count_3m |
| dist_terminal_anterior_km | float64 | cp_card_prev_term_dist_1h |
| risco_estabelecimento | float64 | acceptor_risk |
| mcc | float64 | mcc |
| decisao_sistema_atual | texto | decision ("approve", "deny" ou vazio) |
| fraude | int64 | 1 se feedback_label for True; senão 0 |

Valores vazios NÃO são preenchidos nesta etapa (o modelo trata isso).
Ao final, o script imprime: total de linhas; total de fraudes; fraudes por mês;
contagem por tipo_transacao; percentual de vazios por coluna; contagem de
ip_pais_desconhecido == 1 e quantas dessas são fraude.

## 7. Modelo: `python -m src.treinar_modelo`

Lista de variáveis de entrada (constante `VARIAVEIS_MODELO` em `src/config.py`, nesta ordem):
`valor`, `hora`, `madrugada`, `credito`, `nao_presente`, `ip_pais_desconhecido`,
`vel_cartao_terminal_1h`, `qtd_transacoes_cartao_1min`, `qtd_token_carteira_3m`,
`dist_terminal_anterior_km`, `risco_estabelecimento`.
Nenhuma outra coluna entra no modelo. Alvo: `fraude`.

Divisão temporal (nunca aleatória):
- treino: data_hora de 2025-01-01 (inclusive) até 2025-03-01 (exclusive);
- teste: data_hora de 2025-03-01 (inclusive) até 2025-04-01 (exclusive);
- linhas sem data_hora ficam fora de treino e teste.
Motivo: todas as fraudes da base estão entre janeiro e março de 2025.

Modelo final (obrigatório): um `sklearn.pipeline.Pipeline` com
1. `SimpleImputer(strategy="median", add_indicator=True)`
2. `StandardScaler()`
3. `LogisticRegression(class_weight="balanced", max_iter=2000, random_state=42)`
O pipeline recebe um DataFrame com as colunas de `VARIAVEIS_MODELO` e é salvo em
`modelos/sentinela.joblib` com joblib. A nota de risco é `predict_proba[:, 1] * 100`.

Modelo de comparação (não é salvo): `HistGradientBoostingClassifier(class_weight="balanced",
max_iter=200, learning_rate=0.05, random_state=42)` com as mesmas variáveis.

Métricas no teste, salvas em `modelos/metricas.json` com exatamente estas chaves:

    {
      "modelo": "regressao_logistica",
      "treino": {"linhas": 0, "fraudes": 0},
      "teste": {"linhas": 0, "fraudes": 0},
      "pr_auc": 0.0,
      "roc_auc": 0.0,
      "limiares": [{"limiar": 30, "alertas": 0, "fraudes_detectadas": 0, "precisao": 0.0, "recall": 0.0}],
      "comparacao_hgb": {"pr_auc": 0.0, "roc_auc": 0.0},
      "sistema_atual": {"bloqueadas": 0, "fraudes_bloqueadas": 0, "fraudes_total": 0}
    }

- `limiares`: uma entrada para cada nota de corte 30, 50, 70 e 90 (alerta = nota >= corte).
- `sistema_atual`: no teste, bloqueadas = linhas com decisao_sistema_atual == "deny".
- PR-AUC = average_precision_score. O script também imprime tudo isso na tela e os
  coeficientes da regressão logística por variável.

## 8. Agente: `src/config.py` e `src/agente.py`

### 8.1 `src/config.py` (constantes)

    RAIZ = pasta raiz do repositório (pathlib)
    CAMINHO_CSV = RAIZ / "data" / "case_transacoes_cartoes_sintetico_900k.csv.gz"
    CAMINHO_PREPARADO = RAIZ / "data" / "transacoes_preparadas.parquet"
    CAMINHO_FEEDBACK = RAIZ / "data" / "feedback.csv"
    CAMINHO_MODELO = RAIZ / "modelos" / "sentinela.joblib"
    CAMINHO_METRICAS = RAIZ / "modelos" / "metricas.json"
    CAMINHO_AVALIACAO = RAIZ / "modelos" / "avaliacao_agente.json"
    VARIAVEIS_MODELO = [lista da seção 7]
    NOTA_CONFIRMAR = 30
    NOTA_BLOQUEAR = 70
    MIN_SINAIS_CONFIRMAR = 3
    OLLAMA_URL = "http://localhost:11434"
    OLLAMA_MODELO = "granite4:micro"
    OLLAMA_TIMEOUT_S = 60

### 8.2 Sinais de alerta (regras)

Função `calcular_sinais(transacao: dict) -> list[dict]`. Cada sinal devolvido é
`{"id": ..., "descricao": ...}`. Um sinal só dispara se o valor existir (valor vazio,
None ou NaN nunca dispara e nunca gera erro). Ordem fixa:

| id | Condição | descricao (preencher os valores) |
| --- | --- | --- |
| velocidade_terminal | vel_cartao_terminal_1h >= 10 | "Cartão usado {v:.0f} vezes em terminais na última hora (normal: até 5)." |
| rajada_1min | qtd_transacoes_cartao_1min >= 5 | "{v:.0f} transações do cartão no último minuto (normal: 1 ou 2)." |
| token_carteira | qtd_token_carteira_3m >= 30 | "Token de carteira digital usado {v:.0f} vezes em 3 meses (normal: até 14)." |
| salto_geografico | dist_terminal_anterior_km > 100 | "Terminal a {v:.0f} km do anterior em menos de uma hora." |
| madrugada | madrugada == 1 | "Compra feita de madrugada, às {hora:.0f}h." |
| valor_alto | valor > 150 | "Valor de R$ {v:.2f}, acima do padrão (mediana das compras: R$ 35)." |
| credito_nao_presente | credito == 1 e nao_presente == 1 | "Compra no crédito sem cartão presente (online)." |
| ip_desconhecido | ip_pais_desconhecido == 1 | "Endereço IP de país desconhecido." |
| estabelecimento_risco | risco_estabelecimento >= 40 | "Estabelecimento com risco {v:.0f} (normal: abaixo de 37)." |

### 8.3 Decisão

Função `decidir(nota: float, sinais: list[dict]) -> str`, nesta ordem:
1. `"BLOQUEAR"` se nota >= NOTA_BLOQUEAR, ou se existir o sinal `ip_desconhecido`.
2. `"PEDIR_CONFIRMACAO"` se nota >= NOTA_CONFIRMAR, ou se a quantidade de sinais for
   >= MIN_SINAIS_CONFIRMAR.
3. `"APROVAR"` nos demais casos.

Textos legíveis: BLOQUEAR = "Bloquear e enviar ao analista"; PEDIR_CONFIRMACAO =
"Pedir confirmação ao cliente"; APROVAR = "Aprovar".

### 8.4 Classe `AgenteSentinela`

- `__init__(self, caminho_modelo=CAMINHO_MODELO, base: pd.DataFrame | None = None)`:
  carrega o pipeline com joblib; se o arquivo não existir, levanta FileNotFoundError com
  a mensagem "Modelo não encontrado. Rode: python -m src.treinar_modelo". `base` é o
  DataFrame preparado, usado só por `historico_cartao` (pode ser None).
- `pontuar(self, transacao: dict) -> float`: monta um DataFrame de 1 linha com
  VARIAVEIS_MODELO (chave ausente ou None vira NaN) e devolve a nota de 0 a 100
  arredondada com 1 casa.
- `historico_cartao(self, id_cartao, antes_de=None, n=10) -> pd.DataFrame`: últimas n
  transações do cartão em `base`, ordenadas da mais recente para a mais antiga; se
  `antes_de` (datetime) for dado, só transações anteriores a ele. Devolve DataFrame
  vazio se base for None, se id_cartao for vazio ou se não houver transações.
- `explicar(self, transacao, nota, sinais, decisao, usar_llm=True) -> tuple[str, str]`:
  devolve (texto, fonte), com fonte "granite" ou "regras". Ver 8.5.
- `analisar(self, transacao: dict, usar_llm: bool = True) -> dict`: roda
  calcular_sinais, pontuar, decidir e explicar, e devolve exatamente:
  `{"nota": float, "sinais": list[dict], "decisao": str, "decisao_legivel": str,
  "explicacao": str, "fonte_explicacao": str}`.
- `analisar_lote(self, df: pd.DataFrame) -> pd.DataFrame`: versão rápida para muitas
  linhas, sem LLM. Devolve cópia de df com as colunas novas `nota` (predict_proba em
  lote, 1 casa), `n_sinais` (int) e `decisao`. Deve dar o mesmo resultado que
  `analisar` linha a linha.

`calcular_sinais` e `decidir` são funções de módulo (fora da classe) e não dependem do
arquivo do modelo.

### 8.5 Explicação

Se `usar_llm` for True: primeiro um GET em `{OLLAMA_URL}/api/tags` com timeout de 2
segundos. Se falhar, usar o texto de reserva. Se responder, fazer POST em
`{OLLAMA_URL}/api/generate` com timeout OLLAMA_TIMEOUT_S e o JSON:
`{"model": OLLAMA_MODELO, "prompt": PROMPT, "stream": false, "options": {"temperature": 0.2, "num_predict": 200}}`.
O texto vem no campo `"response"` do JSON de resposta. Qualquer exceção, status
diferente de 200 ou resposta vazia leva ao texto de reserva. Nunca deixar o erro subir.

PROMPT (exato; preencher as chaves):

    Você é um assistente de prevenção a fraudes de uma cooperativa de crédito.
    Explique para um analista, em exatamente 3 frases curtas em português do Brasil,
    por que a transação abaixo recebeu a decisão indicada. Use apenas os dados
    fornecidos. Não invente informações. Não use listas nem markdown.

    Decisão: {decisao_legivel}
    Nota de risco: {nota}/100
    Valor: R$ {valor}
    Data e hora: {data_hora}
    Tipo: {tipo_transacao}, {modalidade_transacao}
    Sinais de alerta:
    {uma linha "- descricao" por sinal, ou "- nenhum sinal de alerta"}

Texto de reserva (fonte "regras"):
- com sinais: "Decisão: {decisao_legivel} (nota {nota}/100). Motivos: " seguido das
  descrições dos sinais separadas por espaço.
- sem sinais: "Decisão: {decisao_legivel} (nota {nota}/100). Nenhum sinal de alerta
  foi encontrado; a transação segue o padrão de compras legítimas."

### 8.6 `python -m src.avaliar_agente`

Carrega os dados preparados, filtra o teste (março de 2025, como na seção 7), roda
`analisar_lote` e salva `modelos/avaliacao_agente.json` com exatamente:

    {
      "periodo": "2025-03",
      "transacoes": 0,
      "fraudes_total": 0,
      "sentinela": {
        "bloqueadas": 0, "fraudes_bloqueadas": 0,
        "confirmacoes": 0, "fraudes_em_confirmacao": 0,
        "aprovadas": 0, "fraudes_aprovadas": 0
      },
      "sistema_atual": {"bloqueadas": 0, "fraudes_bloqueadas": 0, "fraudes_nao_bloqueadas": 0}
    }

Também imprime esses números na tela.

## 9. Testes: `tests/test_agente.py` (pytest)

Transação FRAUDE de exemplo: valor 400.0, hora 3, madrugada 1, credito 1, nao_presente 1,
ip_pais_desconhecido 0, vel_cartao_terminal_1h 45, qtd_transacoes_cartao_1min 20,
qtd_token_carteira_3m 80, dist_terminal_anterior_km 300.0, risco_estabelecimento 45,
tipo_transacao "credito", modalidade_transacao "cartao_nao_presente".
Transação LEGITIMA de exemplo: valor 30.0, hora 14, madrugada 0, credito 0, nao_presente 0,
ip_pais_desconhecido 0, vel_cartao_terminal_1h 2, qtd_transacoes_cartao_1min 1,
qtd_token_carteira_3m 7, dist_terminal_anterior_km 10.0, risco_estabelecimento 18,
tipo_transacao "debito", modalidade_transacao "cartao_presente".

Testes obrigatórios:
1. calcular_sinais(FRAUDE) devolve 8 sinais (todos menos ip_desconhecido).
2. calcular_sinais(LEGITIMA) devolve lista vazia.
3. calcular_sinais com todos os campos None ou NaN devolve lista vazia, sem erro.
4. decidir(10, []) == "APROVAR"; decidir(50, []) == "PEDIR_CONFIRMACAO";
   decidir(10, três sinais quaisquer) == "PEDIR_CONFIRMACAO"; decidir(90, []) == "BLOQUEAR";
   decidir(5, [sinal ip_desconhecido]) == "BLOQUEAR".
5. Com o modelo (pular com pytest.mark.skipif se modelos/sentinela.joblib não existir):
   analisar(FRAUDE, usar_llm=False) tem decisao "BLOQUEAR" e nota >= 70;
   analisar(LEGITIMA, usar_llm=False) tem decisao "APROVAR" e nota < 30;
   o dicionário devolvido tem exatamente as 6 chaves da seção 8.4;
   fonte_explicacao == "regras" quando usar_llm=False.
6. Com o modelo: analisar_lote de um DataFrame com as duas transações dá as mesmas
   decisões que analisar.

Os testes não dependem da pasta data/ nem do Ollama.

## 10. Interface: `app.py` (Streamlit)

Executar com `streamlit run app.py`. `st.set_page_config(page_title="Sentinela",
layout="wide")`. Importa `AgenteSentinela` de `src.agente` e constantes de `src.config`.
Se o modelo ou os dados preparados não existirem, mostrar `st.error` com o comando que
falta rodar e `st.stop()`.

Carga (com `st.cache_data` / `st.cache_resource`): ler o parquet preparado; a "fila" é:
todas as fraudes de março de 2025 mais 2.000 transações legítimas de março sorteadas com
`random_state=42`; rodar `analisar_lote`; ordenar por nota decrescente.

Barra lateral: título "Sentinela"; `st.radio` de navegação com "Fila de alertas" e
"Desempenho"; caixa "Explicar com IBM Granite (Ollama)" (marcada por padrão); texto curto
"Dados 100% sintéticos (Sicredi)".

Página "Fila de alertas":
- 4 métricas no topo (`st.metric`): transações na fila; bloqueadas; pedir confirmação;
  aprovadas.
- Filtro `st.multiselect` por decisão (padrão: BLOQUEAR e PEDIR_CONFIRMACAO).
- Tabela (`st.dataframe`) com colunas: id_transacao, data_hora, valor, tipo_transacao,
  modalidade_transacao, nota, n_sinais, decisao. Linhas coloridas por decisão com
  `df.style`: BLOQUEAR vermelho claro, PEDIR_CONFIRMACAO amarelo claro, APROVAR verde claro.
- `st.selectbox` "Escolha uma transação para analisar", com rótulo
  "{id_transacao} | nota {nota} | {decisao_legivel} | R$ {valor}".
- Detalhe da transação escolhida: decisão em destaque (`st.error` para BLOQUEAR,
  `st.warning` para PEDIR_CONFIRMACAO, `st.success` para APROVAR); nota com
  `st.progress`; lista dos sinais; explicação do agente gerada na hora com
  `agente.analisar(transacao, usar_llm=caixa)` dentro de `st.spinner`, mostrando embaixo
  "Explicação gerada por: IBM Granite 4" ou "Explicação gerada por: regras";
  histórico do cartão (`historico_cartao(id_cartao, antes_de=data_hora)`) em tabela.
- Dois botões: "Confirmar fraude" e "Marcar como legítima". Cada clique acrescenta uma
  linha em `data/feedback.csv` (criar com cabeçalho se não existir) com as colunas
  `registrado_em, id_transacao, nota, decisao, resposta_analista` (resposta_analista =
  "fraude" ou "legitima") e mostra `st.toast("Resposta registrada")`.
- A coluna `fraude` (rótulo real) nunca aparece na fila nem no detalhe.

Página "Desempenho":
- Lê `modelos/metricas.json` e `modelos/avaliacao_agente.json`.
- Métricas: PR-AUC, ROC-AUC, fraudes no teste.
- Tabela comparando "Sistema atual" e "Sentinela" em março: fraudes bloqueadas, fraudes
  não bloqueadas, percentual de fraudes bloqueadas.
- Gráfico de barras (`st.bar_chart`) com fraudes bloqueadas: sistema atual x Sentinela.
- Tabela dos limiares (alertas, precisão, recall).
- Aviso `st.info`: "Dados sintéticos: o resultado é otimista. Em produção o modelo
  precisa de monitoramento e retreino."

## 11. Critérios de aceite (valores esperados com a base completa de 900 mil linhas)

Se um número sair muito diferente, há erro: pare e investigue antes de continuar.

Etapa 1 (dados preparados):
- 900.000 linhas e 21 colunas no parquet; exatamente 900 fraudes (0,10%).
- 540.000 débito e 360.000 crédito.
- Todas as fraudes entre janeiro e março de 2025; zero fraudes de abril a dezembro.
- Toda linha com ip_pais_desconhecido == 1 é fraude (algumas centenas de linhas).
- Cerca de 8% de vazios nas colunas de velocidade, distância e risco.

Etapa 2 (modelo):
- Teste (março) com cerca de 75 mil linhas e algumas centenas de fraudes.
- PR-AUC e ROC-AUC acima de 0,95 (os dados são sintéticos e fáceis de separar).
- No corte 70: recall acima de 0,90 e precisão acima de 0,90.
- Sistema atual: bloqueia só cerca de metade das fraudes de março.
- Coeficientes mais fortes: velocidade, rajada em 1 minuto e distância.

Etapa 3 (agente):
- `pytest` passa todos os testes.
- avaliar_agente: Sentinela bloqueia mais de 90% das fraudes de março; zero ou quase
  zero fraudes aprovadas; pedidos de confirmação em cerca de 1% das transações.

Etapa 4 (interface):
- `streamlit run app.py` abre sem erro; as duas páginas funcionam; a explicação aparece
  com o Ollama ligado ("IBM Granite 4") e desligado ("regras"); os botões gravam em
  data/feedback.csv.

Etapa 5 (entrega):
- README completo; `pytest` passa; repositório sem a pasta data/.
