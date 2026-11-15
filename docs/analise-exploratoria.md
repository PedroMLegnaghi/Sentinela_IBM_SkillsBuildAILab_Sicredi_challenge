# Análise Exploratória dos Dados — Projeto Sentinela

Documento gerado automaticamente por `python -m src.analisar_dados`. Dados 100% sintéticos (Sicredi / IBM SkillsBuild). Nunca contém identificadores de cartão, cliente ou estabelecimento.

## Visão geral

A base contém **160,000 transações** com **146 fraudes** (0.09% de taxa de fraude). O rótulo utilizado é `feedback_label` (coluna `fraude` no parquet); a coluna `fraud` foi descartada por conter erros sistemáticos.

## Distribuição por mês

| Mês | Transações | Fraudes | % Fraude |
| --- | --- | --- | --- |
| 2025-01 | 13,658 | 52 | 0.38% |
| 2025-02 | 12,265 | 40 | 0.33% |
| 2025-03 | 13,608 | 54 | 0.40% |
| 2025-04 | 13,125 | 0 | 0.00% |
| 2025-05 | 13,300 | 0 | 0.00% |
| 2025-06 | 13,085 | 0 | 0.00% |
| 2025-07 | 13,639 | 0 | 0.00% |
| 2025-08 | 13,568 | 0 | 0.00% |
| 2025-09 | 13,155 | 0 | 0.00% |
| 2025-10 | 13,581 | 0 | 0.00% |
| 2025-11 | 13,181 | 0 | 0.00% |
| 2025-12 | 13,524 | 0 | 0.00% |

As fraudes estão concentradas entre janeiro e março de 2025, período de treino e teste do modelo. Meses fora desse intervalo têm zero fraudes, o que é esperado nos dados sintéticos. A taxa de fraude mais alta está em março, o mês de teste.

## Distribuição por tipo de transação

| Tipo | Transações | Fraudes | % Fraude |
| --- | --- | --- | --- |
| credito | 63,713 | 124 | 0.19% |
| debito | 96,287 | 22 | 0.02% |

Transações de crédito apresentam taxa de fraude significativamente maior que as de débito. Isso justifica o sinal `credito_nao_presente` no modelo. A maioria das transações legítimas é de débito.

## Distribuição por modalidade

| Modalidade | Transações | Fraudes | % Fraude |
| --- | --- | --- | --- |
| cartao_nao_presente | 57,805 | 135 | 0.23% |
| cartao_presente | 102,195 | 11 | 0.01% |

Compras sem cartão presente (online) concentram a maior parte das fraudes. Combinado com crédito, esse padrão é o sinal mais discriminante. O modelo captura essa interação com o indicador `nao_presente`.

## Estatísticas por variável do modelo

| Variável | % Vazios | Mediana (fraude) | P10 (fraude) | P90 (fraude) | Mediana (legítima) | P10 (legítima) | P90 (legítima) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| valor | 0.4% | 190.345 | 59.645 | 589.32 | 34.77 | 9.03 | 132.722 |
| hora | 0.2% | 2.0 | 0.0 | 4.0 | 11.0 | 2.0 | 21.0 |
| madrugada | 0.0% | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 1.0 |
| credito | 0.0% | 1.0 | 0.0 | 1.0 | 0.0 | 0.0 | 1.0 |
| nao_presente | 0.0% | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 1.0 |
| ip_pais_desconhecido | 0.0% | 0.0 | 0.0 | 1.0 | 0.0 | 0.0 | 0.0 |
| vel_cartao_terminal_1h | 8.0% | 47.0 | 26.0 | 69.0 | 2.0 | 1.0 | 3.0 |
| qtd_transacoes_cartao_1min | 8.1% | 17.0 | 8.0 | 29.0 | 1.0 | 1.0 | 2.0 |
| qtd_token_carteira_3m | 8.0% | 80.0 | 48.4 | 116.0 | 7.0 | 4.0 | 11.0 |
| dist_terminal_anterior_km | 8.0% | 277.82 | 59.336 | 744.786 | 12.48 | 1.9 | 41.24 |
| risco_estabelecimento | 7.9% | 41.0 | 30.0 | 64.5 | 18.0 | 6.0 | 37.0 |

As variáveis de velocidade (`vel_cartao_terminal_1h`, `qtd_transacoes_cartao_1min`, `qtd_token_carteira_3m`) têm cerca de 8% de valores ausentes; o `SimpleImputer` do pipeline preenche com a mediana e adiciona um indicador de vazio. Fraudes apresentam medianas muito maiores que legítimas nessas variáveis, confirmando o poder discriminativo.

## Cobertura dos sinais de alerta

| Sinal | % Fraudes com sinal | % Legítimas com sinal |
| --- | --- | --- |
| velocidade_terminal | 93.2% | 0.0% |
| rajada_1min | 91.1% | 0.0% |
| token_carteira | 90.4% | 0.0% |
| salto_geografico | 78.1% | 0.3% |
| madrugada | 100.0% | 20.8% |
| valor_alto | 62.3% | 8.1% |
| credito_nao_presente | 82.9% | 29.4% |
| ip_desconhecido | 26.0% | 0.0% |
| estabelecimento_risco | 52.7% | 7.0% |

Sinais como `salto_geografico`, `rajada_1min` e `velocidade_terminal` são quase exclusivos de fraudes. `valor_alto` e `madrugada` aparecem em parte das legítimas, mas com proporção bem maior nas fraudes. A combinação de 3 ou mais sinais é o critério de `PEDIR_CONFIRMACAO`.

## Volume por hora do dia

| Hora | Fraudes | Legítimas |
| --- | --- | --- |
| 00h | 37 | 6,647 |
| 01h | 32 | 6,788 |
| 02h | 28 | 6,688 |
| 03h | 27 | 6,638 |
| 04h | 22 | 6,554 |
| 05h | 0 | 6,720 |
| 06h | 0 | 6,553 |
| 07h | 0 | 6,752 |
| 08h | 0 | 6,700 |
| 09h | 0 | 6,610 |
| 10h | 0 | 6,531 |
| 11h | 0 | 6,632 |
| 12h | 0 | 6,704 |
| 13h | 0 | 6,548 |
| 14h | 0 | 6,734 |
| 15h | 0 | 6,726 |
| 16h | 0 | 6,598 |
| 17h | 0 | 6,565 |
| 18h | 0 | 6,500 |
| 19h | 0 | 6,704 |
| 20h | 0 | 6,789 |
| 21h | 0 | 6,546 |
| 22h | 0 | 6,739 |
| 23h | 0 | 6,577 |

Fraudes se concentram na madrugada (0h–4h), confirmando o sinal `madrugada`. Legítimas seguem o padrão comercial, com pico entre 9h e 18h. A divergência entre os dois perfis é clara e consistente.

## Auditoria de vazamento de informação

As colunas abaixo foram identificadas como proibidas (ESPECIFICACAO, seção 5) e nunca são usadas como entrada do modelo nem das regras de alerta.

| Coluna | Motivo |
| --- | --- |
| `fraud` | Rótulo incorreto: está errado em quase todas as linhas; o rótulo correto é feedback_label. |
| `fraud_score` | Score de fraude calculado pelo sistema externo após a decisão; vazamento direto do alvo. |
| `visa_fraud_score` | Score de fraude da Visa; disponível apenas após a transação ser processada. |
| `mc_fraud_score` | Score de fraude da Mastercard; disponível apenas após o processamento. |
| `decision` | Campo sintético approve/deny, não documentado como decisão de um sistema real; todo deny é fraude (vazamento). Nunca é entrada do modelo. |
| `transaction_status` | Status final da transação; determinado depois da decisão. |
| `action_code` | Código de ação do sistema; resultado da decisão, não entrada. |
| `reason_code` | Código de motivo; resultado da decisão, não entrada. |
| `alert_id` | Identificador do alerta gerado pelo sistema antifraude; pós-decisão. |
| `dispute_*` | Colunas de disputa (prefixo dispute_); existem somente após contestação, posterior à decisão. |
| `fdz_*` | Colunas do sistema FDZ (prefixo fdz_); scores e marcadores pós-decisão. |
| `oob_*` | Colunas out-of-band (prefixo oob_); dados coletados após a autorização. |

O único identificador carregado (`card_id`, `customer_id`, `acceptor_id`) serve apenas para o cálculo de histórico do agente e nunca é exposto na API nem enviado ao watsonx.ai.
