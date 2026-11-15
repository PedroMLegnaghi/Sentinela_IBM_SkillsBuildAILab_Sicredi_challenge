# Backlog

Cada seção é uma Issue do GitHub com o mesmo número. O Bob executa uma Issue com o protocolo do
`AGENTS.md` (seção 3) e só altera os "Arquivos permitidos". Congelamento do código: **domingo
15/11, 12h** (só para as Issues da versão de reserva). Entrega: domingo 15/11, 17h.

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

## Versão de reserva (dom 15/11)

Decidida em sáb 14/11, noite. A refatoração (branch `refatoracao`, Issues #90 a #107) é feita por
Pedro Muller e Bruno e só entra se estiver pronta até domingo às 14h. Enquanto isso, Pedro Machado,
Mariana e Lucas melhoram o `develop` com o Bob, para que a entrega tenha uma versão melhor caso a
refatoração não entre. Cada Issue abaixo é independente das outras; quando duas mexem no mesmo
arquivo (`globals.scss`, `Shell.tsx`, `textos.ts`), cada uma só toca o seu bloco, e quem integrar
depois dá `git pull` e resolve o conflito antes do merge.

| # | Título | Dono | Branch | Prazo |
| --- | --- | --- | --- | --- |
| 108 | feat: aplica a identidade visual da Sicredi no site atual | Mariana | `feature/108-identidade-sicredi` | dom 15/11, 12h |
| 48 | fix: corrige a acessibilidade e a responsividade do site | Lucas | `feature/48-acessibilidade` | dom 15/11, 12h |
| 109 | feat: mostra quando o aviso ao associado foi redigido pelo IBM Granite | Lucas | `feature/109-selo-granite` | dom 15/11, 12h |
| 110 | feat: adiciona cenários prontos ao simulador "e se" | Pedro Machado | `feature/110-cenarios-simulador` | dom 15/11, 12h |
| 111 | docs: atualiza a arquitetura e os requisitos com o estado final | Pedro Machado | `feature/111-docs-estado-final` | dom 15/11, 12h |
| 112 | fix: mostra a latência em segundos e padroniza os números do Desempenho | Mariana | `feature/112-numeros-desempenho` | dom 15/11, 12h |
| 66 | feat: cria o "Pergunte à IA sobre este caso" (extra) | Pedro Machado | `feature/66-pergunte-a-ia` | dom 15/11, 12h |

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
| 63 | feat: cria o app do associado no site | Mariana | `feature/63-app-do-associado` | mocks; API da #62 | sex 13/11, 19h |
| 64 | feat: mostra o perfil do associado no painel | Pedro Machado | `feature/64-perfil-do-associado` | — | sex 13/11, 19h |
| 47 | feat: documenta a análise exploratória dos dados | Pedro Machado | `feature/47-analise-exploratoria` | — | sex 13/11, 19h |
| 30 | docs: registra o uso do IBM Bob | Pedro Machado | `feature/30-uso-do-bob` | todas | sáb 14/11, 11h |
| 42 | feat: avalia o modelo com rigor e calcula o custo da fraude | Lucas | `feature/42-avaliacao-e-custo` | — | sex 13/11, 19h |
| 67 | docs: explica privacidade e experiência do associado | Lucas | `feature/67-privacidade` | #62 | sáb 14/11, 11h |
| 32 | docs: atualiza o README e propõe os textos de entrega | Lucas | `feature/32-readme-e-textos` | todas | sáb 14/11, 12h |
| 65 | feat: redige a mensagem ao associado com o watsonx.ai | Pedro Muller | `feature/65-mensagem-pela-ia` | #62, watsonx.ai | sáb 14/11, 11h |
| 46 | (execução) compara a auditoria por IA com o modelo | Pedro Muller | `feature/46-rodar-ia-contra-modelo` | watsonx.ai | sáb 14/11, 11h |
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

O contrato (R1) é fechado primeiro. Depois, as duas trilhas correm em paralelo e sem revisão de código (cada uma integra o próprio PR com o CI verde) e não tocam nos
mesmos arquivos: o **site** é feito contra os mocks e a **API**, contra os testes do contrato.

| Trilha | Dono | Pastas |
| --- | --- | --- |
| Site | Pedro Muller | `web/` (menos as pastas da R11) |
| API | Bruno | `src/`, `tests/`, e as pastas da R11 em `web/` |

Cada Issue vira uma branch `feature/<n>-<slug>` a partir de `refatoracao`, com PR para
`refatoracao` (nunca para `develop`). O CI "Qualidade" roda nesses PRs. O passo a passo de cada
Issue está no fim deste arquivo e na própria Issue do GitHub.

## Prioridade 1 (entra na entrega se ficar pronta até domingo, 14h)

| Id | Título | Dono | Depende de |
| --- | --- | --- | --- |
| R0 | design: protótipo de alta fidelidade (`docs/prototipo/`) — **feito** | Pedro Muller | — |
| #90 (R1) | docs: fecha o contrato das rotas novas (ESPECIFICACAO, tipos e mocks) | Pedro Muller | protótipo |
| #91 (R2) | feat: aplica a identidade Sicredi e cria as molduras e o login simulado | Pedro Muller | #90 |
| #92 (R3) | feat: cria o domínio, as portas e os adaptadores em memória | Bruno | #90 |
| #93 (R4) | feat: cria a tela inicial e o extrato do associado | Pedro Muller | #91 |
| #94 (R5) | feat: cria as rotas do associado | Bruno | #92 |
| #95 (R6) | feat: cria o simular compra, o aviso e o "não reconheço" | Pedro Muller | #93 |
| #96 (R7) | feat: cria as rotas da filial | Bruno | #94 |
| #97 (R8) | feat: cria a fila do auditor e o painel da compra na filial | Pedro Muller | #95 |
| #98 (R9) | feat: calcula as métricas do gerente | Bruno | #96 |
| #99 (R10) | feat: cria o painel do gerente | Pedro Muller | #97 |
| #100 (R11) | feat: leva "Desempenho" e "Como funciona" para a área da filial | Bruno | #91, #98 |
| #101 (R12) | test: integra o site com a API e confere tudo com o watsonx.ai | os dois | #99, #100 |
| #127 (R19) | feat: guarda os rótulos de retorno para o retreino do modelo | Bruno | #94 |

## Prioridade 2 (ações do auditor)

| Id | Título | Dono | Depende de |
| --- | --- | --- | --- |
| #102 (R13) | feat: auditor bloqueia compra que aguarda confirmação (API) | Bruno | #96 |
| #103 (R14) | feat: auditor bloqueia compra que aguarda confirmação (site) | Pedro Muller | #97, #102 |
| #104 (R15) | feat: mostra bloqueios por auditor e quantos estavam certos | os dois | #102, #103 |

O bloqueio registra o nome do auditor, a data e o motivo (explicação da IA mais uma nota dele). Se
o associado responder "fui eu", a compra é liberada sozinha e o bloqueio conta como incorreto.

## Prioridade 3 (chat)

| Id | Título | Dono | Depende de |
| --- | --- | --- | --- |
| #105 (R16) | feat: chat do associado com a IA (API, watsonx.ai) | Bruno | #94 |
| #106 (R17) | feat: chat do associado e "conversar com gerente" (site) | Pedro Muller | #93, #105 |

A IA só informa: resume os gastos e explica, em termos genéricos, as compras bloqueadas do próprio
associado. "Conversar com gerente" abre a mesma conversa com um resumo da sessão e para aí
(simulado).

## Prioridade 4

| Id | Título | Dono | Depende de |
| --- | --- | --- | --- |
| #107 (R18) | feat: persiste em Postgres por um adaptador novo | a definir | #92 |

---

# Refatoração: passo a passo de cada Issue

## #90 (R1) — docs: fecha o contrato das rotas novas da refatoração

**Dono:** Pedro Muller · **Trilha:** Site (`web/`) · **Prioridade:** P1 · **Depende de:** nenhuma · **Branch:** `feature/90-contrato` (a partir de `refatoracao`)

### Objetivo

Escrever, antes de qualquer código, o contrato das rotas novas. É ele que deixa as duas trilhas trabalharem em paralelo: o site usa os mocks e a API usa os testes de contrato. Depois do merge desta Issue, um campo só muda com o acordo das duas trilhas. Não há revisão de código: cada trilha integra o próprio PR depois do CI verde.

### Arquivos

- `ESPECIFICACAO.md` (seção 17, nova)
- `web/lib/tipos.ts` (tipos novos, no fim do arquivo)
- `web/lib/mocks/refatoracao.ts` (novo)
- `tests/test_contrato_refatoracao.py` (novo)

### Passo a passo

1. Crie a seção 17 da `ESPECIFICACAO.md`, "Associado e filial". Para cada rota abaixo, escreva: método, caminho, cabeçalho, corpo de entrada, corpo de saída com o tipo de cada campo, e os códigos de erro.
2. **Sessão.** `GET /api/sessao/perfis` devolve `{perfis: [{id_perfil, nome, papel, filial: {id_filial, nome}}]}`, com `papel` em `associado`, `auditor` ou `gerente`. `POST /api/sessao` recebe `{id_perfil}` e devolve `{token, perfil}`; perfil desconhecido dá 404. Todas as rotas abaixo exigem o cabeçalho `X-Sessao: <token>`: sem ele, 401; com papel errado, 403.
3. **Início do associado.** `GET /api/associado/inicio` devolve `{associado: {nome, filial}, saldo, limite_total, limite_disponivel, cartoes: [{id, tipo, final, bloqueado}], pendentes: [{id_notificacao, id_compra, valor, data_hora}], ultimas_compras: [CompraExtrato]}` (as 3 mais recentes).
4. **Extrato.** `GET /api/associado/extrato?situacao=` devolve `{total, itens: [CompraExtrato]}`, da mais nova para a mais antiga. `CompraExtrato` = `{id_compra, estabelecimento, data_hora, valor, tipo_transacao, final_cartao, situacao, id_notificacao}`, com `situacao` em `APROVADA`, `AGUARDANDO`, `BLOQUEADA` ou `CONTESTADA`.
5. **Detalhe da compra.** `GET /api/associado/compras/{id_compra}` devolve `CompraExtrato` mais `{bloqueio: {por, em, motivo} | null, resposta_associado: {resposta, em} | null, pode_contestar}`. `por` é `"Sentinela"` ou `"Analista da agência <nome>"`; `motivo` é sempre o texto genérico. Compra de outro associado dá 404.
6. **Simular compra.** `POST /api/associado/compras` recebe `{cartao, estabelecimento, data_hora}` mais os campos de `EntradaAnalise` (seção 12), exceto `credito`, `tipo_transacao` e `auditar` e devolve 201 com `{compra: CompraExtrato, id_notificacao}`. Cartão bloqueado dá 409.
7. **Contestação.** `POST /api/associado/compras/{id_compra}/contestacao` devolve 201 com `{compra, cartao_bloqueado: true}`. Só vale para compra `APROVADA`; nos outros casos, 409.
8. **Aviso "Foi você?".** Continua nas rotas atuais `GET /api/notificacoes/{id}` e `POST /api/notificacoes/{id}/resposta` (seção 15). Escreva que a resposta agora também muda a situação da compra: "fui eu" vira `APROVADA`; "não fui eu" vira `BLOQUEADA`.
9. **Fila da filial.** `GET /api/filial/fila?situacao=` devolve `{filial, total, itens: [{id_compra, nota, decisao, associado, final_cartao, data_hora, valor, situacao, veredito_ia}]}`, só com a carteira da filial da sessão. `associado` é o nome abreviado ("Ana S.").
10. **Compra na filial.** `GET /api/filial/compras/{id_compra}` devolve `{compra, sinais, contribuicoes, explicacao, auditoria, associado: {nome_abreviado, final_cartao, historico: {compras_90d, valor_mediano, contestacoes}}, resposta_associado, bloqueio}`. Nunca devolve saldo, limite nem o extrato. Compra de outra filial dá 403.
11. **Métricas do gerente.** `GET /api/filial/metricas` devolve `{filial, periodo, totais: {compras, aprovadas, confirmacoes, bloqueadas, valor_protegido}, por_tipo: [{tipo_transacao, modalidade, aprovadas, confirmacoes, bloqueadas}], acerto_modelo: {alertas_certos, alertas_desnecessarios, sem_resposta, taxa}, fraudes_aprovadas: {total, itens}, tempo_resposta_mediano_s}`. Só para o papel `gerente`.
12. Escreva na seção 17 as regras de negócio: saldo (débito desconta o saldo, crédito consome o limite, bloqueada ou aguardando não mexe), identificadores públicos opacos (nunca `id_cartao`, `id_cliente` ou `id_estabelecimento` da base) e a divisão da carteira entre as duas filiais.
13. Em `web/lib/tipos.ts`, crie um tipo para cada corpo de saída, com os mesmos nomes de campo.
14. Em `web/lib/mocks/refatoracao.ts`, crie um mock para cada rota, com os dados do protótipo (`docs/prototipo/index.html`): Ana Souza, Agência Centro, saldo R$ 4.820,35 e as seis compras do extrato.
15. Em `tests/test_contrato_refatoracao.py`, crie um teste por rota que chama a rota com o `TestClient` e confere o código e as chaves do corpo. Cada teste se pula sozinho enquanto a rota não existe (confere `app.openapi()`); quem fizer a rota não precisa mexer no arquivo.

### Pronto quando

- A seção 17 descreve todas as rotas acima, com tipos e erros.
- `npm run typecheck` passa com os tipos e os mocks novos.
- `pytest -q -rs` mostra os testes de contrato como pulados, com o motivo.

**Fora desta Issue:** Implementar qualquer rota ou tela.

## #91 (R2) — feat: aplica a identidade Sicredi e cria as molduras e o login simulado

**Dono:** Pedro Muller · **Trilha:** Site (`web/`) · **Prioridade:** P1 · **Depende de:** #90 · **Branch:** `feature/91-identidade-sicredi` (a partir de `refatoracao`)

### Objetivo

Trocar a cara do site pela identidade da Sicredi e criar a estrutura das duas áreas: a moldura do associado (celular), a moldura da filial (desktop) e a tela de entrada.

### Arquivos

- `web/app/layout.tsx`, `web/app/globals.scss`, `web/app/page.tsx`
- `web/styles/sicredi.scss` (novo: cores, fontes, raios e sombras)
- `web/public/logo-sicredi.png` e `web/public/logo-sicredi-branco.png` (cópias de `docs/prototipo/`)
- `web/components/layout/MolduraAssociado.tsx` e `MolduraFilial.tsx` (novos); `Shell.tsx` sai
- `web/app/entrar/page.tsx` (novo)
- `web/lib/sessao.ts` (novo), `web/lib/api.ts` (funções de sessão), `web/lib/textos.ts`
- `web/tests/sessao.test.tsx` (novo)

### Passo a passo

1. Leia `web/AGENTS.md` antes de começar: o Next.js 16 difere do que os modelos conhecem.
2. Abra o protótipo (`docs/prototipo/index.html`, aba "Guia de estilo"). Ele é a referência de cores, tamanhos e espaçamentos.
3. Em `web/styles/sicredi.scss`, declare as variáveis do protótipo: verde `#3FA110`, verde de ação `#33820D`, verde escuro `#146E37`, fundo verde `#ECF6E7`, texto `#323C32`, texto de apoio `#5A645A`, amarelo `#FFCD00` e magenta `#E60050`.
4. Em `web/app/layout.tsx`, carregue as fontes com `next/font/google`: Exo 2 (títulos, itálico 600 e 700) e Nunito (texto, 400 a 800).
5. Em `web/app/globals.scss`, sobreponha os tokens do Carbon para que botões, links e foco usem o verde de ação. Botão com texto branco usa `#33820D`, nunca `#3FA110` (contraste).
6. Copie os dois logos para `web/public/`. Use o colorido em fundo branco e o branco em fundo verde. Não altere cor nem proporção do logo.
7. Crie `MolduraAssociado`: coluna de até 420 px centralizada, com a barra de navegação embaixo (Início, Extrato, Comprar, Chat).
8. Crie `MolduraFilial`: menu lateral com o logo, o nome da agência, os links e, embaixo, o nome e o papel de quem entrou. Os links mudam com o papel (auditor ou gerente).
9. Em `web/lib/api.ts`, crie `obterPerfis()` e `entrar(idPerfil)`. Em `web/lib/sessao.ts`, guarde `{token, perfil}` no `sessionStorage` e exponha `obterSessao()`, `sair()` e um hook `useSessao()`. Toda chamada nova à API envia o cabeçalho `X-Sessao`.
10. Crie `/entrar`: lista os perfis de `obterPerfis()`, agrupados por papel; ao escolher e clicar em "Entrar", guarda a sessão e leva o associado para `/associado` e o auditor ou gerente para `/filial`.
11. `/` passa a redirecionar para `/entrar`. As páginas de `/associado` e `/filial` redirecionam para `/entrar` quando não há sessão ou o papel não serve.
12. Mova a fila atual de `/` para `/filial/fila` dentro da `MolduraFilial`, sem mudar o conteúdo (ele é refeito na Issue da fila do auditor). As páginas `/simulador`, `/respostas`, `/desempenho` e `/como-funciona` continuam funcionando dentro da moldura nova.
13. Teste: a tela de entrada mostra os perfis do mock; entrar como associado leva a `/associado`; sem sessão, `/filial` leva a `/entrar`.

### Pronto quando

- Com `NEXT_PUBLIC_USAR_MOCK=1 npm run dev`, a tela de entrada fica igual à tela 1 do protótipo.
- Nenhuma tela usa mais a cor azul do Carbon em botão, link ou foco.
- Os testes antigos do site continuam passando.

**Fora desta Issue:** As telas internas do associado e da filial (Issues seguintes).

## #92 (R3) — feat: cria o domínio, as portas e os adaptadores em memória

**Dono:** Bruno · **Trilha:** API (`src/` e `tests/`) · **Prioridade:** P1 · **Depende de:** #90 · **Branch:** `feature/92-dominio-e-portas` (a partir de `refatoracao`)

### Objetivo

Criar a base das regras novas com inversão de dependências: o domínio conhece só interfaces; o armazenamento em memória é um adaptador que depois pode ser trocado por Postgres sem mexer nas regras.

### Arquivos

- `src/dominio/` (novo): `entidades.py`, `regras.py`
- `src/portas/repositorios.py` (novo)
- `src/adaptadores/memoria/` (novo): `repositorios.py`, `dados_demo.py`
- `src/composicao.py` (novo: monta os repositórios usados pela API)
- `tests/test_dominio.py` (novo)

### Passo a passo

1. Em `src/dominio/entidades.py`, crie dataclasses para `Filial`, `Funcionario` (papel `auditor` ou `gerente`), `Associado`, `Cartao` (tipo, final, bloqueado), `Compra` (com `situacao`) e `Contestacao`. Use identificadores públicos opacos (por exemplo `asc-01`, `car-01`, `cmp-000001`); o identificador da base fica num campo interno que nunca sai pela API.
2. Em `src/dominio/regras.py`, escreva funções puras: `situacao_inicial(decisao)` (APROVAR vira `APROVADA`, PEDIR_CONFIRMACAO vira `AGUARDANDO`, BLOQUEAR vira `BLOQUEADA`), `aplicar_no_saldo(associado, cartao, compra)` (débito desconta o saldo, crédito consome o limite, só para `APROVADA`), `aplicar_resposta(compra, resposta)` e `contestar(compra, cartao)`.
3. Em `src/portas/repositorios.py`, declare um `Protocol` por repositório: `RepositorioFiliais`, `RepositorioPerfis`, `RepositorioAssociados`, `RepositorioCartoes`, `RepositorioCompras` e `RepositorioContestacoes`. Cada um só com os métodos que as regras usam (`obter`, `listar_por_...`, `salvar`).
4. Em `src/adaptadores/memoria/repositorios.py`, implemente cada porta com dicionários e um `threading.Lock`.
5. Em `src/adaptadores/memoria/dados_demo.py`, monte os dados fictícios: 2 filiais ("Agência Centro" e "Agência Norte"), cada uma com 1 gerente, 2 auditores e 5 associados com nome, saldo e limite inventados.
6. Ligue cada associado com login a um cliente real de março: ordene os clientes de março pela quantidade de compras (maior primeiro, desempate pelo identificador) e pegue os 10 primeiros, alternando entre as filiais. Os cartões saem dos cartões desse cliente; o `final` é inventado.
7. Divida a carteira: ordene todos os clientes de março pelo identificador; posição par vai para a Agência Centro e posição ímpar, para a Agência Norte. Cliente sem login aparece na filial como "Associado 0421" (número da posição).
8. Em `src/composicao.py`, crie `obter_repositorios()`, que devolve os adaptadores em memória já carregados. É o único lugar que importa adaptadores.
9. Testes: as regras de saldo e de situação; a divisão da carteira (as duas metades diferem em no máximo 1 cliente); e um teste de arquitetura que falha se algo em `src/dominio/` ou `src/portas/` importar `pandas`, `fastapi` ou `src.adaptadores`.

### Pronto quando

- `src/dominio/` e `src/portas/` não importam adaptadores, pandas nem FastAPI (teste de arquitetura).
- Os testes trocam um repositório por um dublê sem tocar nas regras.
- Nenhum identificador da base aparece em log, exceção ou objeto público.
- O núcleo (`src/agente.py`, `src/preparar_dados.py`, `src/treinar_modelo.py`) não foi alterado.

**Fora desta Issue:** Rotas da API (Issues seguintes) e Postgres.

## #93 (R4) — feat: cria a tela inicial e o extrato do associado

**Dono:** Pedro Muller · **Trilha:** Site (`web/`) · **Prioridade:** P1 · **Depende de:** #91 · **Branch:** `feature/93-inicio-e-extrato` (a partir de `refatoracao`)

### Objetivo

Criar as telas 2 (Início), 3 (Extrato) e 6 (Detalhe da compra) do protótipo, contra os mocks.

### Arquivos

- `web/app/associado/page.tsx` (substitui a lista de avisos atual)
- `web/app/associado/extrato/page.tsx` e `web/app/associado/compras/[id]/page.tsx` (novos)
- `web/components/associado/` (componentes novos: `CartaoSaldo`, `Atalhos`, `ItemCompra`, `ListaCompras`, `EtiquetaSituacao`, `DetalheCompra`)
- `web/lib/api.ts` (`obterInicio`, `obterExtrato`, `obterCompra`), `web/lib/textos.ts`, `web/lib/formatacao.ts`
- `web/tests/associado.test.tsx`

### Passo a passo

1. Em `web/lib/api.ts`, crie `obterInicio()`, `obterExtrato(situacao?)` e `obterCompra(id)`, no mesmo padrão das funções atuais (mock quando `NEXT_PUBLIC_USAR_MOCK=1`).
2. Crie `EtiquetaSituacao`: `APROVADA` verde, `AGUARDANDO` amarela ("Aguardando você"), `BLOQUEADA` e `CONTESTADA` magenta. Os textos ficam em `web/lib/textos.ts`.
3. Início: cabeçalho verde com o logo branco e "Olá, <nome>"; cartão com saldo e limite disponível (com a barra); quatro atalhos (Simular compra, Extrato, Chat e Investir, este desabilitado); aviso amarelo para cada compra pendente, com o botão "Responder"; e as 3 últimas compras.
4. Extrato: filtros Todas, Aprovadas, Aguardando e Bloqueadas; lista agrupada por mês; valor riscado nas bloqueadas. Tocar numa compra abre o detalhe.
5. Detalhe: valor, quando, cartão e situação. Se bloqueada, mostra "Bloqueada por", "Em" e "Motivo". Se houve resposta do associado, mostra a faixa com a resposta e a hora.
6. Trate os três estados em cada tela com os componentes de `web/components/comuns/`: carregando, erro e vazio.
7. Testes: o início mostra saldo, limite e o aviso pendente; o filtro "Bloqueadas" mostra só as bloqueadas; o detalhe de uma bloqueada mostra quem bloqueou e o motivo genérico.

### Pronto quando

- As três telas ficam iguais ao protótipo em 375 px de largura.
- Nenhum texto técnico (sinais, nota, parecer da IA) aparece na área do associado.
- Navegar pela barra de baixo não recarrega a página.

**Fora desta Issue:** Simular compra, responder ao aviso e contestar (Issue seguinte).

## #94 (R5) — feat: cria as rotas do associado

**Dono:** Bruno · **Trilha:** API (`src/` e `tests/`) · **Prioridade:** P1 · **Depende de:** #92 · **Branch:** `feature/94-rotas-do-associado` (a partir de `refatoracao`)

### Objetivo

Implementar a sessão simulada e as rotas do associado da seção 17: início, extrato, detalhe, simular compra e contestação. A compra simulada passa pelo Sentinela.

### Arquivos

- `src/api/sessao.py` e `src/api/rotas_associado.py` (novos)
- `src/api/esquemas_refatoracao.py` (novo)
- `src/aplicacao/associado.py` (novo: casos de uso)
- `src/api/app.py` (só `include_router` e a ligação da resposta do aviso com a compra)
- `tests/test_rotas_associado.py` (novo) e `tests/test_contrato_refatoracao.py` (só leitura: é a régua)

### Passo a passo

1. Em `src/api/sessao.py`, crie as rotas `GET /api/sessao/perfis` e `POST /api/sessao` e uma dependência do FastAPI `sessao_com_papel(*papeis)`, que lê `X-Sessao`, devolve o perfil e responde 401 ou 403. O token é um `uuid4` guardado em memória.
2. Em `src/aplicacao/associado.py`, escreva os casos de uso recebendo os repositórios por parâmetro (nunca importando adaptadores): `ver_inicio`, `ver_extrato`, `ver_compra`, `simular_compra` e `contestar_compra`.
3. Extrato: junte as compras de março do cliente ligado ao associado (situação calculada uma vez, na subida da API, com `servicos.analisar_transacao`) com as compras simuladas na sessão.
4. `simular_compra`: monte a transação com os campos de `EntradaAnalise` e chame `servicos.analisar_transacao`; grave a `Compra` com `situacao_inicial(decisao)`; se `APROVADA`, aplique no saldo; se `AGUARDANDO` ou `BLOQUEADA`, chame `notificacoes.criar_notificacao` e guarde o `id_notificacao` na compra. Cartão bloqueado responde 409.
5. `contestar_compra`: só para `APROVADA`; grava a `Contestacao`, muda a compra para `CONTESTADA`, bloqueia o cartão e devolve o valor ao saldo ou ao limite.
6. Resposta do aviso: na rota atual `POST /api/notificacoes/{id}/resposta`, depois de `notificacoes.responder`, chame `aplicar_resposta` na compra ligada ("fui eu" aprova e aplica no saldo; "não fui eu" bloqueia). O corpo da resposta da rota não muda.
7. O detalhe da compra devolve sempre o motivo genérico ("A compra fugiu do seu padrão de uso e foi bloqueada por segurança."). Nada de sinais, nota ou parecer da IA nestas rotas.
8. Em `src/api/app.py`, acrescente só `app.include_router(...)` para os dois arquivos novos.
9. Testes: cada rota com sucesso e com cada erro do contrato; saldo antes e depois de uma compra aprovada no débito e no crédito; "fui eu" numa compra aguardando; contestação bloqueando o cartão; e nenhum campo `id_cartao`, `id_cliente` ou `id_estabelecimento` da base em nenhuma resposta.
10. Confira que os testes destas rotas em `tests/test_contrato_refatoracao.py` deixaram de ser pulados e passam (eles se ativam sozinhos quando a rota existe).

### Pronto quando

- Os testes de contrato destas rotas passam sem pulo.
- `tests/test_conformidade_*.py` continuam verdes, sem alteração.
- Uma compra simulada aparece no extrato na mesma hora, com a situação certa.

**Fora desta Issue:** Rotas da filial.

## #95 (R6) — feat: cria o simular compra, o aviso e o "não reconheço" do associado

**Dono:** Pedro Muller · **Trilha:** Site (`web/`) · **Prioridade:** P1 · **Depende de:** #93 · **Branch:** `feature/95-simular-compra-e-aviso` (a partir de `refatoracao`)

### Objetivo

Criar as telas 4 (Simular compra) e 5 (Foi você?) do protótipo e o botão "Não reconheço esta compra".

### Arquivos

- `web/app/associado/comprar/page.tsx` e `web/app/associado/avisos/[id]/page.tsx` (novos)
- `web/components/associado/` (`FormularioCompra`, `CenariosCompra`, `ResultadoCompra`, `ConfirmarCompra`, `BotaoContestar`)
- `web/lib/api.ts` (`simularCompra`, `contestarCompra`), `web/lib/simulacao.ts`, `web/lib/textos.ts`
- `web/app/simulador/` e `web/components/simulador/` (saem no fim)
- `web/tests/associado.test.tsx`, `web/tests/simulador.test.tsx`

### Passo a passo

1. Em `web/lib/api.ts`, crie `simularCompra(entrada)` e `contestarCompra(id)`.
2. Formulário: cartão (lista dos cartões do início), valor, hora, estabelecimento, modalidade, país do acesso e compras no último minuto. Reaproveite os campos e os valores padrão de `web/components/simulador/ControlesSimulador.tsx` e de `web/lib/simulacao.ts`.
3. Cenários prontos em cima do formulário: "Compra comum", "Madrugada no exterior" e "Várias seguidas". Cada um preenche todos os campos de uma vez.
4. Ao enviar: `APROVADA` mostra a faixa verde e o saldo novo; `AGUARDANDO` mostra a faixa amarela e o botão que leva ao aviso; `BLOQUEADA` mostra a faixa magenta com o motivo genérico. Cartão bloqueado (409) mostra a mensagem "Este cartão está bloqueado".
5. Tela do aviso: a mensagem do Sicredi, valor, quando e cartão, e os botões "Fui eu" e "Não fui eu". Use as funções atuais `obterNotificacao` e `responderNotificacao`. Depois da resposta, volte ao detalhe da compra.
6. No detalhe de uma compra `APROVADA` com `pode_contestar`, mostre "Não reconheço esta compra". O clique abre uma confirmação ("O cartão será bloqueado e a sua agência será avisada") e só então chama `contestarCompra`.
7. Apague `/simulador` e os componentes que ficarem sem uso; mova os testes que ainda valem para `associado.test.tsx`.
8. Testes: cada cenário preenche o formulário; cada situação mostra a faixa certa; "Não fui eu" leva ao detalhe com a compra bloqueada; a contestação pede confirmação antes de chamar a API.

### Pronto quando

- As telas ficam iguais ao protótipo em 375 px.
- Dá para fazer o fluxo inteiro só com o teclado.
- O rodapé do aviso diz que o Sicredi nunca pede senha, código ou link.

**Fora desta Issue:** Chat.

## #96 (R7) — feat: cria as rotas da filial

**Dono:** Bruno · **Trilha:** API (`src/` e `tests/`) · **Prioridade:** P1 · **Depende de:** #94 · **Branch:** `feature/96-rotas-da-filial` (a partir de `refatoracao`)

### Objetivo

Implementar a fila e o detalhe da compra para auditor e gerente, só com a carteira da filial e dentro da LGPD.

### Arquivos

- `src/api/rotas_filial.py` (novo)
- `src/aplicacao/filial.py` (novo: casos de uso)
- `src/api/esquemas_refatoracao.py`
- `tests/test_rotas_filial.py` (novo) e `tests/test_contrato_refatoracao.py`

### Passo a passo

1. `GET /api/filial/fila`: junte as linhas da fila de demonstração (`servicos.obter_fila`) cujo cliente é da carteira da filial com as compras simuladas que não foram aprovadas e com as contestadas. Ordene pela nota, da maior para a menor. Aceite o filtro `situacao`.
2. Cada item leva o nome abreviado do associado ("Ana S." ou "Associado 0421"), o final do cartão, a situação e o veredito da IA quando já houver auditoria.
3. `GET /api/filial/compras/{id_compra}`: reaproveite `servicos.obter_transacao` para sinais, contribuições, explicação e auditoria. Troque o perfil pelo bloco `associado` do contrato: nome abreviado, final do cartão e histórico agregado (compras em 90 dias, valor mediano e contestações).
4. Garanta que estas rotas nunca devolvem saldo, limite, extrato, nome completo do associado nem identificador da base.
5. Compra de outra filial responde 403; compra inexistente, 404. Papel `associado` responde 403.
6. Inclua `resposta_associado` (resposta e hora) e `bloqueio` (quem, quando e motivo) no detalhe.
7. Testes: a fila da Agência Centro e a da Agência Norte não têm nenhuma compra em comum e, somadas, dão a fila inteira; 403 para outra filial; ausência dos campos proibidos; uma compra simulada que pediu confirmação aparece na fila da filial certa.

### Pronto quando

- Os testes de contrato destas rotas passam sem pulo.
- As rotas antigas `/api/fila` e `/api/transacoes/{id}` continuam iguais.

**Fora desta Issue:** Métricas e ações do auditor.

## #97 (R8) — feat: cria a fila do auditor e o painel da compra na filial

**Dono:** Pedro Muller · **Trilha:** Site (`web/`) · **Prioridade:** P1 · **Depende de:** #95 · **Branch:** `feature/97-fila-do-auditor` (a partir de `refatoracao`)

### Objetivo

Criar a tela "Filial: auditor" do protótipo: a fila da agência e o painel da compra com o detalhe técnico.

### Arquivos

- `web/app/filial/page.tsx` e `web/app/filial/fila/page.tsx`
- `web/components/fila/` e `web/components/painel/` (ajustes de dados e de estilo)
- `web/lib/api.ts` (`obterFilaFilial`, `obterCompraFilial`), `web/lib/textos.ts`
- `web/tests/fila.test.tsx`, `web/tests/perfil.test.tsx`

### Passo a passo

1. Em `web/lib/api.ts`, crie `obterFilaFilial(situacao?)` e `obterCompraFilial(id)`.
2. `/filial` leva o auditor para `/filial/fila` e o gerente para `/filial/painel`.
3. Tabela: colunas Nota, Associado (nome abreviado e final do cartão), Quando, Valor, Situação e IA. Filtros Todas, Bloqueadas, Aguardando associado e Contestadas. A linha escolhida fica com fundo verde claro.
4. Painel da compra, nesta ordem: cabeçalho (associado, situação, valor, nota e quando), sinais de alerta, o que pesou na nota, parecer da IA, resposta do associado e histórico agregado. Reaproveite `PainelTransacao`, `GraficoContribuicoes` e `RelatorioAuditoria`.
5. Troque `PerfilAssociado` e `HistoricoCartao` pelo bloco agregado do contrato (compras em 90 dias, valor mediano e contestações). O auditor não vê saldo nem extrato.
6. Mantenha a auditoria por IA como está hoje (dispara ao abrir a compra e mostra a fonte "watsonx.ai" ou "modo local").
7. Leve a página "Respostas dos associados" para `/filial/respostas`, dentro da moldura.
8. Testes: a tabela mostra o nome abreviado; o filtro funciona; o painel não mostra saldo; a resposta "Não fui eu" aparece como "Fraude provável".

### Pronto quando

- A tela fica igual ao protótipo em 1440 px e continua usável em 1024 px.
- O botão "Bloquear compra" não aparece nesta Issue (é da prioridade 2).

**Fora desta Issue:** Bloqueio pelo auditor e painel do gerente.

## #98 (R9) — feat: calcula as métricas do gerente

**Dono:** Bruno · **Trilha:** API (`src/` e `tests/`) · **Prioridade:** P1 · **Depende de:** #96 · **Branch:** `feature/98-metricas-do-gerente` (a partir de `refatoracao`)

### Objetivo

Implementar `GET /api/filial/metricas` com os números do painel do gerente, por filial.

### Arquivos

- `src/aplicacao/metricas_filial.py` (novo)
- `src/api/rotas_filial.py`, `src/api/esquemas_refatoracao.py`
- `tests/test_metricas_filial.py` (novo) e `tests/test_contrato_refatoracao.py`

### Passo a passo

1. `totais`: compras de março da carteira mais as simuladas; quantas aprovadas, com pedido de confirmação e bloqueadas; `valor_protegido` é a soma das bloqueadas.
2. `por_tipo`: uma linha por combinação de `tipo_transacao` (crédito ou débito) e modalidade (com ou sem cartão presente), com as três contagens.
3. `acerto_modelo`: entre os avisos enviados, `alertas_certos` são as respostas "não fui eu"; `alertas_desnecessarios`, as "fui eu"; `sem_resposta`, o resto. `taxa` = certos ÷ (certos + desnecessários), ou `null` sem respostas.
4. `fraudes_aprovadas`: as contestações da carteira, com associado abreviado, final do cartão, quando e valor.
5. `tempo_resposta_mediano_s`: mediana, em segundos, entre a criação do aviso e a resposta; `null` sem respostas.
6. Calcule a parte de março uma vez, na subida da API, e some a parte ao vivo a cada chamada. A rota tem de responder em menos de 200 ms.
7. Só o papel `gerente` acessa; `auditor` e `associado` recebem 403.
8. Testes: as contagens das duas filiais somadas dão os números da ESPECIFICACAO, seção 11 (13.395 aprovadas, 159 confirmações e 54 bloqueadas); depois de um "não fui eu", `alertas_certos` sobe 1; depois de uma contestação, `fraudes_aprovadas.total` sobe 1.

### Pronto quando

- O teste de contrato da rota passa sem pulo.
- A soma das duas filiais bate com as invariantes da seção 11.

**Fora desta Issue:** Métricas por auditor (prioridade 2).

## #99 (R10) — feat: cria o painel do gerente

**Dono:** Pedro Muller · **Trilha:** Site (`web/`) · **Prioridade:** P1 · **Depende de:** #97 · **Branch:** `feature/99-painel-do-gerente` (a partir de `refatoracao`)

### Objetivo

Criar a tela "Filial: gerente" do protótipo com as métricas da agência.

### Arquivos

- `web/app/filial/painel/page.tsx` (novo)
- `web/components/gerente/` (novo: `IndicadoresAgencia`, `DecisoesPorTipo`, `AcertoModelo`, `FraudesAprovadas`)
- `web/lib/api.ts` (`obterMetricasFilial`), `web/lib/textos.ts`
- `web/tests/gerente.test.tsx` (novo)

### Passo a passo

1. Em `web/lib/api.ts`, crie `obterMetricasFilial()`.
2. Quatro indicadores no topo: aprovadas, pedidos de confirmação, bloqueadas (com o valor protegido) e tempo de resposta do associado.
3. "Decisões por tipo de compra": uma barra empilhada por linha de `por_tipo`, com verde (aprovadas), amarelo (confirmações) e magenta (bloqueadas), o total à direita e a legenda embaixo. Dê a cada barra um texto alternativo com os três números.
4. "Acerto do modelo": a rosca com a taxa e, ao lado, as três frases (alerta certo, alerta desnecessário e sem resposta). Sem respostas, mostre "Ainda não há respostas" no lugar da rosca.
5. "Fraudes que o modelo aprovou": o total e a lista das contestações.
6. O cartão "Bloqueios da equipe" não entra nesta Issue (prioridade 2).
7. O menu lateral do gerente mostra: Painel da agência, Fila de alertas, Desempenho e Como funciona.
8. Testes: os indicadores mostram os números do mock; sem respostas aparece o estado vazio; um auditor que abre `/filial/painel` é levado para `/filial/fila`.

### Pronto quando

- A tela fica igual ao protótipo em 1440 px.
- Os gráficos não dependem só da cor: cada um tem legenda e números.

**Fora desta Issue:** Bloqueios por auditor.

## #100 (R11) — feat: leva "Desempenho" e "Como funciona" para a área da filial

**Dono:** Bruno · **Trilha:** API (`src/` e `tests/`) · **Prioridade:** P1 · **Depende de:** #91, #98 · **Branch:** `feature/100-desempenho-na-filial` (a partir de `refatoracao`)

### Objetivo

Mover as duas páginas para dentro da área da filial e revisar o conteúdo para a história nova (associado e filial).

### Arquivos

- `web/app/filial/desempenho/page.tsx` e `web/app/filial/como-funciona/page.tsx` (novos)
- `web/app/desempenho/` e `web/app/como-funciona/` (saem)
- `web/components/desempenho/` e `web/components/como-funciona/`
- `web/lib/textos.ts` (só as chaves destas duas páginas)
- `web/tests/desempenho.test.tsx`

### Passo a passo

1. Leia `web/AGENTS.md` antes de começar.
2. Crie as duas rotas novas dentro da `MolduraFilial` e apague as antigas.
3. "Desempenho": mantenha a comparação com o sistema atual, os detalhes do modelo, os custos e a tabela IA contra modelo. Troque as cores dos gráficos pelas variáveis de `web/styles/sicredi.scss`.
4. "Como funciona": reescreva em quatro passos, na ordem do produto novo: 1) o associado faz a compra; 2) o Sentinela decide na hora; 3) a IA audita e o associado confirma; 4) a filial acompanha. Frases curtas, sem jargão.
5. Confira que os links do menu lateral (auditor e gerente) apontam para as rotas novas.
6. Atualize os testes das duas páginas para os caminhos e os textos novos.

### Pronto quando

- As duas páginas abrem pelo menu da filial e não existem mais em `/desempenho` e `/como-funciona`.
- Os números mostrados são os mesmos de antes (vêm de `/api/metricas`).

**Fora desta Issue:** Mexer em outras pastas de `web/` (são da trilha Site).

## #101 (R12) — test: integra o site com a API e confere tudo com o watsonx.ai

**Dono:** os dois · **Trilha:** API (`src/` e `tests/`) · **Prioridade:** P1 · **Depende de:** #99, #100 · **Branch:** `feature/101-integracao` (a partir de `refatoracao`)

### Objetivo

Rodar o site contra a API real, sem mocks, e conferir o fluxo inteiro antes da linha de corte (domingo, 14h).

### Arquivos

- Correções pequenas nos arquivos das Issues anteriores
- `README.md` (seção "Como rodar" e descrição das duas áreas)
- `docs/arquitetura.md` (diagrama com as duas áreas e as portas)

### Passo a passo

1. Suba a API (`uvicorn src.api.app:app --port 8000`) com o `.env` ativo e o site (`cd web && npm run dev`) sem `NEXT_PUBLIC_USAR_MOCK`.
2. Roteiro 1: entre como Ana Souza; confira saldo e extrato; simule "Compra comum" e veja o saldo cair.
3. Roteiro 2: simule "Madrugada no exterior"; responda "Não fui eu" no aviso; confira a compra bloqueada no extrato, com o motivo genérico.
4. Roteiro 3: entre como auditor da Agência Centro; ache a compra do roteiro 2 na fila; confira sinais, parecer da IA com a fonte "watsonx.ai" e "Fraude provável".
5. Roteiro 4: entre como auditor da Agência Norte e confira que a compra da Ana não aparece.
6. Roteiro 5: volte como Ana; conteste a compra do roteiro 1; confira o cartão bloqueado e uma nova compra recusada.
7. Roteiro 6: entre como gerente da Agência Centro; confira que o acerto do modelo e as fraudes aprovadas refletem os roteiros 2 e 5.
8. Rode os dois portões completos e `python -m src.avaliar_agente`.
9. Atualize o `README.md` e o `docs/arquitetura.md`.
10. Às 14h de domingo, mostre o estado ao Pedro Muller. Ele decide se a `refatoracao` entra no `develop`.

### Pronto quando

- Os seis roteiros passam sem erro no console do navegador nem na API.
- Os dois portões e as invariantes da seção 11 estão verdes.

**Fora desta Issue:** Funcionalidades novas.

## #127 (R19) — feat: guarda os rótulos de retorno para o retreino do modelo

**Dono:** Bruno · **Trilha:** API (`src/` e `tests/`) · **Prioridade:** P1 · **Depende de:** #94 · **Branch:** `feature/127-rotulos-retreino` (a partir de `refatoracao`)

### Objetivo

Toda resposta do associado vira um rótulo que pode retreinar o modelo, mas hoje ela fica só em memória e some quando a API reinicia. Esta Issue grava, a cada evento, o que o modelo viu, o que decidiu e o que o associado disse, num repositório só de acréscimo pensado para o retreino. O retreino em si fica fora (o campeão não muda nesta entrega).

### Arquivos

- `ESPECIFICACAO.md` (seção 17.7, nova)
- `src/dominio/rotulos.py` (novo: o evento e a regra do rótulo)
- `src/portas/repositorios.py` (só a porta `RepositorioRotulos`)
- `src/adaptadores/memoria/` e `src/adaptadores/arquivo/rotulos.py` (novo)
- `src/composicao.py`, `src/config.py` (só `CAMINHO_ROTULOS`)
- `src/aplicacao/associado.py` e `src/aplicacao/filial.py` (só as chamadas que gravam o evento)
- `src/exportar_retreino.py` (novo)
- `.gitignore` (só `data/rotulos_retreino.csv` e `data/retreino.parquet`)
- `tests/test_rotulos.py` (novo)

### Passo a passo

1. Escreva a seção 17.7 da `ESPECIFICACAO.md` com o formato do evento, a tabela de rótulos e o script de exportação, como abaixo.
2. Em `src/dominio/rotulos.py`, crie a dataclass `EventoRotulo` com: `registrado_em`, `origem` (`resposta_aviso`, `contestacao` ou `bloqueio_auditor`), `id_compra` (opaco), `id_transacao` (só para compras de março; `None` nas simuladas), `simulada`, `nota`, `decisao_modelo`, `situacao`, `resposta` (`sim`, `nao` ou `None`), `rotulo` (`fraude`, `legitima` ou `None`), `data_hora`, `valor`, `tipo_transacao`, `modalidade_transacao` e as 11 variáveis de `VARIAVEIS_MODELO` (os valores que o modelo realmente usou).
3. Ainda em `rotulos.py`, crie a função pura `rotulo_do_evento(origem, resposta)`: resposta "nao" → `fraude`; resposta "sim" → `legitima`; contestação → `fraude` (fraude que o modelo aprovou); bloqueio do auditor sem resposta → `None`. Evento sem rótulo também é gravado (serve para medir quanto fica sem resposta).
4. Em `src/portas/repositorios.py`, crie a porta `RepositorioRotulos` com só dois métodos: `acrescentar(evento)` e `listar()`. Nada de editar ou apagar: é um histórico.
5. Crie dois adaptadores: em memória (para os testes) e em arquivo (`src/adaptadores/arquivo/rotulos.py`), que acrescenta uma linha por evento em `data/rotulos_retreino.csv` (caminho em `src/config.py`, `CAMINHO_ROTULOS`), com cabeçalho na primeira vez e escrita protegida por `threading.Lock`. Em `src/composicao.py`, a API usa o de arquivo.
6. Grave o evento nos três momentos: quando o associado responde ao aviso (em `src/aplicacao/associado.py`, junto de `aplicar_resposta`), quando contesta uma compra e quando o auditor bloqueia (em `src/aplicacao/filial.py`, Issue #102). As variáveis vêm da transação que foi analisada: guarde-as na `Compra` no momento da análise, para não ter de recalcular.
7. Privacidade: o evento nunca leva nome, `id_cartao`, `id_cliente` nem `id_estabelecimento`. Confira com um teste que as colunas do CSV não incluem nenhuma delas.
8. Crie `src/exportar_retreino.py` (`python -m src.exportar_retreino`): lê os eventos, descarta os sem rótulo, fica com o último evento de cada `id_compra` e grava `data/retreino.parquet` com as 11 variáveis, `valor`, `data_hora` e a coluna `rotulo_retorno` (1 = fraude, 0 = legítima). No fim, imprime quantos eventos leu, quantos rótulos de fraude e de legítima exportou e quantos ficaram sem rótulo.
9. Ponha `data/rotulos_retreino.csv` e `data/retreino.parquet` no `.gitignore`: são dados gerados na hora, não vão para o repositório.
10. Testes: a tabela de rótulos; o último evento vence na exportação; os eventos sobrevivem a recriar o adaptador de arquivo (simula reiniciar a API); responder a um aviso pela rota grava um evento com as variáveis; nenhuma coluna proibida no CSV.

### Pronto quando

- Depois de reiniciar a API, os eventos de antes continuam em `data/rotulos_retreino.csv`.
- `python -m src.exportar_retreino` gera uma base que `src/treinar_modelo.py` conseguiria ler (mesmas variáveis e nomes).
- Nenhum identificador nem nome no CSV ou no parquet.
- `src/treinar_modelo.py`, `src/agente.py` e `modelos/` não foram alterados; `python -m src.avaliar_agente` mostra os mesmos números.

**Fora desta Issue:** Retreinar ou trocar o modelo; tela nova no site; o adaptador Postgres (Issue #107, que deve implementar esta mesma porta).

## #102 (R13) — feat: auditor bloqueia compra que aguarda confirmação (API)

**Dono:** Bruno · **Trilha:** API (`src/` e `tests/`) · **Prioridade:** P2 · **Depende de:** #96 · **Branch:** `feature/102-bloqueio-do-auditor-api` (a partir de `refatoracao`)

### Objetivo

Deixar o auditor bloquear uma compra que ainda espera o associado, com nome, data e motivo registrados.

### Arquivos

- `ESPECIFICACAO.md` (seção 17), `src/dominio/`, `src/portas/repositorios.py`, `src/adaptadores/memoria/`
- `src/aplicacao/filial.py`, `src/api/rotas_filial.py`, `tests/test_rotas_filial.py`

### Passo a passo

1. Acrescente ao contrato `POST /api/filial/compras/{id_compra}/bloqueio`, com `{nota}` (texto opcional, até 300 caracteres), só para o papel `auditor`.
2. Só vale para compra `AGUARDANDO` da própria filial; nos outros casos, 409 ou 403.
3. Grave o bloqueio com o auditor, a data e o motivo: a explicação da IA (se já houver auditoria) mais a nota do auditor.
4. A compra vira `BLOQUEADA`. Para o associado, `bloqueio.por` é "Analista da agência <nome>" e o motivo é o genérico; para a filial, o nome completo e o motivo inteiro.
5. Se depois o associado responder "fui eu", a compra é liberada sozinha (`APROVADA`, aplica no saldo) e o bloqueio fica marcado como incorreto; "não fui eu" marca como correto.
6. Testes para cada regra acima.

### Pronto quando

- O associado nunca recebe o nome do auditor.
- A liberação automática aplica o saldo uma única vez.

**Fora desta Issue:** Tela do bloqueio.

## #103 (R14) — feat: auditor bloqueia compra que aguarda confirmação (site)

**Dono:** Pedro Muller · **Trilha:** Site (`web/`) · **Prioridade:** P2 · **Depende de:** #97, #102 · **Branch:** `feature/103-bloqueio-do-auditor-site` (a partir de `refatoracao`)

### Objetivo

Pôr no painel da compra o botão "Bloquear compra" e mostrar quem bloqueou.

### Arquivos

- `web/components/painel/`
- `web/components/associado/DetalheCompra.tsx`
- `web/lib/api.ts`, `web/lib/tipos.ts`, `web/lib/mocks/refatoracao.ts`, `web/lib/textos.ts`
- `web/tests/fila.test.tsx`

### Passo a passo

1. Em `web/lib/api.ts`, crie `bloquearCompra(id, nota)`.
2. No painel, o botão "Bloquear compra" aparece só para o auditor e só em compra `AGUARDANDO`.
3. O clique abre uma janela com o campo de nota (opcional) e a frase "O associado verá que a compra foi bloqueada por um analista da agência".
4. Depois do bloqueio, o painel mostra "Bloqueada por <nome completo>", a data e o motivo inteiro.
5. No detalhe do associado, a mesma compra mostra "Analista da agência <nome>" e o motivo genérico.
6. Testes: o botão some para o gerente e para compra já decidida; a janela exige confirmação.

### Pronto quando

- Fica igual ao protótipo.
- O nome completo do auditor nunca aparece na área do associado.

**Fora desta Issue:** Métricas por auditor.

## #104 (R15) — feat: mostra os bloqueios por auditor e quantos estavam certos

**Dono:** os dois · **Trilha:** API (`src/` e `tests/`) · **Prioridade:** P2 · **Depende de:** #102, #103 · **Branch:** `feature/104-metricas-por-auditor` (a partir de `refatoracao`)

### Objetivo

Acrescentar ao painel do gerente o cartão "Bloqueios da equipe".

### Arquivos

- `ESPECIFICACAO.md` (seção 17)
- `src/aplicacao/metricas_filial.py`, `tests/test_metricas_filial.py` (trilha API)
- `web/components/gerente/BloqueiosEquipe.tsx`, `web/tests/gerente.test.tsx` (trilha Site)

### Passo a passo

1. Acrescente a `GET /api/filial/metricas` o bloco `bloqueios_por_auditor: [{auditor, bloqueios, corretos, liberados_depois}]`.
2. "Correto" é o bloqueio em que o associado respondeu "não fui eu"; "liberado depois" é o que o associado respondeu "fui eu".
3. No site, crie a tabela do protótipo, com a explicação de "correto" embaixo.
4. Testes nas duas trilhas.

### Pronto quando

- A tabela bate com os bloqueios feitos no roteiro de teste.

**Fora desta Issue:** Classificação ou comparação entre auditores.

## #105 (R16) — feat: cria o chat do associado com a IA (API)

**Dono:** Bruno · **Trilha:** API (`src/` e `tests/`) · **Prioridade:** P3 · **Depende de:** #94 · **Branch:** `feature/105-chat-api` (a partir de `refatoracao`)

### Objetivo

Criar o chat em que a IA responde sobre os gastos e as compras bloqueadas do próprio associado. A IA só informa; não executa ações.

### Arquivos

- `ESPECIFICACAO.md` (seção 18, nova)
- `src/associado/chat.py` (novo), `src/api/rotas_associado.py`
- `tests/test_chat.py` (novo)

### Passo a passo

1. Escreva o contrato: `POST /api/associado/chat` com `{mensagem}` devolve `{resposta, fonte}`; `POST /api/associado/chat/gerente` devolve `{resumo}`.
2. Monte o contexto só com dados do próprio associado: totais por mês e por tipo, as 20 últimas compras e as bloqueadas com o motivo genérico. Nunca envie identificadores, sinais, nota ou parecer da IA.
3. Chame `watsonx.redigir_texto` com instruções fixas: responder só sobre os dados enviados, em português, em até 400 caracteres, sem pedir senha ou código e sem prometer liberar ou bloquear nada.
4. Sem credenciais ou em caso de falha, responda com um texto fixo que resume os gastos do mês (`fonte: "local"`).
5. `/chat/gerente` devolve um resumo da conversa até ali, para abrir a conversa com o gerente. A conversa com o gerente é simulada e para no resumo.
6. Testes com o watsonx simulado: o pedido não leva identificadores; pergunta fora do assunto recebe a recusa padrão; o modo local funciona sem credenciais.

### Pronto quando

- Nenhum identificador nem detalhe técnico sai no pedido ou na resposta.
- Sem `.env`, o chat responde no modo local.

**Fora desta Issue:** Conversa real com o gerente; ações pela IA.

## #106 (R17) — feat: cria o chat do associado e o "conversar com gerente" (site)

**Dono:** Pedro Muller · **Trilha:** Site (`web/`) · **Prioridade:** P3 · **Depende de:** #93, #105 · **Branch:** `feature/106-chat-site` (a partir de `refatoracao`)

### Objetivo

Criar a tela de chat do associado.

### Arquivos

- `docs/prototipo/index.html` (tela do chat)
- `web/app/associado/chat/page.tsx` (novo), `web/components/associado/Chat.tsx`
- `web/lib/api.ts`, `web/lib/tipos.ts`, `web/lib/mocks/refatoracao.ts`, `web/lib/textos.ts`
- `web/tests/chat.test.tsx` (novo)

### Passo a passo

1. Desenhe a tela no protótipo e peça o aceite do Pedro Muller antes de programar.
2. Tela: lista de mensagens, campo de texto e três sugestões ("Quanto gastei este mês?", "Por que minha compra foi bloqueada?", "Quais compras estão pendentes?").
3. Mostre "digitando" enquanto a resposta não chega (o watsonx leva alguns segundos) e a fonte da resposta.
4. Botão "Conversar com gerente": troca o cabeçalho para o nome do gerente da agência, mostra o resumo como primeira mensagem e avisa que a conversa é simulada.
5. Testes: enviar mensagem, sugestão, erro da API e a troca para o gerente.

### Pronto quando

- A conversa some ao sair (não é gravada).
- O aviso de conversa simulada aparece.

**Fora desta Issue:** Histórico de conversas.

## #107 (R18) — feat: persiste os dados em Postgres por um adaptador novo

**Dono:** a definir · **Trilha:** API (`src/` e `tests/`) · **Prioridade:** P4 · **Depende de:** #92 · **Branch:** `feature/107-postgres` (a partir de `refatoracao`)

### Objetivo

Trocar o armazenamento em memória por Postgres, sem mudar o domínio nem as rotas.

### Arquivos

- `src/adaptadores/postgres/` (novo)
- `src/composicao.py`
- `docker-compose.yml`, `.env.example`
- `tests/test_adaptador_postgres.py` (novo)
- `docs/decisoes.md` (ADR novo)

### Passo a passo

1. Registre a decisão num ADR: biblioteca de acesso, migrações e como os testes rodam.
2. Crie as tabelas de filiais, perfis, associados, cartões, compras, contestações, bloqueios e avisos.
3. Implemente cada porta de `src/portas/repositorios.py` no adaptador novo.
4. Em `src/composicao.py`, escolha o adaptador pela variável `SENTINELA_ARMAZENAMENTO` (`memoria` é o padrão).
5. Rode a mesma bateria de testes dos repositórios contra os dois adaptadores.
6. Leve as notificações e as respostas do analista para o mesmo padrão de portas.

### Pronto quando

- Com `memoria`, nada muda.
- Com `postgres`, os dados sobrevivem a reiniciar a API.
- `src/dominio/` não foi alterado.

**Fora desta Issue:** Autenticação real.

---

## #108 — feat: aplica a identidade visual da Sicredi no site atual

**Dono:** Mariana · **Branch:** `feature/108-identidade-sicredi` (a partir de `develop`) · **Prazo:** dom 15/11, 12h

Hoje o site tem a cara padrão do IBM Carbon (azul, cinza, IBM Plex). Esta Issue troca a aparência pela identidade da Sicredi sem mudar nenhuma tela nem comportamento: cores, fontes, logo no cabeçalho e cores dos gráficos. Fonte das regras: https://marca.sicredi.com.br (páginas Cores, Tipografia e Logo).

- **Arquivos permitidos:** `web/app/layout.tsx` (fontes); `web/app/globals.scss` (bloco novo "Identidade Sicredi" logo depois de `@use "@carbon/react";` e troca das cores fixas azuis); `web/components/layout/Shell.tsx` (só o logo e o nome no cabeçalho); `web/components/comuns/FaixaDecisao.tsx`, `web/components/comuns/BarraNota.tsx`, `web/components/painel/GraficoContribuicoes.tsx`, `web/components/desempenho/ComparacaoSistemas.tsx` (só cores); `web/public/logo-sicredi.png` e `web/public/logo-sicredi-branco.png` (já estão no repositório; não altere).

**Passos**

1. Leia `web/AGENTS.md`: o Next.js 16 difere do que os modelos conhecem.
2. Em `web/app/globals.scss`, logo depois de `@use "@carbon/react";`, crie o bloco `// --- Identidade Sicredi ---` com estas variáveis em `:root`: `--sicredi-verde: #3FA110`, `--sicredi-verde-acao: #33820D`, `--sicredi-verde-acao-hover: #26610A`, `--sicredi-verde-escuro: #146E37`, `--sicredi-verde-fundo: #ECF6E7`, `--sicredi-texto: #323C32`, `--sicredi-texto-apoio: #5A645A`, `--sicredi-amarelo: #FFCD00`, `--sicredi-magenta: #E60050`.
3. No mesmo bloco, sobreponha os tokens do Carbon em `:root`: `--cds-interactive`, `--cds-button-primary`, `--cds-link-primary`, `--cds-focus`, `--cds-border-interactive` e `--cds-background-brand` recebem `var(--sicredi-verde-acao)`; `--cds-button-primary-hover` e `--cds-link-primary-hover` recebem `var(--sicredi-verde-acao-hover)`; `--cds-text-primary` recebe `var(--sicredi-texto)`; `--cds-text-secondary` recebe `var(--sicredi-texto-apoio)`.
4. Ainda em `globals.scss`, troque os valores de reserva azuis (`#0f62fe`) pelas variáveis da Sicredi.
5. Em `web/app/layout.tsx`, carregue com `next/font/google` a fonte `Nunito` (pesos 400, 600, 700 e 800) para o texto e `Exo_2` (pesos 600 e 700, estilos normal e itálico) para os títulos. Exponha as duas como variáveis CSS (`--fonte-texto` e `--fonte-titulo`) no `<body>`.
6. Em `globals.scss`, aplique `font-family: var(--fonte-texto)` em `body` e nos componentes do Carbon (`.cds--content, .cds--header, .cds--side-nav, .cds--data-table, .cds--btn, .cds--label, .cds--tag`), e `font-family: var(--fonte-titulo); font-style: italic; font-weight: 700` em `h1` e `h2`.
7. Em `Shell.tsx`, troque o texto "Sentinela" do cabeçalho por `<img src="/logo-sicredi.png" alt="Sicredi" height={28}>` seguido do texto "Sentinela". Não estique nem recolora o logo.
8. Cores das decisões em todo o site: BLOQUEAR usa `--sicredi-magenta`, PEDIR_CONFIRMACAO usa `--sicredi-amarelo` (com texto escuro `#5A3C1E` em cima dele) e APROVAR usa `--sicredi-verde`. Ajuste `FaixaDecisao` e `BarraNota`.
9. Barras dos gráficos (`GraficoContribuicoes` e `ComparacaoSistemas`): Sentinela em `--sicredi-verde`, sistema atual em `--sicredi-texto-apoio`, contribuições que aumentam o risco em `--sicredi-magenta` e as que diminuem em `--sicredi-verde`.
10. Rode o site (`npm run dev`) e passe por todas as páginas procurando azul do Carbon que tenha sobrado (botões, links, abas, foco do teclado, caixas de seleção, barra de rolagem do controle deslizante).

**Aceite:** Nenhum azul do Carbon em botão, link, foco, seleção ou gráfico, em nenhuma página. Botão primário com texto branco usa `#33820D` (o verde `#3FA110` com texto branco não tem contraste suficiente). Títulos em Exo 2 itálico e textos em Nunito. O PR tem prints de antes e depois da Fila, do Desempenho e do App do associado. Os testes do site continuam passando sem alteração.

**Fora desta Issue:** Mudar layout, textos ou comportamento; responsividade (Issue #48).

## #48 — fix: corrige a acessibilidade e a responsividade do site

**Dono:** Lucas · **Branch:** `feature/48-acessibilidade` (a partir de `develop`) · **Prazo:** dom 15/11, 12h

Em telas pequenas o site fica inutilizável: em 375 px o menu lateral fica sempre aberto, ocupa metade da tela e espreme o conteúdo (o título "Fila de alertas" quebra em três linhas e o App do associado fica cortado). Esta Issue faz o site funcionar em celular, tablet e com zoom de 200%, e corrige os problemas de acessibilidade.

- **Arquivos permitidos:** `web/components/layout/Shell.tsx`; `web/app/globals.scss` (bloco novo `// --- Responsividade (Issue #48) ---` no fim do arquivo e ajustes nas regras de grade existentes); `web/components/**` (só atributos de acessibilidade: `aria-*`, `alt`, rótulos, ordem de foco); `web/tests/` (testes novos de acessibilidade).

**Passos**

1. Antes de mudar algo, rode o Lighthouse (aba Accessibility do Chrome) em cada página (`/`, `/desempenho`, `/como-funciona`, `/simulador`, `/respostas`, `/associado`) e abra também em 375 px, 768 px e com zoom de 200%. Registre as notas e os problemas num comentário desta Issue.
2. Menu: em `Shell.tsx`, use o padrão do Carbon `HeaderMenuButton` + `SideNav` com `expanded` controlado por estado. Abaixo de 1056 px o menu começa fechado e abre pelo botão; ao escolher uma página, fecha. Acima de 1056 px fica como hoje.
3. Fila e painel (`.sentinela-fila`): abaixo de 1056 px as duas colunas viram uma só, com o painel abaixo da tabela.
4. Tabelas (fila, respostas, desempenho): envolva cada uma num contêiner com `overflow-x: auto`, para rolar de lado em vez de espremer as colunas.
5. App do associado: abaixo de 480 px a moldura do celular some e o conteúdo ocupa a largura toda.
6. Simulador: abaixo de 1056 px os controles e o resultado ficam um embaixo do outro.
7. Acessibilidade: todo campo com rótulo visível; todo gráfico com texto alternativo que diga os números; estados (decisão, situação) não podem depender só da cor (precisam de texto ou ícone); foco visível em todos os elementos clicáveis.
8. Faça um commit por problema corrigido.
9. Refaça o Lighthouse e cole as notas novas na descrição do PR.

**Aceite:** Lighthouse Accessibility ≥ 90 em todas as páginas. Nada cortado nem sobreposto em 375 px, 768 px e com zoom de 200%. Dá para usar o menu e responder a um aviso no App do associado só com o teclado. Os testes do site continuam passando.

**Fora desta Issue:** Cores e fontes (Issue da identidade Sicredi).

## #109 — feat: mostra quando o aviso ao associado foi redigido pelo IBM Granite

**Dono:** Lucas · **Branch:** `feature/109-selo-granite` (a partir de `develop`) · **Prazo:** dom 15/11, 12h

Desde a #65, a mensagem ao associado pode ser redigida pelo IBM Granite (watsonx.ai) ou vir do modelo fixo. A API já devolve isso no campo `fonte_mensagem` ("watsonx" ou "modelo"), mas o site não mostra. Esta Issue mostra a origem no App do associado e no painel da transação, o que também ajuda no vídeo.

- **Arquivos permitidos:** `web/components/associado/ItemNotificacao.tsx`; `web/components/painel/PainelTransacao.tsx` (só o bloco "Associado"); `web/lib/textos.ts` (só os blocos "App do associado" e "Associado" do painel); `web/lib/mocks/index.ts` (um aviso com cada fonte); `web/tests/associado.test.tsx`.

**Passos**

1. Confira o campo `fonte_mensagem` em `web/lib/tipos.ts` (tipo `FonteMensagem`) e na ESPECIFICACAO, seção 15.
2. Em `ItemNotificacao.tsx`, mostre abaixo da mensagem uma etiqueta discreta (`Tag` do Carbon, tamanho `sm`): "Redigida pelo IBM Granite" quando `fonte_mensagem` for "watsonx" e "Mensagem padrão" quando for "modelo". Os textos ficam em `textos.ts`.
3. Lembre que a mensagem pode trocar depois de alguns segundos: o aviso nasce com o modelo fixo e o Granite melhora o texto em segundo plano. Se a lista de avisos já é atualizada de tempos em tempos, a etiqueta acompanha; se não é, acrescente uma atualização a cada 5 segundos enquanto houver aviso "aguardando" com `fonte_mensagem` "modelo", parando depois de 30 segundos.
4. No bloco "Associado" do painel da transação, mostre a mesma etiqueta ao lado do status do aviso.
5. Nos mocks, deixe um aviso com cada fonte.
6. Testes: a etiqueta certa para cada fonte; a etiqueta muda quando o mock passa de "modelo" para "watsonx".

**Aceite:** Com a API real e o `.env` ativo, um aviso novo aparece primeiro com "Mensagem padrão" e, em alguns segundos, com "Redigida pelo IBM Granite". Sem o `.env`, aparece só "Mensagem padrão" e nada quebra.

**Fora desta Issue:** Mudar a API ou o texto da mensagem.

## #110 — feat: adiciona cenários prontos ao simulador "e se"

**Dono:** Pedro Machado · **Branch:** `feature/110-cenarios-simulador` (a partir de `develop`) · **Prazo:** dom 15/11, 12h

Hoje, para ver o Sentinela bloquear ou pedir confirmação no simulador, é preciso mexer em vários campos. Esta Issue cria três botões de cenário que preenchem tudo de uma vez, o que deixa a demonstração (e o vídeo) rápida e previsível.

- **Arquivos permitidos:** `web/components/simulador/ControlesSimulador.tsx`, `web/components/simulador/SimuladorTransacao.tsx`; `web/lib/simulacao.ts` (valores de cada cenário); `web/lib/textos.ts` (só o bloco do simulador); `web/tests/simulador.test.tsx`.

**Passos**

1. Leia `web/lib/simulacao.ts` e `ControlesSimulador.tsx` para entender os campos (valor, velocidades, hora, risco do estabelecimento, IP, cartão presente etc.).
2. Em `web/lib/simulacao.ts`, crie a constante `CENARIOS` com três itens, cada um com um nome, uma frase curta e o valor de **todos** os campos do simulador: "Compra comum" (tarde, valor baixo, cartão presente, IP conhecido, sem rajada); "Madrugada no exterior" (3h da manhã, sem cartão presente, IP de país desconhecido, valor médio, sem rajada); "Rajada de compras" (madrugada, várias transações no último minuto e na última hora, sem cartão presente).
3. Em cima dos controles, mostre os três cenários como botões (`Button` do Carbon, `kind="tertiary"`, tamanho `sm`), com a frase como dica. Ao clicar, todos os campos recebem os valores do cenário e a análise roda de novo, como acontece hoje ao mudar um campo.
4. Mantenha o botão (ou ação) que volta aos valores da transação original da fila.
5. Ajuste os valores rodando com a API real até que: "Compra comum" dê APROVAR, "Madrugada no exterior" dê PEDIR_CONFIRMACAO ou BLOQUEAR, e "Rajada de compras" dê BLOQUEAR.
6. Testes: cada botão preenche os campos com os valores de `CENARIOS`; os três botões têm nome acessível.

**Aceite:** Com a API real, os três cenários dão as decisões descritas no passo 5. Os cenários funcionam também com `NEXT_PUBLIC_USAR_MOCK=1`.

**Fora desta Issue:** Mudar o modelo, os limiares ou a API.

## #111 — docs: atualiza a arquitetura e os requisitos com o estado final

**Dono:** Pedro Machado · **Branch:** `feature/111-docs-estado-final` (a partir de `develop`) · **Prazo:** dom 15/11, 12h

A arquitetura e o mapa de requisitos foram escritos antes das últimas entregas (mensagem pelo Granite na #65, comparação IA × modelo na #46, privacidade na #67). Esta Issue confere cada afirmação contra o código e os JSONs de `modelos/` e atualiza os dois documentos, que os avaliadores vão ler.

- **Arquivos permitidos:** `docs/arquitetura.md`; `docs/requisitos.md`.

**Passos**

1. Leia o `README.md`, a `ESPECIFICACAO.md` (seções 12 a 15) e `docs/privacidade.md`: eles já estão atualizados e são a referência.
2. Em `docs/arquitetura.md`: confira que o diagrama mostra o site, a API, o núcleo, a auditoria e o canal do associado, e que o canal também chama o watsonx.ai (mensagem pelo Granite, em segundo plano). Descreva o fluxo de uma compra suspeita do começo ao fim: decisão na hora → aviso ao associado (modelo fixo e, depois, o texto do Granite se passar nas regras) → auditoria em paralelo → resposta do associado → painel do analista.
3. Em `docs/requisitos.md`: para cada item do desafio, uma linha com "como atendemos" e "onde está" (arquivo ou página do site). Inclua a comparação IA × modelo (`modelos/ia_contra_modelo.json`: 254 compras, recall de 100% nos dois, precisão de 96,4% contra 44,3%) e a mensagem pelo Granite.
4. Todo número citado tem de sair de um arquivo do repositório (`modelos/*.json` ou a saída de `python -m src.avaliar_agente`). Não invente nem arredonde diferente do README.
5. Procure menções a Streamlit e Ollama: fora de `docs/decisoes.md` (que guarda o histórico das decisões) elas não podem existir nestes dois arquivos.
6. Escreva em português simples, frases curtas, sem jargão sem explicação.

**Aceite:** Todos os números batem com o README e com `modelos/*.json`. Nenhuma menção a Streamlit ou Ollama nos dois arquivos. O portão Python continua verde (nenhum código foi alterado).

**Fora desta Issue:** Alterar o README, a ESPECIFICACAO ou qualquer código.

## #112 — fix: mostra a latência em segundos e padroniza os números do Desempenho

**Dono:** Mariana · **Branch:** `feature/112-numeros-desempenho` (a partir de `develop`) · **Prazo:** dom 15/11, 12h

Na página Desempenho, a tabela "Modelo e IA lado a lado" mostra o tempo da IA como "6.061,7 ms", que é difícil de ler e esconde a comparação principal (milissegundos contra segundos). Esta Issue padroniza os números da página.

- **Arquivos permitidos:** `web/components/desempenho/SecaoIaContraModelo.tsx`; `web/components/desempenho/IndicadoresDesempenho.tsx`, `web/components/desempenho/SecaoCustos.tsx` (só formatação); `web/lib/formatacao.ts` (função nova); `web/tests/formatacao.test.ts`, `web/tests/desempenho.test.tsx`.

**Passos**

1. Em `web/lib/formatacao.ts`, crie `formatarDuracao(ms: number): string`: abaixo de 1.000 ms mostra em milissegundos com uma casa ("5,0 ms"); de 1.000 ms para cima, em segundos com uma casa ("6,1 s").
2. Em `SecaoIaContraModelo.tsx`, use `formatarDuracao` nas linhas de tempo e acrescente, abaixo da tabela, uma frase com a razão entre os tempos medianos ("A IA levou cerca de 1.200 vezes mais que o modelo"), calculada a partir dos dados, não escrita à mão.
3. Confira os outros números da página: porcentagens com uma casa e vírgula, valores em reais com `R$` e duas casas, contagens com ponto de milhar. Use sempre as funções de `formatacao.ts`.
4. Testes de `formatarDuracao` (999, 1.000, 6.061,7) e um teste da página com o texto "6,1 s".

**Aceite:** A tabela mostra "5,0 ms" para o modelo e "6,1 s" para a IA (dados atuais). Os números da página continuam iguais aos do README.

**Fora desta Issue:** Mudar o layout da página ou os dados da API.

## #66 — feat: cria o "Pergunte à IA sobre este caso" (extra)

**Dono:** Pedro Machado · **Branch:** `feature/66-pergunte-a-ia` (a partir de `develop`) · **Prazo:** dom 15/11, 12h

Extra, só depois das outras duas Issues do Pedro Machado. O analista faz uma pergunta livre sobre a transação aberta no painel e o IBM Granite responde usando as mesmas 5 ferramentas da auditoria. O contrato já está fechado na ESPECIFICACAO, seção 16, e o teste de conformidade já existe (hoje pulado).

- **Arquivos permitidos:** `src/auditoria/perguntas.py` (novo); `src/api/app.py` (só a rota nova) e `src/api/esquemas.py` (esquemas novos); `web/components/painel/PergunteIA.tsx` (novo) e `web/components/painel/PainelTransacao.tsx` (só para incluir o componente); `web/lib/api.ts`, `web/lib/tipos.ts`, `web/lib/mocks/index.ts`, `web/lib/textos.ts` (só o que for desta Issue); `tests/test_perguntas.py` (novo), `web/tests/pergunte.test.tsx` (novo).

**Passos**

1. Leia a ESPECIFICACAO, seção 16, e o teste pulado em `tests/test_conformidade_api.py` (procure por "perguntas"). **Não altere o teste de conformidade**: ele é a régua.
2. Em `src/auditoria/perguntas.py`, reaproveite `src/auditoria/watsonx.py` (`_chamar_chat`, as ferramentas de `ferramentas.py`) e o modo local de `local.py`. Com credenciais, o Granite responde à pergunta usando as ferramentas; sem credenciais, a resposta lista o resumo de cada ferramenta e diz que a IA está indisponível.
3. Crie a rota `POST /api/transacoes/{id_transacao}/perguntas` exatamente como a seção 16: pergunta de 1 a 300 caracteres (senão 422), transação fora da fila dá 404, resposta com `resposta`, `ferramentas_usadas`, `fonte` e `latencia_ms`.
4. A resposta nunca pode trazer identificador (cartão, cliente, estabelecimento), rótulo nem a decisão do sistema atual. Escreva um teste para isso.
5. No painel da transação, abaixo do relatório da IA, crie o bloco "Pergunte à IA sobre este caso": campo de texto, botão "Perguntar", indicador de carregamento (a resposta leva alguns segundos), a resposta, as ferramentas usadas e a fonte.
6. O teste de conformidade deixa de ser pulado sozinho quando a rota existe: rode `python -m pytest tests/test_conformidade_api.py -q -rs` e confira que ele **passa** (não aparece mais como pulado).

**Aceite:** O teste de conformidade das perguntas passa. Com o `.env`, uma pergunta real é respondida pelo watsonx.ai; sem ele, pelo modo local. Os dois portões (Python e site) estão verdes e `python -m src.avaliar_agente` mostra os mesmos números.

**Fora desta Issue:** Mudar a auditoria existente ou o modelo.
