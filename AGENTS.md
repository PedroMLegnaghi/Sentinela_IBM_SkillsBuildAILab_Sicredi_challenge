# AGENTS.md — Regras de trabalho do projeto Sentinela

O IBM Bob carrega este arquivo em toda tarefa. Ele define COMO trabalhar; O QUE construir está
nas fontes da seção 1. Se um prompt contradisser estas regras, pare e pergunte (seção 11).

## 1. Fontes da verdade (nesta ordem)

1. `AGENTS.md` — como trabalhar.
2. `ESPECIFICACAO.md` — dados, modelo, agente, API, auditoria, site e números esperados.
3. `docs/backlog.md` — as Issues: escopo, arquivos permitidos e critérios de aceite.
4. `docs/decisoes.md` — decisões já tomadas (ADRs). Não as reverta.
5. `docs/arquitetura.md` e `docs/requisitos.md`.

Os testes `tests/test_conformidade_nucleo.py` e `tests/test_conformidade_api.py` são do líder e
são a medida oficial de "pronto". Nunca edite esses testes, a ESPECIFICACAO, este arquivo nem
`docs/`, salvo quando a Issue mandar. Nunca invente coluna, arquivo, biblioteca, rota ou número
que não esteja nas fontes.

## 2. O projeto

Sentinela é um agente antifraude para compras com cartão (desafio Sicredi, IBM SkillsBuild). A API
calcula 9 sinais, dá uma nota de 0 a 100 (regressão logística) e decide na hora APROVAR,
PEDIR_CONFIRMACAO ou BLOQUEAR. Em paralelo, um agente no IBM watsonx.ai audita a decisão (confirma,
diverge ou inconclusivo) sem mudá-la, e o associado é avisado e confirma a compra pelo app. Um
analista revisa tudo num site Next.js. Dados 100% sintéticos, só na máquina de cada pessoa.

## 3. Protocolo de toda Issue

1. **Sincronizar:** `git switch develop && git pull`. Alterações locais não commitadas? Pare e pergunte.
2. **Branch:** `git switch -c feature/<numero>-<slug>`, com o nome exato do backlog.
3. **Ler** a Issue em `docs/backlog.md` e só os arquivos que ela lista.
4. **Ambiente:** Python do `.venv` da raiz (`.venv/bin/python`; Windows `.venv\Scripts\python`).
   O parquet de `data/` já vem no repositório. Para recriá-lo, descompacte o CSV
   (`gunzip -k data/*.csv.gz`) e rode `python -m src.preparar_dados`. Nunca rode
   `src.treinar_modelo` sem a Issue mandar.
5. **Planejar:** arquivos, funções, testes e verificação. Todos em "Arquivos permitidos"?
6. **Implementar** em passos pequenos (seções 5 a 9).
7. **Verificar** com o portão (seção 10) e os critérios de aceite. Falhou? Corrija a causa.
   Nunca altere critério, teste ou número esperado para passar.
8. **Commitar e enviar:** commits pequenos (seção 4) e `git push -u origin <branch>`.
9. **Relatar** (seção 12) e parar.

## 4. Git

- `main` recebe só a versão de entrega; `develop` é o alvo de todo PR; uma Issue, uma branch.
- Conventional Commits: prefixo em inglês, assunto em português, minúsculo, sem ponto final, até
  72 caracteres (`feat: cria o app do associado`).
- Proibido: `push --force`, `rebase` em branch compartilhada, commit direto em `main`/`develop`,
  `git add -A`, `git add .`, e adicionar a `data/` algo além dos 4 arquivos do ADR-016,
  `.venv/`, `node_modules/`, caches ou `.env`.
- Você não faz merge. Não há revisão por outra pessoa: o dono da Issue confere o portão na
  própria máquina (com `data/`), abre o PR e faz o merge com o CI verde.

## 5. Escopo

Altere só os "Arquivos permitidos". Problema fora do escopo vai para "Achados fora do escopo" no
relatório. Nada de funcionalidade que não esteja nos critérios de aceite.

## 6. Código

- **Idioma (ADR-001):** nomes, comentários, docstrings, logs e textos em português, sem acento em
  identificadores e nomes de arquivo; nunca misture idiomas num nome.
- **Python:** Black (100 colunas) e Ruff (`pyproject.toml`); `snake_case` com verbo para funções,
  `PascalCase` para classes, `UPPER_SNAKE_CASE` para constantes; tipos em toda função pública;
  limiares, caminhos e URLs em `src/config.py`; docstring Google em português (`Args`, `Returns`,
  `Raises`); comentário explica o porquê.
- **TypeScript (`web/`):** Next.js App Router, TypeScript estrito, Carbon (`@carbon/react`) — não
  troque nem acrescente biblioteca de UI. `camelCase` para funções, `PascalCase` para componentes e
  tipos; textos em `web/lib/textos.ts`, formatação em `web/lib/formatacao.ts`, chamadas à API só
  por `web/lib/api.ts` com os tipos de `web/lib/tipos.ts`. Sem `any` e sem `console.log`.
- **Tamanho:** função até 50 linhas; módulo e componente até cerca de 150. Passou, divida.
- Sem código morto, código comentado ou duplicação de regra do agente (importe de `src/`).

## 7. Erros e logs

- Nunca `except:` nem `except Exception:`; capture o tipo específico, trate ou registre em log.
- Logs com `logging.getLogger(__name__)`; `print` só nos scripts `python -m`.
- Erro para o usuário em português, dizendo o que aconteceu e o que fazer; nunca stack trace.

## 8. Dados, privacidade e segredos

- Do CSV, só as 16 colunas da ESPECIFICACAO, seção 4; nunca colunas pessoais nem proibidas (seção 5).
- Nunca abra, imprima ou cole linhas de `data/` (o `.bobignore` bloqueia); mostre só agregados.
- Logs, respostas da API e mensagens à IA nunca levam identificador de cartão, cliente ou
  estabelecimento.
- Testes só com valores inventados.
- O único segredo são as credenciais do watsonx.ai: só no `.env` (ignorado pelo Git);
  `.env.example` lista os nomes. Nunca escreva chave ou token em código, teste, log ou commit.

## 9. Testes

- Python: pytest; site: Vitest com os mocks de `web/lib/mocks/`, sem depender da API.
- Obrigatório testar regra de negócio, cálculo, validação e todo defeito corrigido.
- Nome do teste é uma frase; um comportamento por teste (Arranjo–Ação–Asserção).
- Sem depender de ordem, de `data/`, do Ollama ou do watsonx.ai (use `monkeypatch`/mocks).

## 10. Portão de qualidade (antes de todo commit)

```bash
python -m black --check .
python -m ruff check .
python -m pytest -q
```

Se mexeu em `web/`: `npm run lint`, `npm run typecheck`, `npm test` e `npm run build`, dentro de
`web/`. Depois, `python -m src.avaliar_agente` continua com os números da ESPECIFICACAO, seção 11.

- Conformidade sem falhas. Os dois arquivos são intocáveis: nada de
  `skip`, `xfail`, `-k`, `--deselect` ou configuração para escondê-los. Achou um teste que
  contradiz a ESPECIFICACAO? Pare e relate.
- O CI roda tudo, inclusive os testes com dados (o parquet é versionado); o portão local continua
  obrigatório antes do push.

## 11. Quando parar e perguntar

Fontes em conflito; arquivo fora da lista, biblioteca nova ou mudança de contrato da API;
número invariante mudou; teste que passava começou a falhar; alterações não commitadas,
conflito ou push recusado. Explique em até 5 linhas e proponha 2 opções.

## 12. Relatório final

1. Resumo em até 5 linhas.
2. Tabela `critério | esperado | obtido | OK?` (OK só com evidência).
3. A última linha REAL de cada comando do portão, com passed/failed/skipped.
4. Arquivos criados ou alterados.
5. Achados fora do escopo (ou "nenhum").
6. Título e corpo do PR (modelo de `.github/pull_request_template.md`, com `Closes #N`).

## 13. Economia de Bob Coins

Leia só o que a Issue lista; não abra `data/` nem binários; mostre só o fim das saídas longas;
uma sessão nova por Issue.
