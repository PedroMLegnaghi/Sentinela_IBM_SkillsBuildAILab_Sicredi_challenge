# ESPECIFICACAO.md — Projeto Sentinela (Desafio Sicredi, IBM SkillsBuild AI Lab)

Versão 5 (13/11/2026). Este arquivo define O QUE o sistema faz: dados, modelo, agente, API,
auditoria por IA, canal do associado, site e números esperados. COMO trabalhar está no
`AGENTS.md`; as tarefas, em `docs/backlog.md`.
Quem escreve o código é o IBM Bob. Não invente colunas, arquivos, bibliotecas ou números que
não estejam aqui. Se um pedido conflitar com este arquivo, pare e pergunte.

## 1. Objetivo

Sentinela é um agente de IA para prevenção a fraudes em transações de cartão. Para cada
transação ele: (1) calcula sinais de alerta por regras; (2) dá uma nota de risco de 0 a
100 com um modelo de machine learning; (3) decide entre APROVAR, PEDIR_CONFIRMACAO ou
BLOQUEAR; (4) explica a decisão em português; (5) em paralelo, um agente de IA no IBM watsonx.ai audita a
decisão (seção 13); (6) quando a decisão pede confirmação ou bloqueia, avisa o associado e recebe
a resposta dele (seção 15); (7) registra a resposta do analista para retreino futuro.

## 2. Regras gerais

- Python 3.14. Bibliotecas de execução em `requirements.txt`, com versão fixada
  (`pacote==versão`): pandas, numpy, pyarrow, scikit-learn, joblib, requests, pytest, fastapi,
  uvicorn, httpx. Ferramentas de desenvolvimento em `requirements-dev.txt`: black, ruff. O site
  (`web/`) tem as dependências fixadas em `web/package.json`. Biblioteca nova exige ADR em
  `docs/decisoes.md` e aprovação do líder.
- Convenções de código, idioma, testes, erros, Git e revisão: ver `AGENTS.md`.
- Caminhos sempre com pathlib, relativos à raiz do repositório (RAIZ = pasta que contém
  este arquivo). O código deve funcionar em Windows, macOS e Linux.
- Arquivos de texto sempre com encoding="utf-8".
- Toda aleatoriedade usa a semente 42 (constante SEMENTE).
- `src/` é um pacote (tem `__init__.py`). Scripts são executados da raiz com
  `python -m src.nome_do_modulo`. Existe um `conftest.py` vazio na raiz para o pytest.
- Da pasta `data/`, só vão para o Git o CSV comprimido (`.csv.gz`), o dicionário, as orientações e o
  parquet (ADR-016); o CSV bruto (281 MB) e `feedback.csv` ficam fora. A pasta `modelos/` vai.

## 3. Estrutura de pastas

    AGENTS.md  ESPECIFICACAO.md  README.md     regras, contrato e apresentação
    requirements.txt  requirements-dev.txt     dependências Python, versões fixadas
    pyproject.toml  conftest.py  .env.example  configuração (Black, Ruff, pytest, watsonx.ai)
    src/
      config.py                    constantes (seção 8.1)
      preparar_dados.py            CSV → parquet (seção 6)
      treinar_modelo.py            modelo e métricas (seção 7)
      agente.py                    sinais, nota, decisão e explicação (seção 8)
      avaliar_agente.py            avaliação de março (seção 8.6)
      explicabilidade.py           o que pesou na nota
      fila.py                      fila de demonstração (seção 10)
      feedback.py                  respostas do analista (seção 10)
      avaliar_ia.py                IA contra modelo (Issue #46)
      api/                         API FastAPI (seção 12)
      auditoria/                   auditoria por IA (seção 13)
    web/                           site Next.js (seção 14)
    tests/                         pytest; test_conformidade_*.py são do líder
    modelos/                       sentinela.joblib e JSONs gerados pelos scripts
    docs/                          requisitos, arquitetura, decisões e backlog
    data/                          CSV comprimido, dicionário e parquet no Git; CSV e respostas fora

## 4. Dados de entrada

Arquivo: `data/case_transacoes_cartoes_sintetico_900k.csv` (CSV com vírgula e cabeçalho,
NÃO compactado, cerca de 294 MB; 160.000 linhas de dados; 297 colunas; dados 100%
sintéticos da Sicredi). Atenção: apesar do "900k" no nome e do arquivo de orientações,
o arquivo entregue pela Sicredi tem 160.000 linhas. Isso é esperado; não é erro.

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

Gerado por `python -m src.preparar_dados`. Uma linha por transação, todas as 160.000
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
    CAMINHO_CSV = RAIZ / "data" / "case_transacoes_cartoes_sintetico_900k.csv"
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
    OLLAMA_TIMEOUT_DISPONIBILIDADE_S = 2
    SEMENTE = 42
    INICIO_TREINO = "2025-01-01"; INICIO_TESTE = "2025-03-01"; FIM_TESTE = "2025-04-01"
    HORA_FIM_MADRUGADA = 5
    LIMIAR_VELOCIDADE_TERMINAL = 10
    LIMIAR_RAJADA_1MIN = 5
    LIMIAR_TOKEN_CARTEIRA = 30
    LIMIAR_DISTANCIA_KM = 100
    LIMIAR_VALOR_ALTO = 150
    LIMIAR_RISCO_ESTABELECIMENTO = 40
    TAMANHO_AMOSTRA_LEGITIMAS = 2000
    ROTULOS_DECISAO = {"BLOQUEAR": "Bloquear e enviar ao analista",
                       "PEDIR_CONFIRMACAO": "Pedir confirmação ao cliente",
                       "APROVAR": "Aprovar"}

As constantes a partir de OLLAMA_TIMEOUT_DISPONIBILIDADE_S foram acrescentadas na Issue #2
para tirar valores soltos do código. Os valores são os mesmos que já estavam no código.

### 8.2 Sinais de alerta (regras)

Função `calcular_sinais(transacao: dict) -> list[dict]`. Cada sinal devolvido é
`{"id": ..., "descricao": ...}`. Um sinal só dispara se o valor existir (valor vazio,
None ou NaN nunca dispara e nunca gera erro). Ordem fixa:

| id | Condição | descricao (preencher os valores) |
| --- | --- | --- |
| velocidade_terminal | vel_cartao_terminal_1h >= LIMIAR_VELOCIDADE_TERMINAL | "Cartão usado {v:.0f} vezes em terminais na última hora (normal: até 5)." |
| rajada_1min | qtd_transacoes_cartao_1min >= LIMIAR_RAJADA_1MIN | "{v:.0f} transações do cartão no último minuto (normal: 1 ou 2)." |
| token_carteira | qtd_token_carteira_3m >= LIMIAR_TOKEN_CARTEIRA | "Token de carteira digital usado {v:.0f} vezes em 3 meses (normal: até 14)." |
| salto_geografico | dist_terminal_anterior_km > LIMIAR_DISTANCIA_KM | "Terminal a {v:.0f} km do anterior em menos de uma hora." |
| madrugada | madrugada == 1 | "Compra feita de madrugada, às {hora:.0f}h." |
| valor_alto | valor > LIMIAR_VALOR_ALTO | "Valor de R$ {v:.2f}, acima do padrão (mediana das compras: R$ 35)." |
| credito_nao_presente | credito == 1 e nao_presente == 1 | "Compra no crédito sem cartão presente (online)." |
| ip_desconhecido | ip_pais_desconhecido == 1 | "Endereço IP de país desconhecido." |
| estabelecimento_risco | risco_estabelecimento >= LIMIAR_RISCO_ESTABELECIMENTO | "Estabelecimento com risco {v:.0f} (normal: abaixo de 37)." |

### 8.3 Decisão

Função `decidir(nota: float, sinais: list[dict]) -> str`, nesta ordem:
1. `"BLOQUEAR"` se nota >= NOTA_BLOQUEAR, ou se existir o sinal `ip_desconhecido`.
2. `"PEDIR_CONFIRMACAO"` se nota >= NOTA_CONFIRMAR, ou se a quantidade de sinais for
   >= MIN_SINAIS_CONFIRMAR.
3. `"APROVAR"` nos demais casos.

Textos legíveis: constante `ROTULOS_DECISAO` de `src/config.py` (seção 8.1), usada pelo
agente e pela interface. BLOQUEAR = "Bloquear e enviar ao analista"; PEDIR_CONFIRMACAO =
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

Função de módulo `granite_disponivel(timeout_s: float = OLLAMA_TIMEOUT_DISPONIBILIDADE_S) -> bool`:
faz GET em `{OLLAMA_URL}/api/tags` e devolve True só se a resposta tiver status 200; qualquer
`requests.RequestException` devolve False (registrado em log). A interface usa esta mesma
função para mostrar o estado do IBM Granite. Acrescentada na Issue #2.

Se `usar_llm` for True: primeiro chama `granite_disponivel()`. Se devolver False, usar o
texto de reserva. Se responder, fazer POST em
`{OLLAMA_URL}/api/generate` com timeout OLLAMA_TIMEOUT_S e o JSON:
`{"model": OLLAMA_MODELO, "prompt": PROMPT, "stream": false, "options": {"temperature": 0.2, "num_predict": 200}}`.
O texto vem no campo `"response"` do JSON de resposta. `requests.RequestException`, JSON
inválido (`ValueError`), campo ausente (`KeyError`), status diferente de 200 ou resposta vazia
levam ao texto de reserva, com registro em log. Nunca deixar o erro subir.

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

## 10. Fila de demonstração e respostas do analista

- A fila (`src/fila.py`, `montar_fila`) tem todas as fraudes de março de 2025 mais
  TAMANHO_AMOSTRA_LEGITIMAS transações legítimas de março sorteadas com `random_state=SEMENTE`,
  pontuadas com `analisar_lote` e ordenadas pela nota, da maior para a menor (ADR-007).
- A resposta do analista (`src/feedback.py`) é gravada em CAMINHO_FEEDBACK com as colunas
  `registrado_em, id_transacao, nota, decisao, resposta_analista`; `resposta_analista` só aceita
  "fraude" ou "legitima". Vale a última resposta de cada transação.
- As colunas `fraude` e `decisao_sistema_atual` nunca aparecem na API nem no site.

## 11. Critérios de aceite e invariantes (valores exatos, base de 160.000 linhas)

Se um número sair diferente, há erro: pare e investigue antes de continuar.
Os testes `tests/test_conformidade_nucleo.py` conferem todos os números abaixo automaticamente,
inclusive que os arquivos de `modelos/` saem do código atual (não foram editados à mão).

Etapa 1 (dados preparados):
- 160.000 linhas e 21 colunas no parquet.
- 146 fraudes (0,09%): 52 em janeiro, 40 em fevereiro, 54 em março de 2025 e zero de
  abril a dezembro.
- 96.287 débito e 63.713 crédito.
- 311 linhas com data_hora vazia (nenhuma delas é fraude).
- 38 linhas com ip_pais_desconhecido == 1, e as 38 são fraude.
- Cerca de 8% de vazios em vel_cartao_terminal_1h, qtd_transacoes_cartao_1min,
  qtd_token_carteira_3m, dist_terminal_anterior_km e risco_estabelecimento.

Etapa 2 (modelo):
- Treino: 25.923 linhas e 92 fraudes. Teste: 13.608 linhas e 54 fraudes.
- PR-AUC e ROC-AUC iguais ou acima de 0,99 (os dados são sintéticos e fáceis de separar;
  valores perto de 1,0 são esperados).
- Nos cortes 30, 50 e 70: 54 alertas e 54 fraudes detectadas (precisão 1,0 e recall 1,0).
- Sistema atual no teste: 26 bloqueadas, as 26 são fraude (28 fraudes não bloqueadas).
- Os três coeficientes mais fortes são de dist_terminal_anterior_km,
  qtd_transacoes_cartao_1min e vel_cartao_terminal_1h (em qualquer ordem).

Etapa 3 (agente):
- `pytest` passa todos os testes. Nota da transação FRAUDE de exemplo perto de 100; da
  LEGITIMA, perto de 0.
- avaliar_agente (março de 2025): 13.608 transações e 54 fraudes; Sentinela com 54
  bloqueadas (54 fraudes), 159 pedidos de confirmação (0 fraudes) e 13.395 aprovadas
  (0 fraudes). Sistema atual: 26 fraudes bloqueadas e 28 não bloqueadas.
  Uma diferença pequena (poucas unidades) em confirmações é aceitável; em fraudes, não.

Interface e entrega: critérios de cada Issue em `docs/backlog.md`. A fila tem 2.054
transações (54 fraudes de março + 2.000 legítimas).

Invariantes: depois de QUALQUER Issue, os números das Etapas 1, 2 e 3 acima continuam
iguais. Mudou um deles, alguma coisa quebrou.

## 12. API: `src/api/` (Issue #38; ADR-011)

O site e qualquer sistema externo (por exemplo, o autorizador de cartões) falam com o Sentinela
só por esta API. Ela é o contrato entre backend e site: nenhum campo muda sem uma Issue que mude
esta seção. Os testes `tests/test_conformidade_api.py` traduzem esta seção.

- Executar: `uvicorn src.api.app:app --port 8000`. O objeto FastAPI se chama `app` e fica em
  `src/api/app.py`. Dependências em `requirements.txt`.
- Na subida, a API carrega uma única vez o parquet, o agente (`AgenteSentinela` com `base`) e a
  fila de demonstração (`montar_fila(base, agente.analisar_lote)`, ADR-007). O modelo carrega
  sozinho: sem o parquet, `POST /api/analisar` continua funcionando (só precisa do modelo), e as
  rotas que dependem da base (fila, transação, auditoria de transação da fila e respostas)
  respondem 503 com a mensagem do que rodar. Sem o modelo, só `/api/saude` e `/api/metricas`
  respondem. A API sobe em todos os casos, e `/api/saude` informa o que falta (Issue #52).
- CORS liberado só para as origens de `API_ORIGENS_PERMITIDAS` em `src/config.py`
  (`["http://localhost:3000"]`).
- Campos em `snake_case`, em português, como no resto do projeto. Datas em texto ISO 8601 sem fuso
  (`"2025-03-03T00:17:00"`) ou `null`. Números vazios viram `null`, nunca `NaN`.
- Nenhuma resposta contém `fraude`, `decisao_sistema_atual`, colunas proibidas (seção 5) nem
  `id_cartao`, `id_cliente` ou `id_estabelecimento`.
- Erros: `{"detail": "<mensagem em português dizendo o que aconteceu e o que fazer>"}`; nunca stack
  trace. Validação inválida: 422.

### 12.1 Objetos

- **Analise:** `{"nota": float, "decisao": "APROVAR"|"PEDIR_CONFIRMACAO"|"BLOQUEAR",
  "decisao_legivel": str, "sinais": [{"id": str, "descricao": str}], "explicacao": str,
  "contribuicoes": [{"variavel": str, "nome": str, "contribuicao": float}], "latencia_ms": float}`.
  `nota`, `decisao`, `decisao_legivel` e `sinais` vêm de `calcular_sinais`, `pontuar` e `decidir`
  (iguais a `analisar`); `explicacao` é o texto de reserva da seção 8.5 (a API nunca chama o
  Ollama); `contribuicoes` vem de `src/explicabilidade.py` (Issue #41; lista vazia até lá);
  `latencia_ms` mede sinais + nota + decisão, sem a explicação.
- **ItemFila:** `{"id_transacao": int, "nota": float, "decisao": str, "valor": float|null,
  "data_hora": str|null, "tipo_transacao": str, "modalidade_transacao": str, "n_sinais": int}`.
- **Transacao:** `id_transacao`, `data_hora`, `valor`, `tipo_transacao`, `modalidade_transacao`
  e as 11 variáveis de `VARIAVEIS_MODELO`.
- **ItemHistorico:** `{"data_hora", "valor", "tipo_transacao", "modalidade_transacao",
  "dist_terminal_anterior_km"}`.
- **Resposta:** `{"id_transacao": int, "resposta": "fraude"|"legitima", "registrado_em": str}`.
- **PerfilAssociado** (Issue #64): o que é normal para o associado, calculado só com compras
  anteriores do mesmo cliente: `{"compras_anteriores": int, "mediana_valor": float|null,
  "valor_atual_sobre_mediana": float|null, "hora_mais_comum": int|null,
  "percentual_madrugada": float|null, "percentual_credito_nao_presente": float|null}`; `null`
  quando o cliente não tem compras anteriores. Reaproveita `perfil_do_cliente` de
  `src/auditoria/ferramentas.py`.
- **Relatorio** e **Auditoria:** seção 13.

### 12.2 Endpoints

| Método e caminho | Entrada | Saída (200, salvo indicação) |
| --- | --- | --- |
| `GET /api/saude` | — | `{"status": "ok", "modelo_carregado": bool, "dados_carregados": bool, "auditoria": "watsonx"\|"local"}` |
| `GET /api/fila` | `decisoes` (opcional, separadas por vírgula; padrão `BLOQUEAR,PEDIR_CONFIRMACAO`; valor inválido → 422) | `{"total_fila": int, "contagens": {"BLOQUEAR": int, "PEDIR_CONFIRMACAO": int, "APROVAR": int}, "itens": [ItemFila]}`, itens por nota decrescente; `contagens` e `total_fila` sempre da fila inteira |
| `GET /api/transacoes/{id_transacao}` | — | `{"transacao": Transacao, "analise": Analise, "historico": [ItemHistorico] (até 10, antes desta, mais recente primeiro), "resposta_analista": Resposta\|null, "perfil_associado": PerfilAssociado\|null, "notificacao": Notificacao\|null}`; fora da fila → 404. `perfil_associado` entra na Issue #64 e `notificacao` na #62 |
| `POST /api/analisar` | corpo com as 11 variáveis de `VARIAVEIS_MODELO` (todas opcionais, numéricas), `data_hora`, `valor`, `tipo_transacao`, `modalidade_transacao` opcionais e `auditar: bool = true` | `{"analise": Analise, "id_auditoria": str\|null, "id_notificacao": str\|null}`; responde sem esperar a auditoria; `id_notificacao` (Issue #62) só existe quando a decisão é PEDIR_CONFIRMACAO ou BLOQUEAR |
| `POST /api/transacoes/{id_transacao}/auditoria` | — | 202 `{"id_auditoria": str, "status": str}`; se já existe auditoria dessa transação, devolve a mesma; fora da fila → 404 |
| `GET /api/auditorias/{id_auditoria}` | — | Auditoria; desconhecida → 404 |
| `POST /api/respostas` | `{"id_transacao": int, "resposta": "fraude"\|"legitima"}` | 201 Resposta; grava com `src/feedback.py` em `CAMINHO_FEEDBACK` (seção 10); fora da fila → 404 |
| `GET /api/respostas` | — | `{"total": int, "fraudes": int, "legitimas": int, "concordancia": float\|null, "itens": [{"id_transacao", "resposta", "registrado_em", "decisao", "nota"}]}`; vale a última resposta de cada transação; concordância = fração de respostas em que "fraude" veio com BLOQUEAR, ou "legitima" com APROVAR ou PEDIR_CONFIRMACAO (1 casa, em %; `null` sem respostas) |
| `GET /api/metricas` | — | `{"metricas": obj, "avaliacao": obj, "extras": {"avaliacao_rigorosa": obj\|null, "custos": obj\|null, "eda": obj\|null, "ia_contra_modelo": obj\|null}}`, lidos de `modelos/`; sem `metricas.json` ou `avaliacao_agente.json` → 503 |

A auditoria roda em segundo plano (thread ou tarefa assíncrona), guardada em memória num
dicionário `id_auditoria → Auditoria`; reiniciar a API apaga as auditorias, e isso é aceitável no
protótipo.

## 13. Auditoria por IA: `src/auditoria/` (Issue #39; ADR-012 e ADR-013)

O modelo decide; a IA audita. A IA nunca muda a decisão, a nota nem os sinais: ela produz um
relatório para o analista, ao lado da decisão.

- Função pública `auditar(transacao: dict, analise: dict) -> dict` em `src/auditoria/__init__.py`.
  Nunca levanta exceção: qualquer falha do watsonx.ai cai no modo local, com registro em log.
- **Auditoria:** `{"id_auditoria": str, "status": "pendente"|"concluida"|"erro",
  "relatorio": Relatorio|null, "latencia_ms": float|null, "mensagem": str|null}`.
- **Relatorio:** `{"parecer": "CONFIRMA"|"DIVERGE"|"INCONCLUSIVO",
  "risco_ia": "BAIXO"|"SUSPEITO"|"ALTO"|null, "confianca": "BAIXA"|"MEDIA"|"ALTA",
  "explicacao": str, "evidencias_a_favor": [str], "evidencias_contra": [str],
  "dados_ausentes": [str], "ferramentas_usadas": [{"nome": str, "resumo": str}],
  "fonte": "watsonx"|"local", "modelo": str}`. `explicacao` em português, até 600 caracteres.
- **Parecer** (calculado em Python, nunca pelo LLM): `ALTO ↔ BLOQUEAR`,
  `SUSPEITO ↔ PEDIR_CONFIRMACAO`, `BAIXO ↔ APROVAR`. `risco_ia` nulo ou `confianca` BAIXA →
  INCONCLUSIVO; risco correspondente à decisão do modelo → CONFIRMA; senão → DIVERGE.
- **Ferramentas** (funções Python sobre o parquet carregado; só dados anteriores à transação):
  `sinais_da_transacao`, `contribuicoes_da_nota`, `historico_do_cartao` (agregados das últimas
  10), `perfil_do_cliente` (quantidade, mediana de valor, % de madrugada, % de crédito sem cartão
  presente) e `perfil_do_estabelecimento` (quantidade, mediana de valor, risco). Cada uma devolve
  `{"status": "ok"|"sem_dados", "dados": obj, "campos_ausentes": [str]}`. Nenhuma devolve rótulo,
  `decisao_sistema_atual`, coluna proibida ou identificador.
- **watsonx.ai:** credenciais só por variáveis de ambiente (`WATSONX_APIKEY`,
  `WATSONX_PROJECT_ID`, `WATSONX_URL`, `WATSONX_MODELO`), lidas de um `.env` fora do Git;
  `.env.example` lista os nomes sem valores. Chamadas com `requests` (sem biblioteca nova): token
  IAM em `https://iam.cloud.ibm.com/identity/token`, guardado até expirar, e o endpoint de chat
  com ferramentas do watsonx.ai. Limites em `src/config.py`: `AUDITORIA_MAX_ITERACOES = 6` e
  `AUDITORIA_TIMEOUT_S = 30`. A resposta final do modelo é um JSON validado contra o Relatorio;
  inválido → uma nova tentativa pedindo o JSON; inválido de novo → modo local.
- **Instruções ao modelo (resumo obrigatório):** é auditor de prevenção a fraudes de uma
  cooperativa; escreve em português; usa as ferramentas antes de concluir; só afirma o que as
  ferramentas mostraram; lista o que faltou; responde INCONCLUSIVO (`risco_ia` nulo ou confiança
  BAIXA) quando a evidência é insuficiente ou contraditória; nunca recomenda bloquear ou liberar
  por conta própria.
- **Modo local** (sem credenciais, sem resposta ou JSON inválido): roda as mesmas ferramentas e
  decide `risco_ia` por regra independente da nota: IP de país desconhecido ou 4 sinais ou mais →
  ALTO; 2 ou 3 sinais → SUSPEITO; 0 ou 1 → BAIXO; `confianca` MEDIA; `fonte` "local"
  (`AUDITORIA_SINAIS_RISCO_ALTO` e `AUDITORIA_SINAIS_SUSPEITO` em `src/config.py`). Medido na fila
  de demonstração em 13/11: concorda com o modelo em 88,4% das transações e diverge só em
  aprovações com 2 ou 3 sinais (a regra anterior, com 1 sinal já suspeito, concordava em 47,5%).
- **Privacidade:** ao watsonx.ai só vão as variáveis da transação e os agregados das ferramentas,
  nunca identificadores. O log nunca registra a chave nem o conteúdo das respostas do modelo.

## 14. Site: `web/` (ADR-011 e ADR-014)

- Next.js (App Router) com TypeScript estrito e o Carbon Design System da IBM (`@carbon/react`),
  em `web/`. Rotas: `/` (Fila de alertas), `/desempenho`, `/como-funciona`, `/simulador`,
  `/respostas`.
- Textos de tela em `web/lib/textos.ts`; formatação pt-BR em `web/lib/formatacao.ts` (moeda
  "R$ 1.234,50", nota "97,3", percentual "48,1%", data "03/03/2025 00:17", vazio → "—"); tipos
  em `web/lib/tipos.ts`, espelho exato da seção 12; cliente em `web/lib/api.ts`, com a URL de
  `NEXT_PUBLIC_API_URL` (padrão `http://localhost:8000`). Com `NEXT_PUBLIC_USAR_MOCK=1`, o cliente
  usa dados inventados de `web/lib/mocks/`, no mesmo formato, para o site funcionar sem a API.
- A auditoria é consultada a cada 2 s, por até 60 s; depois disso o painel diz que a auditoria
  demorou e oferece tentar de novo. A decisão do modelo aparece antes, sem esperar a IA.
- Portão do site, dentro de `web/`: `npm run lint`, `npm run typecheck`, `npm test` (Vitest) e
  `npm run build`, todos sem erro; o CI roda os quatro.
- Acessibilidade WCAG 2.2 AA (os componentes do Carbon já ajudam): contraste, foco visível, rótulos
  em todos os controles, nada que dependa só de cor. Nunca exibir `fraude` nem
  `decisao_sistema_atual`.

## 15. Canal do associado: `src/associado/` (Issues #62, #63 e #65; ADR-015)

O agente não só decide: ele age. Quando a decisão é PEDIR_CONFIRMACAO ou BLOQUEAR, o Sentinela
avisa o associado e registra a resposta dele. É uma simulação: nada é enviado por SMS ou push de
verdade; o "App do associado" do site faz o papel do celular.

- **Notificacao:** `{"id_notificacao": str, "id_transacao": int|null, "tipo":
  "CONFIRMACAO"|"AVISO_BLOQUEIO", "mensagem": str, "fonte_mensagem": "watsonx"|"modelo",
  "criada_em": str, "status": "aguardando"|"confirmada"|"negada", "respondida_em": str|null,
  "resultado": str|null}`. Guardada em memória, como as auditorias.
- **Regras de negócio:**
  - PEDIR_CONFIRMACAO → `tipo` CONFIRMACAO. Resposta "sim" → `status` confirmada,
    `resultado` "Compra liberada pelo associado."; "nao" → `status` negada, `resultado`
    "Compra bloqueada e cartão protegido. O caso foi para o analista."
  - BLOQUEAR → `tipo` AVISO_BLOQUEIO. A compra continua bloqueada em qualquer caso. Resposta
    "sim" → confirmada, `resultado` "O associado diz que fez a compra; a liberação depende do
    analista."; "nao" → negada, `resultado` "O associado não reconhece a compra: fraude provável."
  - APROVAR não gera notificação. Uma notificação respondida não aceita nova resposta.
- **Mensagem** (`redigir_mensagem(transacao, analise) -> tuple[str, str]`, devolve texto e
  fonte): com credenciais do watsonx.ai (Issue #65), o Granite redige; senão, ou se a mensagem
  dele for recusada, usa o modelo fixo (fonte "modelo"):
  - CONFIRMACAO: "Sicredi: compra de {valor} em {data} às {hora} no seu cartão de {tipo}. Foi
    você? Responda no app."
  - AVISO_BLOQUEIO: "Sicredi: bloqueamos uma compra de {valor} em {data} às {hora} por segurança.
    Seu cartão está protegido. Foi você? Responda no app."
  - Valor com `formatar_moeda` pt-BR ("R$ 341,79"); data "dd/mm"; sem data, omite "em … às …".
- **Regras contra golpe (validadas em toda mensagem, inclusive a do modelo fixo):** começa com
  "Sicredi:"; até 160 caracteres; sem link ("http", "www", ".com"); sem pedir senha, código,
  token ou dados do cartão; sem sequência de 4 dígitos ou mais fora do valor; nenhum
  identificador. Mensagem do Granite que quebra uma regra é trocada pelo modelo fixo.
- **Mensagem pelo Granite (Issue #65):** o Granite recebe só valor, data, hora, tipo do cartão e a
  situação (nunca identificadores). Além das regras contra golpe, o texto dele só é aceito se
  todo valor, data e hora citados forem os da compra e, num AVISO_BLOQUEIO, se disser que a compra
  foi bloqueada. Para não atrasar a decisão, a notificação nasce com o modelo fixo e o texto do
  Granite a substitui em segundo plano (`fonte_mensagem` passa a "watsonx") enquanto o status
  ainda é "aguardando".
- **Endpoints:**

| Método e caminho | Entrada | Saída |
| --- | --- | --- |
| `POST /api/transacoes/{id_transacao}/notificacao` | — | 201 Notificacao (200 com a mesma, se já existe); fora da fila → 404; decisão APROVAR → 422 |
| `GET /api/notificacoes` | — | `{"itens": [Notificacao]}`, da mais recente para a mais antiga |
| `GET /api/notificacoes/{id_notificacao}` | — | Notificacao; desconhecida → 404 |
| `POST /api/notificacoes/{id_notificacao}/resposta` | `{"resposta": "sim"\|"nao"}` | 200 Notificacao atualizada; já respondida → 409; desconhecida → 404; valor inválido → 422 |

- `POST /api/analisar` cria a notificação automaticamente quando a decisão é PEDIR_CONFIRMACAO
  ou BLOQUEAR (com `id_transacao` null) e devolve o `id_notificacao`.
- `GET /api/transacoes/{id}` devolve a notificação da transação, se existir, em `notificacao`.

## 16. "Pergunte à IA sobre este caso": extra (Issue #66)

- `POST /api/transacoes/{id_transacao}/perguntas` com `{"pergunta": str}` (1 a 300
  caracteres; fora disso → 422; fora da fila → 404) → 200 `{"resposta": str, "ferramentas_usadas":
  [{"nome": str, "resumo": str}], "fonte": "watsonx"|"local", "latencia_ms": float}`.
- Com credenciais, o Granite responde em português usando as mesmas 5 ferramentas da auditoria
  (seção 13), com os mesmos limites de iterações e tempo, e só afirma o que as ferramentas
  mostraram. Sem credenciais (modo local), a resposta lista o resumo de cada ferramenta e diz
  que a IA está indisponível.
- A resposta nunca traz identificador, rótulo ou decisão do sistema atual.

## 17. Associado e filial (refatoração; Issues #90 a #101)

O site passa a ter duas áreas: a do **associado** (celular), que vê saldo, extrato, simula compras
e responde aos avisos, e a da **filial** (desktop), em que o auditor revisa a fila da agência e o
gerente acompanha as métricas. O núcleo (seções 6 a 11) não muda: BLOQUEAR bloqueia na hora e
PEDIR_CONFIRMACAO espera o associado. As rotas das seções 12 a 16 continuam iguais. Os testes
`tests/test_contrato_refatoracao.py` traduzem esta seção; cada teste fica pulado até a rota
existir.

### 17.1 Regras gerais

- **Arquitetura.** As regras ficam em `src/dominio/` e `src/aplicacao/` e dependem só das
  interfaces de `src/portas/`. O armazenamento de hoje é `src/adaptadores/memoria/`; o único lugar
  que escolhe o adaptador é `src/composicao.py`. As rotas ficam em `src/api/sessao.py`,
  `src/api/rotas_associado.py` e `src/api/rotas_filial.py`, incluídas em `src/api/app.py`.
- **Dados fictícios.** Nomes, saldos, limites, filiais e funcionários são inventados (17.2). Cada
  associado com login é ligado a um cliente real de março, para ter extrato e histórico. Nenhuma
  resposta contém `id_cartao`, `id_cliente`, `id_estabelecimento` nem `id_transacao` da base: as
  rotas novas usam identificadores opacos (`cmp-000123`, `car-01`, `asc-01`).
- **Carteiras.** Os clientes com compra em março, ordenados pelo identificador, são divididos por
  posição: posição par vai para a Agência Centro, ímpar para a Agência Norte. Cliente sem login
  aparece na filial como "Associado NNNN" (posição com 4 dígitos).
- **Situação de uma compra.** `APROVADA`, `AGUARDANDO`, `BLOQUEADA` ou `CONTESTADA`. Ao nascer:
  APROVAR → `APROVADA`; PEDIR_CONFIRMACAO → `AGUARDANDO`; BLOQUEAR → `BLOQUEADA`. A resposta do
  associado ao aviso (seção 15) muda a situação: numa `AGUARDANDO`, "sim" → `APROVADA` e "nao" →
  `BLOQUEADA`; numa `BLOQUEADA` pelo Sentinela, a situação não muda (o analista decide, como hoje).
  "Não reconheço esta compra" muda uma `APROVADA` para `CONTESTADA`.
- **Saldo e limite.** Só as compras simuladas mexem neles; as de março já estão no saldo inicial.
  Compra no débito que vira `APROVADA` desconta o saldo; no crédito, consome o limite disponível.
  `AGUARDANDO` e `BLOQUEADA` não mexem. Contestação devolve o valor ao saldo ou ao limite.
- **Cartões.** Cada associado tem um cartão de débito e um de crédito. As compras de março vão
  para o cartão do mesmo tipo. Contestação bloqueia o cartão da compra; cartão bloqueado não
  aceita compra nova (409).
- **Avisos.** Compra simulada que vira `AGUARDANDO` ou `BLOQUEADA` cria o aviso da seção 15. Na
  subida, as compras de março dos associados com login que estão `AGUARDANDO` ou `BLOQUEADA`
  também ganham aviso, com status "aguardando".
- **O que cada um vê.** O associado vê só as próprias compras, com motivo genérico (17.3), e nunca
  sinais, nota, contribuições ou parecer da IA. O auditor e o gerente veem só a carteira da
  própria filial, com o detalhe técnico, o nome abreviado do associado ("Ana S.") e o final do
  cartão; nunca saldo, limite, extrato ou nome completo do associado.
- **Sessão simulada.** Não há senha. `POST /api/sessao` devolve um `token` (texto opaco, guardado
  em memória); as outras rotas desta seção exigem o cabeçalho `X-Sessao: <token>`. Sem cabeçalho
  ou com token desconhecido → 401; papel sem acesso à rota → 403. O CORS (seção 12) passa a
  aceitar o cabeçalho `X-Sessao`.
- **Erros** como na seção 12: `{"detail": "<mensagem em português>"}`. Recurso de outro associado
  → 404 (não revela que existe); recurso de outra filial → 403.

### 17.2 Dados de demonstração

| Filial | `id_filial` | Gerente | Auditores |
| --- | --- | --- | --- |
| Agência Centro | `fil-centro` | Helena Castro (`ger-01`) | Rafael Moura (`aud-01`), Júlia Prates (`aud-02`) |
| Agência Norte | `fil-norte` | Marcos Viana (`ger-02`) | Tiago Nunes (`aud-03`), Paula Reis (`aud-04`) |

Associados com login: os 10 clientes de março com mais compras (desempate pelo identificador),
alternando Centro e Norte a partir do primeiro. Nomes, na ordem em que entram: Ana Souza, Carlos
Lima, Bruno Teixeira, Fernanda Alves, Carla Mendes, Gustavo Pires, Diego Prado, Isabela Costa,
Elisa Rocha e João Martins (`asc-01` a `asc-10`; posição `p` de 0 a 9). Saldo inicial:
R$ 4.820,35 − R$ 310,00 × `p` (Ana R$ 4.820,35; Carlos R$ 4.510,35). Limite total de crédito
R$ 3.000,00 e disponível R$ 2.150,00 para todos. Finais de cartão, com 4 dígitos: débito
`1111 + 111 × p` e crédito `4821 + 7 × p` (Ana: débito 1111, crédito 4821). Ids dos cartões:
`car-NN-d` e `car-NN-c`, com `NN` = `p + 1` em 2 dígitos.

### 17.3 Objetos

- **Perfil:** `{"id_perfil": str, "nome": str, "papel": "associado"|"auditor"|"gerente",
  "filial": {"id_filial": str, "nome": str}}`.
- **Cartao:** `{"id": str, "tipo": "debito"|"credito", "final": str, "bloqueado": bool}`.
- **CompraExtrato:** `{"id_compra": str, "estabelecimento": str, "data_hora": str|null,
  "valor": float|null, "tipo_transacao": str, "modalidade_transacao": str, "final_cartao": str,
  "situacao": "APROVADA"|"AGUARDANDO"|"BLOQUEADA"|"CONTESTADA", "id_notificacao": str|null,
  "simulada": bool}`. `estabelecimento` das compras de março é um nome fictício escolhido pelo
  risco do estabelecimento (lista fixa no adaptador); o das simuladas é o informado.
- **Bloqueio:** `{"por": str, "em": str, "motivo": str}`. Para o associado, `por` é "Sentinela" ou
  "Analista da agência <nome da agência>" e `motivo` é sempre "A compra fugiu do seu padrão de uso
  e foi bloqueada por segurança." Para a filial, `por` é "Sentinela" ou o nome completo do auditor
  e `motivo` é a explicação do modelo (seção 8.5), mais a nota do auditor quando houver.
- **RespostaAssociado:** `{"resposta": "sim"|"nao", "em": str}`.
- **ItemFilaFilial:** `{"id_compra": str, "nota": float, "decisao": str, "associado": str,
  "final_cartao": str, "data_hora": str|null, "valor": float|null, "tipo_transacao": str,
  "modalidade_transacao": str, "situacao": str, "veredito_ia": "CONFIRMA"|"DIVERGE"|
  "INCONCLUSIVO"|null}`. `associado` é o nome abreviado; `veredito_ia` é o parecer da última
  auditoria concluída (seção 13), ou `null`.

### 17.4 Endpoints

| Método e caminho | Papel | Entrada | Saída (200, salvo indicação) |
| --- | --- | --- | --- |
| `GET /api/sessao/perfis` | — | — | `{"perfis": [Perfil]}`: 2 gerentes, 4 auditores e 10 associados |
| `POST /api/sessao` | — | `{"id_perfil": str}` | `{"token": str, "perfil": Perfil}`; perfil desconhecido → 404 |
| `GET /api/associado/inicio` | associado | — | `{"associado": {"nome": str, "filial": str}, "saldo": float, "limite_total": float, "limite_disponivel": float, "cartoes": [Cartao], "pendentes": [{"id_notificacao": str, "id_compra": str, "valor": float\|null, "data_hora": str\|null}], "ultimas_compras": [CompraExtrato]}` (3 mais recentes) |
| `GET /api/associado/extrato` | associado | `situacao` (opcional, separadas por vírgula; inválida → 422) | `{"total": int, "itens": [CompraExtrato]}`, da mais recente para a mais antiga; as simuladas primeiro, na ordem em que foram feitas |
| `GET /api/associado/compras/{id_compra}` | associado | — | CompraExtrato + `{"bloqueio": Bloqueio\|null, "resposta_associado": RespostaAssociado\|null, "pode_contestar": bool}`; de outro associado → 404 |
| `POST /api/associado/compras` | associado | `{"cartao": str, "estabelecimento": str (1 a 60 caracteres), "data_hora": str}` + as variáveis de `POST /api/analisar` (seção 12), exceto `credito`, `tipo_transacao` e `auditar` | 201 `{"compra": CompraExtrato, "id_notificacao": str\|null}`; cartão de outro associado → 404; cartão bloqueado → 409 |
| `POST /api/associado/compras/{id_compra}/contestacao` | associado | — | 201 `{"compra": CompraExtrato, "cartao": Cartao}` (cartão bloqueado); situação diferente de `APROVADA` → 409 |
| `GET /api/filial/fila` | auditor, gerente | `situacao` (opcional; padrão `BLOQUEADA,AGUARDANDO,CONTESTADA`; inválida → 422) | `{"filial": {"id_filial": str, "nome": str}, "total": int, "itens": [ItemFilaFilial]}`, por nota decrescente |
| `GET /api/filial/compras/{id_compra}` | auditor, gerente | — | `{"compra": ItemFilaFilial, "analise": Analise (seção 12), "auditoria": Auditoria\|null (seção 13), "associado": {"nome_abreviado": str, "final_cartao": str, "historico": {"compras_90d": int, "valor_mediano": float\|null, "contestacoes": int}}, "resposta_associado": RespostaAssociado\|null, "bloqueio": Bloqueio\|null}`; de outra filial → 403 |
| `GET /api/filial/metricas` | gerente | — | `{"filial": {"id_filial", "nome"}, "periodo": "2025-03", "totais": {"compras": int, "aprovadas": int, "confirmacoes": int, "bloqueadas": int, "valor_protegido": float}, "por_tipo": [{"tipo_transacao": str, "modalidade_transacao": str, "aprovadas": int, "confirmacoes": int, "bloqueadas": int}], "acerto_modelo": {"alertas_certos": int, "alertas_desnecessarios": int, "sem_resposta": int, "taxa": float\|null}, "fraudes_aprovadas": {"total": int, "itens": [{"associado": str, "final_cartao": str, "data_hora": str\|null, "valor": float\|null}]}, "tempo_resposta_mediano_s": float\|null}` |

Notas sobre as rotas:

- Na compra simulada, `credito` e `tipo_transacao` vêm do tipo do cartão; `hora` e `madrugada`,
  quando ausentes, vêm de `data_hora`. O site manda `data_hora` com a data `2025-03-31` e a hora
  escolhida. A compra passa por `servicos.analisar_transacao` (o mesmo de `POST /api/analisar`) e
  dispara a auditoria por IA em segundo plano.
- `GET /api/filial/compras/{id}` dispara a auditoria por IA se ela ainda não existe, como hoje
  faz o painel; o site acompanha por `GET /api/auditorias/{id_auditoria}` (`auditoria.id_auditoria`).
- `totais` soma as compras de março da carteira e as simuladas. Somando as duas filiais, sem
  compras simuladas, os números de março são os da seção 11 (13.395 aprovadas, 159 confirmações e
  54 bloqueadas). `valor_protegido` é a soma das bloqueadas.
- `acerto_modelo`: entre os avisos da carteira, "nao" conta em `alertas_certos`, "sim" em
  `alertas_desnecessarios` e o resto em `sem_resposta`; `taxa` = certos ÷ (certos +
  desnecessários), em %, 1 casa, ou `null` sem respostas.
- `fraudes_aprovadas` são as compras contestadas da carteira.
- `tempo_resposta_mediano_s` é a mediana, em segundos, entre `criada_em` e `respondida_em` dos
  avisos respondidos da carteira; `null` sem respostas.

### 17.5 Prioridade 2 e 3 (contrato a fechar nas Issues)

- `POST /api/filial/compras/{id_compra}/bloqueio` (auditor bloqueia compra `AGUARDANDO`, Issue
  #102) e `bloqueios_por_auditor` nas métricas (Issue #104).
- `POST /api/associado/chat` e `POST /api/associado/chat/gerente` (Issue #105).
