# Avaliação do modelo Sentinela

> Documento gerado por `python -m src.avaliar_rigor` e `python -m src.analisar_custos`.
> Os números abaixo vêm de `modelos/avaliacao_rigorosa.json` e `modelos/custos.json`.

---

## 1. Janelas temporais

A especificação exige validação temporal: o modelo vê o passado e é testado no futuro.
Duas janelas foram avaliadas para verificar estabilidade das métricas ao longo do tempo.

| Janela | Treino (linhas / fraudes) | Teste (linhas / fraudes) | PR-AUC | ROC-AUC | Alertas (corte 30) | Fraudes detectadas | Recall | Precisão |
|---|---|---|---|---|---|---|---|---|
| jan→fev | 13.658 / 52 | 12.265 / 40 | 1,0000 | 1,0000 | 40 | 40 | 1,0 | 1,0 |
| jan+fev→mar | 25.923 / 92 | 13.608 / 54 | 1,0000 | 1,0000 | 54 | 54 | 1,0 | 1,0 |

> Os dados sintéticos do desafio têm separabilidade quase perfeita entre fraudes e compras
> legítimas. PR-AUC = 1,0 e ROC-AUC = 1,0 nas duas janelas confirmam que o modelo generaliza
> perfeitamente para o mês seguinte — o que é esperado para dados gerados artificialmente com
> padrões bem definidos.

---

## 2. Bootstrap — IC 95% de recall e precisão (Sentinela, março)

Mil reamostras com reposição sobre o conjunto de teste de março medem a incerteza
estatística das métricas principais.

| Métrica | IC 95% (inferior – superior) |
|---|---|
| Recall | 1,0 – 1,0 |
| Precisão | 1,0 – 1,0 |

> O IC 95% colapsa num único ponto (1,0 – 1,0) porque em todas as 1.000 reamostras o
> modelo detectou todas as fraudes com precisão perfeita. Isso indica que a robustez não
> depende de uma amostra específica: em qualquer sub-amostra aleatória de março o resultado
> é o mesmo.

---

## 3. Comparação de baselines (março)

Quatro abordagens foram comparadas no mesmo conjunto de teste para justificar o
Sentinela completo (regras + regressão logística).

| Abordagem | Alertas | Fraudes detectadas | Recall | Precisão | PR-AUC |
|---|---|---|---|---|---|
| Só regras ≥ 3 sinais | 213 | 54 | 1,0 | 0,2535 | — |
| Só regras ≥ 4 sinais | 57 | 54 | 1,0 | 0,9474 | — |
| Só modelo | 54 | 54 | 1,0 | 1,0 | 1,0 |
| Sentinela completo | 213 | 54 | 1,0 | 0,2535 | — |
| HistGradientBoosting | 54 | 54 | 1,0 | 1,0 | 1,0 |

> Só regras com ≥ 4 sinais dá exatamente 57 alertas e 54 fraudes, confirmando a referência
> medida em 12/11. O modelo sozinho (regressão logística) é suficiente para precisão e
> recall perfeitos com 54 alertas, e é mais simples de explicar ao analista que o
> HistGradientBoosting.

---

## 4. Ablação de variáveis (março)

Cada variável foi removida individualmente; ao final, as 3 de velocidade foram
retiradas juntas. A queda de PR-AUC mede a importância relativa de cada coluna.

| Variável removida | PR-AUC |
|---|---|
| valor | 1,0 |
| hora | 1,0 |
| madrugada | 1,0 |
| credito | 1,0 |
| nao_presente | 1,0 |
| ip_pais_desconhecido | 1,0 |
| vel_cartao_terminal_1h | 1,0 |
| qtd_transacoes_cartao_1min | 1,0 |
| qtd_token_carteira_3m | 1,0 |
| dist_terminal_anterior_km | 1,0 |
| risco_estabelecimento | 1,0 |
| **COLUNAS_VELOCIDADE (3 juntas)** | **0,861** |

> Como os dados são sintéticos com boa separabilidade, remover qualquer variável
> individualmente não derruba a PR-AUC de 1,0 — cada variável tem redundância suficiente
> nas demais. A exceção é retirar as 3 variáveis de velocidade juntas: a PR-AUC cai para
> 0,861, confirmando a referência medida em 12/11 (cerca de 0,86) e que essas três colunas
> concentram o sinal mais insubstituível do conjunto de dados.

---

## 5. Calibração (março)

Calibração mede se a nota do modelo reflete a probabilidade real de fraude.

**Brier score:** 0,000007 (praticamente zero — calibração excelente)

| Faixa de nota | N | Fraudes | Taxa real (%) | Taxa prevista (%) |
|---|---|---|---|---|
| 0–10 | 13.554 | 0 | 0,0 | 5,0 |
| 10–20 | 0 | 0 | — | 15,0 |
| 20–30 | 0 | 0 | — | 25,0 |
| 30–40 | 0 | 0 | — | 35,0 |
| 40–50 | 0 | 0 | — | 45,0 |
| 50–60 | 0 | 0 | — | 55,0 |
| 60–70 | 0 | 0 | — | 65,0 |
| 70–80 | 1 | 1 | 100,0 | 75,0 |
| 80–90 | 1 | 1 | 100,0 | 85,0 |
| 90–100 | 35 | 35 | 100,0 | 95,0 |

> A nota separa perfeitamente legítimas (faixa 0–10) de fraudes (faixas 70+): 13.554
> compras legítimas têm nota abaixo de 10, e todas as 37 fraudes fora de BLOQUEAR direto
> ficam em notas acima de 70. O Brier score de 0,000007 confirma que a nota não só
> classifica corretamente como também reflete a probabilidade real de forma confiável.

---

## 6. Análise de custos (março)

A análise de custo compara o Sentinela com o sistema atual considerando o valor das
fraudes interceptadas e o custo operacional dos pedidos de confirmação.

**Custo unitário de confirmação assumido:** R$ 1,00

| Métrica | Sentinela | Sistema atual |
|---|---|---|
| Fraudes bloqueadas | 54 | 26 |
| Valor das fraudes bloqueadas (R$) | 13.490,70 | 6.836,54 |
| Fraudes não bloqueadas | 0 | 28 |
| Valor das fraudes não bloqueadas (R$) | 0,00 | 6.654,16 |
| Confirmações solicitadas | 159 | — |
| Custo das confirmações (R$) | 159,00 | — |

**Prejuízo evitado (Sentinela − sistema atual, descontado custo de confirmações):** R$ 6.495,16

> O Sentinela intercepta as 54 fraudes de março (R$ 13.490,70), enquanto o sistema atual
> bloqueou apenas 26 (R$ 6.836,54), deixando 28 fraudes (R$ 6.654,16) passarem. Com custo
> de confirmação de R$ 1,00 por pedido e apenas 159 confirmações, o prejuízo evitado é de
> R$ 6.495,16 — mais do que justificando o custo operacional das confirmações.

---

## 7. Curva de custo por nota de corte (seleção)

A curva mostra como o valor das fraudes capturadas e o custo de confirmações variam
com o limiar de nota usado para disparar alertas.

| Corte | Fraudes capturadas | Valor capturado (R$) | Confirmações | Custo confirmações (R$) |
|---|---|---|---|---|
| 0 | 54 | 13.490,70 | 13.608 | 13.608,00 |
| 10 | 54 | 13.490,70 | 54 | 54,00 |
| 30 | 54 | 13.490,70 | 54 | 54,00 |
| 50 | 54 | 13.490,70 | 54 | 54,00 |
| 70 | 54 | 13.490,70 | 54 | 54,00 |
| 75 | 53 | 13.048,16 | 53 | 53,00 |
| 85 | 52 | 12.800,35 | 52 | 52,00 |
| 100 | 51 | 12.638,19 | 51 | 51,00 |

> Corte em 30 (valor de `NOTA_CONFIRMAR`) representa o ponto de operação do Sentinela.
> As notas ficam em bipartição quase perfeita (< 10 para legítimas, ≥ 70 para fraudes),
> então qualquer corte entre 10 e 70 captura todas as 54 fraudes com apenas 54 confirmações.
> A tabela completa com 21 pontos (0 a 100, de 5 em 5) está em `modelos/custos.json`.
