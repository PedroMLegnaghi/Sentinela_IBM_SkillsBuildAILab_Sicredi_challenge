# ESPECIFICACAO.md — Projeto Sentinela (Desafio Sicredi, IBM SkillsBuild AI Lab)

Versão 4 (12/11/2026; testes de conformidade). Este arquivo define O QUE o sistema faz: dados, modelo, agente e
números esperados. COMO trabalhar (Git, convenções, testes, revisão) está no `AGENTS.md`.
A interface está em `docs/08-design-da-interface.md` e as tarefas em `docs/backlog.md`.
Quem escreve o código é o IBM Bob. Não invente colunas, arquivos, bibliotecas ou números que
não estejam aqui. Se um pedido conflitar com este arquivo, pare e pergunte.

## 1. Objetivo

Sentinela é um agente de IA para prevenção a fraudes em transações de cartão. Para cada
transação ele: (1) calcula sinais de alerta por regras; (2) dá uma nota de risco de 0 a
100 com um modelo de machine learning; (3) decide entre APROVAR, PEDIR_CONFIRMACAO ou
BLOQUEAR; (4) explica a decisão em português para um analista humano, usando o modelo
IBM Granite local (Ollama), com texto automático de reserva; (5) registra a resposta do
analista para retreino futuro.

## 2. Regras gerais

- Python 3.11 ou mais novo. Bibliotecas de execução em `requirements.txt`, com versão fixada
  (`pacote==versão`): pandas, pyarrow, scikit-learn, joblib, streamlit, requests, pytest.
  Ferramentas de desenvolvimento em `requirements-dev.txt`: black, ruff. Nenhuma outra.
  Adicionar biblioteca exige ADR em `docs/07-decisoes.md` e aprovação do líder.
- Convenções de código, idioma, testes, erros, Git e revisão: ver `AGENTS.md`.
- Caminhos sempre com pathlib, relativos à raiz do repositório (RAIZ = pasta que contém
  este arquivo). O código deve funcionar em Windows, macOS e Linux.
- Arquivos de texto sempre com encoding="utf-8".
- Toda aleatoriedade usa a semente 42 (constante SEMENTE).
- `src/` é um pacote (tem `__init__.py`). Scripts são executados da raiz com
  `python -m src.nome_do_modulo`. Existe um `conftest.py` vazio na raiz para o pytest.
- A pasta `data/` nunca vai para o Git. A pasta `modelos/` vai.

## 3. Estrutura de pastas (exata)

    AGENTS.md                         regras de trabalho do Bob
    ESPECIFICACAO.md                  este arquivo
    README.md
    requirements.txt                  dependências de execução, versões fixadas
    requirements-dev.txt              black e ruff
    pyproject.toml                    configuração de Black, Ruff e pytest
    .gitignore
    .bobignore                        impede o Bob de ler data/ e binários
    conftest.py
    app.py                            ponto de entrada da interface (navegação)
    .streamlit/config.toml            tema da interface (tokens de cor e fonte)
    .github/pull_request_template.md
    .github/workflows/qualidade.yml   Black, Ruff e pytest a cada Pull Request
    src/__init__.py
    src/config.py
    src/preparar_dados.py
    src/treinar_modelo.py
    src/agente.py
    src/avaliar_agente.py
    src/interface/__init__.py
    src/interface/tema.py             rótulos, ícones e cores de cada decisão
    src/interface/textos.py           todos os textos da tela
    src/interface/formatacao.py       formatação pt-BR (moeda, data, nota, percentual)
    src/interface/dados.py            carga em cache, fila e verificação do Granite
    src/interface/feedback.py         gravação e leitura das respostas do analista
    src/interface/pagina_fila.py
    src/interface/pagina_desempenho.py
    src/interface/pagina_como_funciona.py
    tests/test_agente.py
    tests/test_formatacao.py
    tests/test_feedback.py
    tests/test_fila.py
    tests/test_app.py                 teste de fumaça da interface (pula sem dados)
    tests/test_conformidade_nucleo.py     do líder: confere as seções 2 a 11 (não editar)
    tests/test_conformidade_interface.py  do líder: confere o design da interface (não editar)
    docs/                             requisitos, histórias, fluxos, arquitetura, ADRs, design, backlog
    modelos/sentinela.joblib
    modelos/metricas.json
    modelos/avaliacao_agente.json
    data/case_transacoes_cartoes_sintetico_900k.csv   (não versionado)
    data/transacoes_preparadas.parquet                 (não versionado)
    data/feedback.csv                                  (não versionado)

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

## 10. Interface

Toda a interface está especificada em `docs/08-design-da-interface.md`: páginas, layout,
componentes, textos, estados, tokens de tema e acessibilidade. Os módulos estão na seção 3.
Resumo das regras que dependem desta especificação:
- A fila de demonstração tem todas as fraudes de março de 2025 mais TAMANHO_AMOSTRA_LEGITIMAS
  transações legítimas de março sorteadas com `random_state=SEMENTE`, pontuadas com
  `analisar_lote` e ordenadas pela nota, da maior para a menor (ADR-007).
- A resposta do analista é gravada em CAMINHO_FEEDBACK com as colunas
  `registrado_em, id_transacao, nota, decisao, resposta_analista`; `resposta_analista` só
  aceita "fraude" ou "legitima". Vale a última resposta de cada transação.
- As colunas `fraude` e `decisao_sistema_atual` nunca aparecem na fila nem no painel.

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
