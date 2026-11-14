# Privacidade e experiência do associado

## O que o Sentinela lê

O modelo usa apenas 11 variáveis comportamentais e operacionais, sem nenhum dado pessoal
identificável:

| Variável | Descrição |
| --- | --- |
| `valor` | Valor da compra em reais |
| `hora` | Hora do dia (0 a 23) |
| `madrugada` | 1 se a compra foi antes das 5h |
| `credito` | 1 se o tipo de transação é crédito |
| `nao_presente` | 1 se o cartão não estava fisicamente presente |
| `ip_pais_desconhecido` | 1 se o IP não tem país identificado (código ZZ) |
| `vel_cartao_terminal_1h` | Uso do cartão em terminais na última hora |
| `qtd_transacoes_cartao_1min` | Transações do cartão no último minuto |
| `qtd_token_carteira_3m` | Uso do token de carteira digital nos últimos 3 meses |
| `dist_terminal_anterior_km` | Distância do terminal anterior em km |
| `risco_estabelecimento` | Risco do estabelecimento (0 a 100) |

Os dados preparados guardam ainda `tipo_transacao`, `modalidade_transacao`, `data_hora` e `mcc`,
usados para derivar variáveis, calcular os sinais e exibir a compra; eles não entram na nota como
variáveis próprias.

## O que o Sentinela nunca lê

As colunas abaixo não entram no modelo nem nas regras, porque entregariam a resposta (vazamento
de informação) ou porque são dados pessoais que não devem ser processados:

- **Scores prontos:** `fraud_score`, `visa_fraud_score`, `mc_fraud_score` — dariam a resposta
  diretamente.
- **Decisão do sistema atual:** `decision`, `transaction_status`, `action_code`, `reason_code` —
  são o resultado, não a entrada.
- **Disputas e fraudes declaradas:** `fraud`, `alert_id`, `dispute_*`, `fdz_*`, `oob_*` — só
  existem depois do evento.
- **Identificadores:** `id_cartao`, `id_cliente` e `id_estabelecimento` servem só para agrupar o
  histórico do cartão, do cliente e do estabelecimento; nunca aparecem nas respostas da API, nos
  logs nem nas mensagens enviadas à IA.

## O que vai para o IBM watsonx.ai

Quando a IA audita uma compra, ela recebe apenas:

- Os dados da própria compra: valor, data e hora, tipo e modalidade
- Os 9 sinais de alerta calculados (booleanos e valores agregados)
- As contribuições de cada variável para a nota
- O histórico de compras do cartão (agregados das últimas 10 — sem identificadores)
- O perfil comportamental do cliente (mediana de valor, percentual de madrugada — sem nome nem id)
- O perfil do estabelecimento (quantidade de compras anteriores, mediana de valor e a nota de
  risco de 0 a 100 já presente na compra — sem razão social nem id)

Nenhuma ferramenta devolve o rótulo de fraude nem a decisão do sistema atual.

Nenhum identificador de cartão, cliente ou estabelecimento é enviado ao watsonx.ai.

## Regras contra golpe na mensagem ao associado

Toda mensagem enviada ao associado (incluindo as geradas pelo Granite) é validada contra as
seguintes regras antes de chegar ao celular:

1. Começa com "Sicredi:" — identifica a origem.
2. Até 160 caracteres — cabe num SMS.
3. Sem link ("http", "www", ".com") — impede phishing.
4. Sem pedir senha, código, token ou dados do cartão — impede engenharia social.
5. Sem sequência de 4 dígitos ou mais fora do valor monetário — impede exposição de número de
   cartão.
6. Sem identificador de cartão, cliente ou estabelecimento — privacidade.

Se o Granite gerar uma mensagem que quebre qualquer regra, ela é descartada e o modelo fixo é
usado no lugar.

## Experiência do associado em março de 2025

Base: 13.608 compras de março (dados sintéticos), 54 fraudes.

| Indicador | Valor |
| --- | --- |
| Compras legítimas bloqueadas | **0** |
| Pedidos de confirmação enviados | **159** |
| Pedidos de confirmação como % das compras | 1,2% |
| Fraudes bloqueadas | 54 de 54 (100%) |

O Sentinela pediu confirmação em 159 compras de 13.608 (1,2% das transações de março) e não
bloqueou nenhuma compra legítima. Os números acima são calculados pelo script
`python -m src.avaliar_agente` e gravados em `modelos/avaliacao_agente.json`.
