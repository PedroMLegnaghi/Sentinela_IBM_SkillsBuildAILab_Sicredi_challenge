# Backlog

Cada seção é uma Issue do GitHub com o mesmo número. O Bob executa uma Issue com o protocolo do
`AGENTS.md` (seção 3) e só altera os "Arquivos permitidos". Congelamento do código: **sábado
14/11, 12h**. Entrega: domingo 15/11, 17h.

## Regras comuns

- **O campeão não muda.** Nenhuma Issue altera `src/preparar_dados.py`, `src/treinar_modelo.py`,
  `src/agente.py` nem os arquivos de `modelos/` que eles geram. Modelos novos só em memória.
- **Invariantes intactas.** `python -m src.avaliar_agente` mostra os números da ESPECIFICACAO,
  seção 11, e a conformidade (`tests/test_conformidade_*.py`) termina sem falhas, com `data/`.
- **O contrato manda.** Rotas, campos e códigos são os da ESPECIFICACAO, seções 12 a 16. O site
  usa só `web/lib/api.ts` e `web/lib/tipos.ts`. Faltou algo? Pare e pergunte.
- **Scripts de análise** rodam com `python -m src.<nome>`, leem só o parquet, gravam um JSON em
  `modelos/` (nunca editado à mão, no mesmo commit do script) e nunca guardam identificadores.
- **Site:** testes com Vitest e os mocks de `web/lib/mocks/`; verificação manual com a API real.
- **Sem revisão.** O dono roda o portão na própria máquina, abre o PR para `develop`, espera o CI
  verde e faz "Squash and merge".

## Feitas

| # | Entrega | PR |
| --- | --- | --- |
| 1–8, 13, 19 | Núcleo corrigido (dados, modelo, agente, avaliação) e padrões | #9 a #16, #36 |
| 37 | Arquitetura web com auditoria por IA | #49 |
| 38, 52 | API FastAPI | #50, #53 |
| 39 | Auditoria por IA no watsonx.ai (ou modo local) | #54 |
| 40 | Base do site (Next.js + Carbon) | #51 |
| 43 | Fila de alertas e painel da transação | #57 |
| 44 | Desempenho e Como funciona | #58 |
| 45 | Simulador e Respostas do analista | #59 |
| 46 | Script que compara IA e modelo (falta rodar com o watsonx.ai) | #55 |
| 60, 61 | Estrutura enxuta; contrato do canal e do "Pergunte à IA" | este PR |

## Abertas

| # | Título | Dono | Branch | Depende de | Prazo |
| --- | --- | --- | --- | --- | --- |
| 62 | feat: cria o canal do associado na API | Bruno | `feature/62-canal-do-associado` | — | sex 13/11, 14h |
| 41 | feat: explica o que pesou na nota | Bruno | `feature/41-explicabilidade` | — | sex 13/11, 19h |
| 48 | fix: corrige a acessibilidade e a responsividade do site | Bruno | `feature/48-acessibilidade` | #63, #64 | sáb 14/11, 11h |
| 63 | feat: cria o app do associado no site | Mariana | `feature/63-app-do-associado` | mocks; API da #62 | sex 13/11, 19h |
| 64 | feat: mostra o perfil do associado no painel | Pedro Machado | `feature/64-perfil-do-associado` | — | sex 13/11, 19h |
| 47 | feat: documenta a análise exploratória dos dados | Pedro Machado | `feature/47-analise-exploratoria` | — | sex 13/11, 19h |
| 30 | docs: registra o uso do IBM Bob | Pedro Machado | `feature/30-uso-do-bob` | todas | sáb 14/11, 11h |
| 42 | feat: avalia o modelo com rigor e calcula o custo da fraude | Lucas | `feature/42-avaliacao-e-custo` | — | sex 13/11, 19h |
| 67 | docs: explica privacidade e experiência do associado | Lucas | `feature/67-privacidade` | #62 | sáb 14/11, 11h |
| 32 | docs: atualiza o README e propõe os textos de entrega | Lucas | `feature/32-readme-e-textos` | todas | sáb 14/11, 12h |
| 65 | feat: redige a mensagem ao associado com o watsonx.ai | Pedro Muller | `feature/65-mensagem-pela-ia` | #62, watsonx.ai | sáb 14/11, 11h |
| 46 | (execução) compara a auditoria por IA com o modelo | Pedro Muller | `feature/46-rodar-ia-contra-modelo` | watsonx.ai | sáb 14/11, 11h |
| 66 | feat: cria o "Pergunte à IA sobre este caso" (extra) | Pedro Muller | `feature/66-pergunte-a-ia` | — | sáb 14/11, 11h |
| 8 | chore: publica a versão de entrega, grava o vídeo e envia | Pedro Muller | `develop` → `main` | todas | sáb 14/11, 22h |

---

## #62 — feat: cria o canal do associado na API

ESPECIFICACAO, seção 15; ADR-015. Os testes da conformidade da API para o canal deixam de pular
quando `src/associado/__init__.py` existe.

- **Arquivos permitidos:** `src/associado/__init__.py`, `src/associado/mensagem.py`,
  `src/associado/notificacoes.py` (novos), `src/api/app.py`, `src/api/esquemas.py`,
  `src/api/servicos.py`, `src/config.py` (só constantes do canal), `tests/test_associado.py`.

**Passos**

1. `mensagem.py`: `redigir_mensagem(transacao, analise) -> tuple[str, str]` com os dois modelos
   fixos (fonte `"modelo"`) e `validar_mensagem(texto) -> bool` com as regras contra golpe.
   Deixe um ponto único para a #65 plugar o watsonx.ai.
2. `notificacoes.py`: armazenamento em memória protegido por `threading.Lock` (como
   `src/api/auditorias.py`); `criar_notificacao`, `obter`, `listar` (mais recente primeiro),
   `responder` com as regras de status e `resultado` da seção 15.
3. Rotas e esquemas: as 4 da tabela da seção 15, com 201/200/404/409/422. `POST /api/analisar`
   cria a notificação e devolve `id_notificacao`; `GET /api/transacoes/{id}` traz `notificacao`.
4. Testes: cada regra de status, mensagem dentro das regras (inclusive sem data), resposta
   duplicada → 409, APROVAR → 422.

**Aceite:** portão completo; conformidade da API sem falhas e sem os 6 testes do canal pulando.

## #41 — feat: explica o que pesou na nota

- **Arquivos permitidos:** `src/explicabilidade.py`, `tests/test_explicabilidade.py`.

**Passos**

1. Com o pipeline salvo (`imputer` → `scaler` → `modelo`), sem treinar:
   `contribuicoes(pipeline, transacao)` aplica `imputer` e `scaler` e devolve
   `{"variavel", "nome", "contribuicao"}` para cada coluna da regressão (as 11 variáveis e os
   indicadores de vazio), com `contribuicao = coeficiente × valor padronizado`, ordenado por valor
   absoluto; `importancia_global(pipeline)`; `NOMES_LEGIVEIS` em português (indicador de vazio vira
   "<nome> ausente").
2. A API já chama `contribuicoes` e o painel já desenha o gráfico (`GraficoContribuicoes`): basta
   preencher o cálculo e retirar o TODO.
3. Testes com um pipeline pequeno treinado no teste com dados inventados: soma das contribuições
   mais o intercepto = log-odds; ordenação; nome para todas as colunas.

**Aceite:** portão completo; numa transação bloqueada, o painel mostra contribuições positivas
grandes.

## #48 — fix: corrige a acessibilidade e a responsividade do site

- **Antes do Bob:** Lighthouse (Accessibility) no Chrome em todas as páginas, zoom de 200% e
  janela de 768 px; registre notas e problemas num comentário da Issue.
- **Arquivos permitidos:** `web/**`, exceto `web/lib/tipos.ts` e `web/lib/api.ts`.

**Passos:** um commit por problema registrado; refazer o Lighthouse e colocar as notas no PR.

**Aceite:** Lighthouse Accessibility ≥ 90 em todas as páginas; nada cortado em 200% e 768 px;
portão do site.

## #63 — feat: cria o app do associado no site

ESPECIFICACAO, seção 15. Comece pelos mocks; troque para a API real quando a #62 estiver em
`develop`.

- **Arquivos permitidos:** `web/app/associado/page.tsx`, `web/components/associado/*` (novos),
  `web/components/painel/*` (só para mostrar a notificação), `web/components/layout/*` (link no
  menu), `web/lib/tipos.ts` (`Notificacao` e os campos `notificacao`/`id_notificacao`),
  `web/lib/api.ts` (`obterNotificacoes`, `obterNotificacao`, `responderNotificacao`,
  `notificarAssociado`), `web/lib/mocks/*`, bloco "App do associado" de `web/lib/textos.ts`,
  `web/tests/associado.test.tsx`.

**Passos**

1. Página `/associado`: uma moldura de celular com a lista de notificações (mais recente
   primeiro); cada uma mostra a mensagem, a hora e, se `aguardando`, os botões "Sim, fui eu" e
   "Não fui eu" com o mesmo peso visual; depois da resposta, mostra o `resultado`.
2. Painel da transação: um bloco "Associado" com o status da notificação (Aguardando / Confirmou
   a compra / Não reconheceu) e o botão "Avisar o associado" quando ainda não houver notificação
   e a decisão não for APROVAR.
3. Simulador: depois de analisar, se vier `id_notificacao`, um link "Ver no app do associado".
4. Testes: responder "não" mostra o resultado; botões somem depois da resposta; erro 409
   mostra mensagem em português.

**Aceite:** portão do site; fluxo do vídeo funcionando com a API real (simulador → app do
associado → "Não fui eu" → painel mostra "Não reconheceu").

## #64 — feat: mostra o perfil do associado no painel

ESPECIFICACAO, seção 12 (PerfilAssociado). O teste da conformidade deixa de pular quando a
transação traz `perfil_associado`.

- **Arquivos permitidos:** `src/api/servicos.py`, `src/api/esquemas.py`,
  `src/auditoria/ferramentas.py` (só `_perfil_cliente`), `tests/test_perfil_associado.py`,
  `web/lib/tipos.ts` (`PerfilAssociado`), `web/lib/mocks/*`,
  `web/components/painel/PerfilAssociado.tsx` (novo), `web/components/painel/PainelTransacao.tsx`,
  bloco "Perfil" de `web/lib/textos.ts`, `web/tests/perfil.test.tsx`.

**Passos**

1. API: `perfil_associado` em `GET /api/transacoes/{id}`, reaproveitando a ferramenta
   `perfil_do_cliente` de `src/auditoria/ferramentas.py` e acrescentando `hora_mais_comum` (só
   compras anteriores; `null` sem histórico).
2. Painel: cartão "O normal deste associado" com compras anteriores, mediana de valor, "esta
   compra é N vezes a mediana" (destacado se ≥ 3), hora mais comum, % na madrugada e % de crédito
   não presente; sem histórico, "Primeira compra registrada deste associado".
3. Testes Python (perfil sem histórico, só compras anteriores) e do site (com e sem perfil).

**Aceite:** portão completo e do site; conformidade da API sem falhas e sem pular o teste do
perfil.

## #47 — feat: documenta a análise exploratória dos dados

- **Arquivos permitidos:** `src/analisar_dados.py`, `modelos/eda.json` (gerado),
  `docs/analise-exploratoria.md`, `tests/test_analisar_dados.py`.

**Passos**

1. `src/analisar_dados.py` lê só o parquet e calcula, sem identificadores: linhas, fraudes e
   percentual por mês, tipo e modalidade; por variável de `VARIAVEIS_MODELO`, % de vazios,
   mediana e percentis 10/90 em fraudes e legítimas; % de fraudes e de legítimas com cada sinal;
   contagem por hora (24) para fraude e legítima.
2. Auditoria de vazamento: as colunas proibidas da ESPECIFICACAO, seção 5, com o motivo de cada.
3. `main()` grava `CAMINHO_EDA` e escreve o documento com as tabelas e até 3 frases de leitura
   por tabela. A API já expõe o JSON em `/api/metricas` (`extras.eda`).
4. Testes com dados inventados: contagens por mês, percentis, nenhum id na saída.

**Aceite:** portão completo; 160.000 linhas e 146 fraudes no JSON; documento coerente com o JSON.

## #42 — feat: avalia o modelo com rigor e calcula o custo da fraude

- **Arquivos permitidos:** `src/avaliar_rigor.py`, `src/analisar_custos.py`,
  `modelos/avaliacao_rigorosa.json`, `modelos/custos.json` (gerados), `docs/avaliacao.md`,
  `tests/test_avaliar_rigor.py`, `tests/test_analisar_custos.py`.

**Avaliação rigorosa** (`avaliar_rigor.py`, mesma receita do campeão, treino em memória):
janelas temporais (jan → fev; jan–fev → mar) com PR-AUC, ROC-AUC, recall, precisão e alertas no
corte `NOTA_CONFIRMAR`; IC 95% de recall e precisão do Sentinela completo por bootstrap
(`REPETICOES_BOOTSTRAP`, `SEMENTE`); comparação só regras (≥3 e ≥4 sinais), só modelo, Sentinela
e `HistGradientBoostingClassifier`; ablação sem cada variável e sem as 3 de
`COLUNAS_VELOCIDADE`; calibração (Brier e 10 faixas). Referência medida em 12/11: sem as 3 de
velocidade a PR-AUC cai para cerca de 0,86; só regras com ≥4 sinais dá 57 alertas e 54 fraudes.

**Custo** (`analisar_custos.py`, março): `calcular_custos(teste, custo_confirmacao)` com valor das
fraudes bloqueadas e não bloqueadas do Sentinela e do sistema atual (`decision == "deny"`),
custo das confirmações (`CUSTO_PEDIDO_CONFIRMACAO`), prejuízo evitado e curva de custo por nota
de corte (0 a 100, de 5 em 5). Valor vazio conta 0 e entra em `valores_vazios`.

`docs/avaliacao.md` traz as duas análises, com até 3 frases de leitura por tabela. A API já expõe
os JSON em `/api/metricas` (`extras`). Testes com dados inventados (bootstrap ordenado, soma do
custo, prejuízo = diferença, curva com 21 pontos).

**Aceite:** portão completo; JSON gerados pelos scripts; números do documento iguais aos dos JSON.

## #67 — docs: explica privacidade e experiência do associado

- **Arquivos permitidos:** `docs/privacidade.md` (novo), `web/components/como-funciona/*`, bloco
  "Como funciona" de `web/lib/textos.ts`, `web/tests/desempenho.test.tsx`.

**Passos:** documento curto com o que o Sentinela lê e o que nunca lê (seções 4 e 5), o que vai
para o watsonx.ai (sem identificadores), as regras contra golpe da mensagem (seção 15) e os
números de experiência (0 legítimas bloqueadas; 159 confirmações em 13.608 compras). Uma seção
"Privacidade e o associado" em Como funciona, com 3 a 5 frases e os mesmos números.

**Aceite:** portão do site; números iguais aos de `modelos/avaliacao_agente.json`.

## #30 — docs: registra o uso do IBM Bob

- **Arquivos permitidos:** `docs/uso-do-bob.md` (novo), `.bob/custom_modes.yaml` (ou o arquivo
  que a documentação do Bob indicar).

**Passos:** como o time usou o Bob (`AGENTS.md`, `.bobignore`, modos, prompt único, contrato da
API e testes de conformidade permitindo backend e site em paralelo), tabela de Issues e PRs tirada
de `gh pr list --state all`, defeitos que a conformidade e o CI pegaram, o que aprendemos. Um
modo personalizado `auditor-sentinela` com as regras do portão; cite a página da documentação.

**Aceite:** números reais do GitHub; o modo aparece no seletor do Bob.

## #32 — docs: atualiza o README e propõe os textos de entrega

- **Arquivos permitidos:** `README.md`.

**Passos:** acrescentar ao README os achados de `docs/avaliacao.md` e
`docs/analise-exploratoria.md` com os números dos JSON, o canal do associado e o link para
`docs/uso-do-bob.md`; conferir que cada comando do README funciona. No relatório, propor os Textos
1 (problema e solução) e 2 (tecnologia e IBM Bob), até 500 palavras cada.

**Aceite:** números iguais aos dos JSON; todos os comandos funcionam.

## #65 — feat: redige a mensagem ao associado com o watsonx.ai

- **Arquivos permitidos:** `src/associado/mensagem.py`, `src/auditoria/watsonx.py` (só se
  precisar de uma função de chat sem ferramentas), `tests/test_associado.py`.

**Passos:** com credenciais, o Granite redige a mensagem a partir de valor, data, hora, tipo e
decisão (nunca identificadores); toda mensagem passa por `validar_mensagem`; recusa ou falha →
modelo fixo, com log. Testes com o watsonx.ai simulado: mensagem válida usada (fonte "watsonx"),
inválida trocada, falha cai no modelo.

**Aceite:** portão completo; conformidade da API sem falhas; no PR, 3 exemplos reais de mensagem
gerada (sem identificadores).

## #46 (execução) — compara a auditoria por IA com o modelo

O script já está em `develop`. Com o `.env` preenchido: `python -m src.avaliar_ia`; conferir que
nenhuma auditoria caiu no modo local; commit só de `modelos/ia_contra_modelo.json`. A página
Desempenho passa a mostrar a comparação.

## #66 — feat: cria o "Pergunte à IA sobre este caso" (extra)

ESPECIFICACAO, seção 16. Só depois da #65 e da #46.

- **Arquivos permitidos:** `src/auditoria/perguntas.py` (novo), `src/api/app.py`,
  `src/api/esquemas.py`, `tests/test_perguntas.py`, `web/components/painel/PergunteIA.tsx`
  (novo), `web/components/painel/PainelTransacao.tsx`, `web/lib/tipos.ts`, `web/lib/api.ts`,
  `web/lib/mocks/*`, bloco "Pergunte à IA" de `web/lib/textos.ts`.

**Aceite:** portão completo e do site; conformidade da API sem pular o teste de perguntas.

## #8 — chore: publica a versão de entrega, grava o vídeo e envia

PR `develop` → `main` com merge commit (não squash); tag `v1.0`; vídeo de até 3 minutos;
Textos 1 e 2; envio em My Teams → Submissions até domingo, 17h.

---

# Refatoração: associado e filial (branch `refatoracao`)

Decidida em sáb 14/11, noite. Fica fora do `develop` até a **linha de corte: domingo 15/11, 14h**.
Se não estiver pronta e testada nessa hora, a entrega usa a versão atual do `develop`.

## O que muda

O site passa a ter duas áreas, com a identidade visual da Sicredi (verde `#3FA110`, branco, Exo 2
nos títulos e Nunito no texto):

- **Associado** (pensado para celular): login simulado, saldo, cartões, extrato, simular compra,
  aviso "Foi você?" e "Não reconheço esta compra".
- **Filial** (pensada para desktop): fila do auditor só com a carteira da filial, painel da compra
  com o detalhe técnico e painel do gerente com as métricas.

## Regras da refatoração

- **O núcleo não muda.** BLOQUEAR bloqueia na hora; PEDIR_CONFIRMACAO espera o associado.
- **As rotas atuais e a conformidade ficam intactas.** As rotas novas ficam em arquivos próprios
  (`src/api/rotas_associado.py` e `src/api/rotas_filial.py`), incluídos em `src/api/app.py`.
- **Portas e adaptadores.** As regras novas dependem de interfaces de repositório (`src/portas/`);
  hoje o adaptador é em memória (`src/adaptadores/memoria/`). Trocar por Postgres não mexe nas
  regras.
- **Dados fictícios.** Nomes, saldos, limites, filiais e auditores são inventados. Cada associado
  com login é ligado a um cliente da base, para ter histórico. Os clientes de março são divididos
  igualmente entre as duas filiais.
- **Privacidade.** O associado vê um motivo genérico e "Analista da agência X". O detalhe técnico
  (sinais, o que pesou, parecer da IA) e o nome completo do auditor aparecem só na filial. O
  auditor vê nome abreviado, final do cartão, a compra em análise e histórico agregado; nunca o
  saldo nem o extrato inteiro.
- **Saldo.** Compra aprovada no débito desconta o saldo; no crédito, consome o limite; bloqueada
  ou aguardando confirmação não mexe em nada.

## Divisão em duas pessoas

O contrato (R1) é fechado primeiro. Depois, as duas trilhas correm em paralelo e não tocam nos
mesmos arquivos: o **site** é feito contra os mocks e a **API**, contra os testes do contrato.

| Trilha | Dono | Pastas |
| --- | --- | --- |
| Site | Pedro Muller | `web/` (menos as pastas da R11) |
| API | Pessoa 2 | `src/`, `tests/`, e as pastas da R11 em `web/` |

Cada Issue vira uma branch `refatoracao/<id>-<slug>` a partir de `refatoracao`, com PR para
`refatoracao`.

## Prioridade 1 (entra na entrega se ficar pronta até domingo, 14h)

| Id | Título | Dono | Depende de |
| --- | --- | --- | --- |
| R0 | design: protótipo de alta fidelidade (`docs/prototipo/`) | Pedro Muller | — |
| R1 | docs: fecha o contrato das rotas novas (ESPECIFICACAO, tipos e mocks) | Pedro Muller, com revisão da Pessoa 2 | R0 |
| R2 | feat: aplica a identidade Sicredi e cria as molduras e o login simulado | Pedro Muller | R1 |
| R3 | feat: cria o domínio, as portas e os adaptadores em memória | Pessoa 2 | R1 |
| R4 | feat: cria a tela inicial e o extrato do associado | Pedro Muller | R2 |
| R5 | feat: cria as rotas do associado | Pessoa 2 | R3 |
| R6 | feat: cria o simular compra, o aviso e o "não reconheço" | Pedro Muller | R4 |
| R7 | feat: cria as rotas da filial | Pessoa 2 | R5 |
| R8 | feat: cria a fila do auditor e o painel da compra na filial | Pedro Muller | R6 |
| R9 | feat: calcula as métricas do gerente | Pessoa 2 | R7 |
| R10 | feat: cria o painel do gerente | Pedro Muller | R8 |
| R11 | feat: leva "Desempenho" e "Como funciona" para a área da filial | Pessoa 2 | R2, R9 |
| R12 | test: integra o site com a API e confere tudo com o watsonx.ai | os dois | R10, R11 |

### R1 — contrato

Rotas previstas (campos fechados nesta Issue, na ESPECIFICACAO, seção 17):

- `POST /api/sessao` (login simulado; devolve o perfil: associado, auditor ou gerente)
- `GET /api/associado/inicio` (saldo, limite e cartões)
- `GET /api/associado/extrato`
- `POST /api/associado/compras` (simula a compra; passa pelo Sentinela e entra no extrato e na fila
  da filial)
- `POST /api/associado/compras/{id}/contestacao` ("não reconheço": registra, avisa a filial e
  bloqueia o cartão)
- `GET /api/filial/fila` e `GET /api/filial/compras/{id}` (só a carteira da filial; visão dentro
  da LGPD)
- `GET /api/filial/metricas`

Aceite: tipos em `web/lib/tipos.ts`, mocks em `web/lib/mocks/` e um teste de contrato por rota em
`tests/test_contrato_refatoracao.py` (pulado até a rota existir).

### R3 — domínio, portas e adaptadores

`src/dominio/` (associado, cartão, filial, auditor, compra, contestação), `src/portas/`
(repositórios) e `src/adaptadores/memoria/`. Duas filiais, dois auditores e um gerente por filial,
cerca de cinco associados com login em cada. Aceite: as regras não importam nenhum adaptador; os
testes trocam o repositório por um dublê.

### R9 — métricas do gerente

Por filial: decisões por tipo de compra e por modalidade; acerto do modelo pela resposta do
associado ("fui eu" e "não fui eu"); fraudes que o modelo aprovou (contestações); tempo de resposta
do associado. Bloqueios por auditor entram na R15.

## Prioridade 2 (ações do auditor)

| Id | Título | Dono | Depende de |
| --- | --- | --- | --- |
| R13 | feat: auditor bloqueia compra que aguarda confirmação (API) | Pessoa 2 | R7 |
| R14 | feat: auditor bloqueia compra que aguarda confirmação (site) | Pedro Muller | R8, R13 |
| R15 | feat: mostra bloqueios por auditor e quantos estavam certos | os dois | R13, R14 |

O bloqueio registra o nome do auditor, a data e o motivo (explicação da IA mais uma nota dele). Se
o associado responder "fui eu", a compra é liberada sozinha e o bloqueio conta como incorreto.

## Prioridade 3 (chat)

| Id | Título | Dono | Depende de |
| --- | --- | --- | --- |
| R16 | feat: chat do associado com a IA (API, watsonx.ai) | Pessoa 2 | R5 |
| R17 | feat: chat do associado e "conversar com gerente" (site) | Pedro Muller | R4, R16 |

A IA só informa: resume os gastos e explica, em termos genéricos, as compras bloqueadas do próprio
associado. "Conversar com gerente" abre a mesma conversa com um resumo da sessão e para aí
(simulado).

## Prioridade 4

| Id | Título | Dono | Depende de |
| --- | --- | --- | --- |
| R18 | feat: persiste em Postgres por um adaptador novo | a definir | R3 |
