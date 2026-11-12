# 07 — Registro de decisões (ADRs)

Cada decisão cara de reverter tem um registro. Um ADR aceito não é editado: se a decisão
mudar, escreva um ADR novo que substitui o anterior.

---

# ADR-001 — Código e textos em português do Brasil

**Status:** Aceito · **Data:** 2026-11-12

## Contexto
O Manual da IDE (2.5.1) pede identificadores em inglês, mas admite exceção registrada. A
ESPECIFICACAO, os testes e as Etapas 1 a 4 já foram entregues com nomes em português
(`calcular_sinais`, `AgenteSentinela`), o domínio do desafio é conversado em português com a
Sicredi e faltam 3 dias para a entrega.

## Decisão
Identificadores, comentários, docstrings, logs e textos de tela ficam em português do Brasil,
sem acento em identificadores e nomes de arquivo. Prefixos de commit (Conventional Commits)
ficam em inglês, com assunto em português.

## Alternativas rejeitadas
- **Tudo em inglês:** exigiria renomear funções, testes e a especificação já entregues, com risco
  de quebrar as invariantes a 3 dias do prazo.
- **Misturar idiomas:** gera nomes híbridos (`get_transacao`), proibidos pelo Manual.

## Consequências
Leitura fácil para o time e os avaliadores. Quem for usar bibliotecas convive com APIs em inglês
ao lado de nomes em português, o que é aceitável. Nenhum nome híbrido é permitido.

---

# ADR-002 — Streamlit e Python, rodando localmente, fora da stack padrão da IDE

**Status:** Aceito · **Data:** 2026-11-12

## Contexto
A stack padrão da IDE é Next.js, Django e PostgreSQL. Este projeto não é de cliente da IDE: é um
protótipo do desafio IBM SkillsBuild, de uso de um analista por vez, feito em 3 dias, com dados
que não podem ir para a internet sem cuidado e um ecossistema de ciência de dados em Python.

## Decisão
Interface em Streamlit, núcleo e scripts em Python, tudo rodando na máquina de quem usa.

## Alternativas rejeitadas
- **Next.js com API Django e PostgreSQL:** duas linguagens, API e banco para um protótipo de uma
  tela; inviável no prazo.
- **Notebook Jupyter:** não é uma ferramenta para o analista e não demonstra o fluxo de revisão.
- **Hospedar no Streamlit Community Cloud:** a base de 294 MB não pode ir para o repositório, e
  o Granite local não estaria disponível.

## Consequências
Desenvolvimento rápido e um só idioma de programação. Sem login, sem multiusuário, sem deploy.
O modelo de execução do Streamlit (o script roda de novo a cada clique) obriga a usar cache e
`st.session_state` com cuidado.

---

# ADR-003 — Regressão logística como modelo de produção

**Status:** Aceito · **Data:** 2026-11-12

## Contexto
Os dados sintéticos separam fraude e compra legítima quase perfeitamente. A explicação para o
analista é parte central da proposta.

## Decisão
O modelo salvo é a regressão logística com imputação pela mediana, indicadores de vazio,
padronização e pesos para a classe rara.

## Alternativas rejeitadas
- **Gradient boosting:** desempenho igual nesta base e coeficientes menos interpretáveis.
- **Só regras, sem modelo:** não dá uma nota contínua para ordenar a fila.

## Consequências
Coeficientes legíveis e nota fácil de explicar. Em dados reais, mais complexos, vale reavaliar.

---

# ADR-004 — Validação temporal

**Status:** Aceito · **Data:** 2026-11-12

## Contexto
Todas as fraudes da base estão entre janeiro e março de 2025. Em produção, o modelo sempre prevê
o futuro a partir do passado.

## Decisão
Treino com janeiro e fevereiro de 2025 e teste com março de 2025. Nunca divisão aleatória.

## Alternativas rejeitadas
- **Divisão aleatória:** mistura passado e futuro e infla as métricas.
- **Validação cruzada embaralhada:** mesmo problema.

## Consequências
Métricas honestas para o cenário de produção. A concentração das fraudes em 3 meses exige
monitoramento de desvio em uso real.

---

# ADR-005 — O IBM Granite explica, mas não decide

**Status:** Aceito · **Data:** 2026-11-12

## Contexto
Um modelo de linguagem escreve bem, mas não é determinístico nem auditável. A decisão de bloquear
uma compra precisa ser reproduzível.

## Decisão
A decisão vem de regras e da regressão logística. O IBM Granite 4 (`granite4:micro`), rodando
localmente pelo Ollama, só escreve a explicação. Se ele não responder, o agente monta o texto a
partir dos sinais.

## Alternativas rejeitadas
- **LLM decide:** resultado não reproduzível e difícil de auditar.
- **watsonx.ai na nuvem:** exige conta, chave de API e custo; a chave correria risco de ir para o
  repositório. Não é obrigatório no desafio.
- **Só texto por regras:** funciona, mas a explicação fica menos natural.

## Consequências
O sistema funciona sem o Ollama. Com ele, a explicação fica mais clara. A primeira explicação
demora enquanto o modelo carrega.

---

# ADR-006 — Exclusão de colunas com vazamento de informação

**Status:** Aceito · **Data:** 2026-11-12

## Contexto
A base tem colunas que entregam a resposta ou só existem depois da decisão: scores de fraude
prontos, a decisão do sistema atual, campos de disputa e uma coluna `fraud` que não é o rótulo.

## Decisão
Essas colunas nunca entram no modelo nem nas regras (lista na ESPECIFICACAO, seção 5).
`decision` é carregada só para comparar com o sistema atual.

## Alternativas rejeitadas
- **Usar `fraud_score`:** o modelo apenas copiaria o sistema existente, e o score pode não estar
  disponível no momento da autorização.

## Consequências
Métricas que refletem o que o Sentinela aprende sozinho.

---

# ADR-007 — Fila de demonstração com todas as fraudes de março e 2.000 compras legítimas

**Status:** Aceito · **Data:** 2026-11-12

## Contexto
Março tem 13.608 transações e 54 fraudes. A interface precisa mostrar o fluxo de revisão de forma
clara e rápida, no vídeo e na avaliação.

## Decisão
A fila tem as 54 fraudes de março e 2.000 transações legítimas de março sorteadas com semente 42.
A página "Como funciona" diz isso explicitamente.

## Alternativas rejeitadas
- **Todas as 13.608 transações:** carga mais lenta e fluxo de demonstração diluído.
- **Só as fraudes:** esconderia as decisões de aprovar e pedir confirmação.

## Consequências
A proporção de fraudes na fila não é a real. Em produção, a fila seria o fluxo completo de
transações.

---

# ADR-008 — Fluxo Git reduzido, revisão assíncrona e CI

**Status:** Aceito · **Data:** 2026-11-12

## Contexto
O time tem 5 pessoas sem tempo para reuniões, e o código é escrito pelo IBM Bob a partir de
prompts. O Manual da IDE (2.2) pede Issue, branch, Pull Request, revisão e merge em `develop`.

## Decisão
Uma Issue por tarefa, branch `feature/<numero>-<slug>`, Pull Request para `develop`, revisão por
outra pessoa com prazo de 2 horas nesta reta final, merge por "Squash and merge" feito por quem
revisou. `main` recebe `develop` uma vez, na versão de entrega. Um workflow do GitHub Actions roda
Black, Ruff e pytest em todo Pull Request.

## Alternativas rejeitadas
- **Push direto em `main`:** sem revisão nem histórico rastreável.
- **Prazo de revisão de 1 dia útil (padrão do Manual):** incompatível com a entrega em 3 dias.

## Consequências
Cada mudança fica ligada a uma Issue e revisada. O time precisa responder a pedidos de revisão
em até 2 horas.

---

# ADR-009 — Testes de conformidade do líder, independentes do Bob

**Status:** Aceito · **Data:** 2026-11-12

## Contexto
As Etapas 1 a 4 foram feitas pelo IBM Bob com relatórios de "tudo certo", mas o resultado não
atendeu à especificação. O Bob escreve o código e os próprios testes; sem uma régua externa,
"pronto" depende da palavra dele.

## Decisão
O líder mantém `tests/test_conformidade_nucleo.py` e `tests/test_conformidade_interface.py`,
escritos a partir da ESPECIFICACAO e do design e validados contra uma implementação de referência.
Eles conferem estrutura, constantes, sinais, decisão, explicação, modelo, números de `modelos/`
(inclusive se saem do código atual), formatação, textos e as telas com o `AppTest`. O Bob não pode
alterá-los (AGENTS.md, seção 12) e cada Issue só termina com 0 falhas.

## Alternativas rejeitadas
- **Confiar no relatório do Bob:** foi o que falhou nas Etapas 1 a 4.
- **Só revisão humana:** o time não tem tempo para conferir números e textos à mão.

## Consequências
"Pronto" vira uma linha do pytest. Mudar a especificação exige mudar esses testes, o que só o
líder faz, numa Issue própria.

---

# ADR-010 — A interface antiga da Etapa 4 é descartada

**Status:** Aceito · **Data:** 2026-11-12

## Contexto
O `app.py` da Etapa 4 não segue o design (`docs/08`), que mudou a estrutura em módulos,
textos centralizados, estados e acessibilidade.

## Decisão
A Issue #1 apaga a interface antiga, para que Black, Ruff e CI não tropecem nela, e a Issue #3
recria a base do zero, sem reaproveitar trechos.

## Alternativas rejeitadas
- **Refatorar o `app.py` antigo:** custa mais revisar o que manter do que reescrever a partir de
  um design que já define cada componente e texto.

## Consequências
Quem testou a interface antiga apaga o próprio `data/feedback.csv`, cujo formato pode ser outro.
