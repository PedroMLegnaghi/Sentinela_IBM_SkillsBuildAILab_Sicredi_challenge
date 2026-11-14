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
