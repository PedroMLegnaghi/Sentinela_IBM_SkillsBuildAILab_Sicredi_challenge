# Como usamos o IBM Bob

O Sentinela foi construído por cinco pessoas, sem reuniões, em cerca de quatro dias. Para
trabalhar em paralelo com o IBM Bob sem perder a qualidade, transformamos o processo em
arquivos que o próprio Bob lê, e criamos uma régua de "pronto" que ele não pode alterar.
Os números deste documento vêm do GitHub (`gh pr list --state all`, `gh issue list`,
`gh run list`) em 14/11/2026.

## 1. O que o Bob lê

| Arquivo | Para quê |
| --- | --- |
| [`AGENTS.md`](../AGENTS.md) | Carregado pelo Bob em toda tarefa ([regras do Bob](https://bob.ibm.com/docs/ide/configuration/rules)). Traz o protocolo de 9 passos de uma Issue, padrões de código em português, regras de privacidade, o portão de qualidade e as situações em que o Bob deve parar e perguntar. |
| [`ESPECIFICACAO.md`](../ESPECIFICACAO.md) | O contrato: colunas permitidas e proibidas, os 9 sinais com limiares, a decisão, as rotas da API e os números exatos que o sistema tem de reproduzir. |
| [`docs/backlog.md`](backlog.md) | Cada Issue com "arquivos permitidos" e critérios de aceite. O Bob só altera o que a Issue lista. |
| [`.bobignore`](../.bobignore) | Impede as ferramentas de arquivo do Bob de abrir a base da Sicredi, o modelo e caches ([.bobignore](https://bob.ibm.com/docs/ide/configuration/bobignore)). Protege os dados e economiza Bob Coins; scripts e terminal continuam lendo. |
| [`.bob/custom_modes.yaml`](../.bob/custom_modes.yaml) | O modo personalizado **Auditor Sentinela** (seção 5). |

## 2. O ciclo de uma Issue

1. O líder escreve a Issue com dono, branch, prazo, arquivos permitidos, aceite e o prompt.
   15 Issues do GitHub trazem o prompt pronto no corpo.
2. O dono abre uma sessão nova do Bob, no modo **Agent**, e cola sempre o mesmo prompt:

   ```
   Execute a Issue #N do arquivo docs/backlog.md seguindo o protocolo da seção 3 do AGENTS.md.
   Comece pelo passo 1 e só pare no relatório final (seção 12) ou se uma regra da seção 11
   mandar parar.
   ```

3. O Bob sincroniza o `develop`, cria a branch, lê só os arquivos da Issue, implementa, roda o
   portão, faz os commits e o push e termina com um relatório: tabela "critério | esperado |
   obtido", a última linha real de cada comando e o texto do PR.
4. O dono confere o portão na própria máquina, abre o PR para `develop`, espera o CI verde e
   faz "Squash and merge".

Uma sessão nova por Issue e a leitura restrita aos arquivos listados economizam Bob Coins
(150 por pessoa, sem recarga).

## 3. A régua de "pronto" não é do Bob

O líder escreveu os testes de conformidade
([`tests/test_conformidade_nucleo.py`](../tests/test_conformidade_nucleo.py) e
[`tests/test_conformidade_api.py`](../tests/test_conformidade_api.py)). Eles conferem dados,
sinais, bordas da decisão, a reprodutibilidade do modelo e o contrato da API. O `AGENTS.md`
proíbe o Bob de alterá-los, de pulá-los ou de mexer na configuração para escondê-los.

O contrato fixo da API também permitiu trabalhar em paralelo: o site foi construído contra dados
simulados no mesmo formato (`web/lib/mocks/`) enquanto o backend era feito.

## 4. O que a régua pegou

| Quando | O que aconteceu | Como foi pego | Correção |
| --- | --- | --- | --- |
| 12/11 | A primeira versão do núcleo (Etapas 1 a 4) foi entregue como pronta | Conformidade: **18 falhas em 132 testes**; Black: 5 arquivos fora do padrão; Ruff: 56 erros | Issue #2 (PR #10): 0 falhas, portão limpo |
| 12/11 | Teste de fumaça da fila quebrava com os dados presentes | Portão local com `data/`; no CI, sem dados, o teste era pulado | PR #14 e, depois, dados versionados no repositório para o CI rodar tudo (PR #71) |
| 13/11 | Sem os dados, a API não carregava nem o modelo | CI de `develop` vermelho | PR #53 |
| 14/11 | Calibração deixava de fora as compras com nota 100 | Conferência dos totais do JSON (13.591 em vez de 13.608) | PR #80 |

Uma lição registrada no guia do time: o relatório do Bob chegou a trazer contagens de testes que
não batiam com a execução real. Por isso a regra é "só vale o que você viu na tela": o dono roda
o portão e cola a última linha real no PR, e o CI confirma.

## 5. Modo personalizado: Auditor Sentinela

O arquivo [`.bob/custom_modes.yaml`](../.bob/custom_modes.yaml) define o modo `auditor-sentinela`
([documentação de custom modes](https://bob.ibm.com/docs/ide/configuration/custom-modes)). Ele
só lê arquivos e roda comandos: roda o portão completo, confere as invariantes e o escopo de uma
branch e devolve uma tabela de achados, sem editar nada. Para usar: abrir o seletor de modos do
Bob e escolher "Auditor Sentinela".

## 6. Números do processo (14/11/2026)

| Item | Quantidade |
| --- | --- |
| Issues no GitHub | 51 |
| Pull Requests | 33 (32 integrados; o #18 é a publicação final em `main`) |
| Execuções do CI "Qualidade" | 93 (87 verdes, 4 vermelhas, 2 sem conclusão) |
| Testes Python | 335 passando, 1 pulado de propósito (Issue #66, extra) |
| Testes do site (Vitest) | 68 |

PRs por fase:

| Fase | PRs | O que entregou |
| --- | --- | --- |
| Padrões e núcleo | #9–#16, #36 | Kit de padrões, núcleo corrigido, primeira interface |
| Arquitetura web | #49–#59 | API FastAPI, auditoria no watsonx.ai, site Next.js + Carbon, simulador |
| Estrutura enxuta | #56, #68, #69, #71 | Streamlit aposentado, dados versionados |
| Associado e análises | #72–#78 | Canal e app do associado, explicabilidade, perfil, EDA, avaliação rigorosa, privacidade |
| Correções finais | #79, #80, #83, #84 | Feitas fora do Bob, para cumprir o prazo |

## 7. O que aprendemos

- **Escopo fechado rende mais.** Com "arquivos permitidos" e um aceite objetivo, o Bob entrega
  algo revisável; pedidos abertos geram mudanças espalhadas.
- **A régua precisa ser externa.** O Bob relatou sucesso nas Etapas 1 a 4; a conformidade
  mostrou 18 falhas. Testes que ele não pode tocar tornaram a revisão rápida e objetiva.
- **Regras escritas substituem reuniões.** `AGENTS.md`, ESPECIFICACAO e backlog deixaram cinco
  pessoas trabalharem em paralelo, cada uma com o seu Bob.
- **O CI precisa ver o que a máquina vê.** Testes pulados sem os dados esconderam um defeito;
  versionar os dados sintéticos fez o CI rodar tudo.
