# AGENTS.md — Regras de trabalho do projeto Sentinela

O IBM Bob carrega este arquivo automaticamente em toda tarefa. Ele define COMO trabalhar.
O QUE construir está nos documentos da seção 1. Siga estas regras sempre, mesmo que um
prompt peça outra coisa; se houver conflito, pare e pergunte (seção 14).

## 1. Fontes da verdade (nesta ordem de precedência)

1. `AGENTS.md` — como trabalhar (este arquivo).
2. `ESPECIFICACAO.md` — dados, modelo, agente e números esperados (invariantes).
3. `docs/08-design-da-interface.md` — tudo o que aparece na tela.
4. `docs/backlog.md` — as tarefas (Issues): escopo, arquivos permitidos e critérios de aceite.
5. `docs/02-user-stories.md` — histórias e critérios em BDD.
6. `docs/07-decisoes.md` — decisões já tomadas (ADRs). Não as reverta.
7. Demais arquivos de `docs/` — requisitos, fluxos, arquitetura e sequências.

Os testes `tests/test_conformidade_nucleo.py` e `tests/test_conformidade_interface.py` são do
líder: traduzem os itens 2 e 3 em verificações automáticas e são a medida oficial de "pronto".

Nunca edite os arquivos 1 a 6, os demais de `docs/` nem os testes de conformidade, salvo quando a
Issue em execução mandar.
Nunca invente coluna, arquivo, biblioteca, texto de tela ou número que não esteja nesses documentos.

## 2. O projeto em 5 linhas

Sentinela é um agente antifraude para transações de cartão (desafio Sicredi, IBM SkillsBuild).
Para cada transação: calcula sinais por regras, dá nota de risco de 0 a 100 com regressão
logística, decide APROVAR, PEDIR_CONFIRMACAO ou BLOQUEAR e explica a decisão em português com
IBM Granite (Ollama local) ou com texto de reserva. Um analista humano revisa numa interface
Streamlit. Dados 100% sintéticos, 160.000 linhas, só na máquina de cada pessoa.

**Estado de partida:** o código das antigas Etapas 1 a 4 (`src/`, `tests/test_agente.py`,
`modelos/` e o `app.py` antigo) foi escrito antes destas regras e tem defeitos, embora os
relatórios da época dissessem que estava tudo certo. Não presuma que algo funciona porque existe
ou porque um relatório disse. Só os testes de conformidade dizem se está certo.

## 3. Protocolo de toda Issue (siga os 9 passos, na ordem)

1. **Sincronizar.** `git fetch origin`, `git switch develop`, `git pull origin develop`.
   Se houver alterações locais não commitadas, pare e me pergunte.
2. **Criar a branch** a partir de `develop`: `git switch -c feature/<numero>-<slug>`, com o
   nome exato indicado em `docs/backlog.md`. Se a branch já existir, use-a (`git switch`).
3. **Ler** a tarefa em `docs/backlog.md` e SOMENTE os documentos e arquivos que ela lista.
4. **Ambiente.** Use o Python do `.venv` da raiz em todos os comandos
   (Windows: `.venv\Scripts\python`; macOS/Linux: `.venv/bin/python`). Se o `.venv` não
   existir, crie-o e instale `requirements.txt` e `requirements-dev.txt`.
   Se `data/transacoes_preparadas.parquet` faltar e a tarefa precisar dele, rode
   `python -m src.preparar_dados`. Nunca rode `src.treinar_modelo` sem a Issue mandar.
5. **Planejar.** Antes de editar, escreva um plano curto: arquivos que vai criar ou alterar,
   funções, testes e como vai verificar. Confira se todos os arquivos estão na lista
   "Arquivos permitidos" da tarefa. Se precisar de outro arquivo, pare e pergunte.
6. **Implementar** em passos pequenos, seguindo as seções 5 a 11.
7. **Verificar** com o portão de qualidade (seção 12), com os testes de conformidade e com
   as verificações da tarefa. Compare cada resultado com os critérios de aceite. Se algo falhar,
   corrija a causa no código e verifique de novo. Nunca altere um critério, um teste ou um número
   esperado para "passar".
8. **Commitar e enviar.** Commits pequenos e coerentes (seção 4). Depois
   `git push -u origin feature/<numero>-<slug>`. Nunca faça push em `main` ou `develop`.
9. **Relatar** no formato da seção 13 e pare. Não abra outra Issue por conta própria.

## 4. Git

- Branches: `main` (versão entregue, protegida), `develop` (integração, protegida, alvo de
  todo Pull Request), `feature/<numero>-<slug>` (uma Issue, uma branch).
- Mensagens no padrão Conventional Commits: prefixo em inglês, assunto em português, verbo no
  presente, minúscula, sem ponto final, até 72 caracteres.
  Prefixos: `feat`, `fix`, `refactor`, `test`, `docs`, `style`, `perf`, `chore`.
  Exemplos: `feat: adiciona painel de análise da transação`; `test: cobre registro de resposta inválida`.
- Proibido: `git push --force`, `git rebase` em branch compartilhada, commit direto em `main` ou
  `develop`, `git add` de `data/`, `.venv/`, `__pycache__/`, `.ruff_cache/`, arquivos `.env`.
- Antes de cada commit, rode `git status` e confira que só arquivos permitidos pela tarefa entraram.
- Você não faz merge. O merge é feito no GitHub por outra pessoa, depois da revisão.

## 5. Escopo

- Altere somente os arquivos listados em "Arquivos permitidos" da tarefa.
- Encontrou um problema fora do escopo? Não corrija. Anote em "Achados fora do escopo" no
  relatório; ele vira uma Issue nova.
- Não adicione funcionalidades que não estejam nos critérios de aceite, mesmo que pareçam úteis.

## 6. Convenções de código (Python)

- Formatação: Black (linha de 100 caracteres). Lint: Ruff com a configuração do `pyproject.toml`.
  Não discuta estilo; o formatador decide.
- Idioma (ADR-001): identificadores, comentários, docstrings, logs e textos de tela em português
  do Brasil, sem acento em identificadores e nomes de arquivo. Nunca misture idiomas num mesmo
  nome (proibido `get_transacao`, `calcular_score`).
- Nomes: funções e variáveis `snake_case` com verbo para funções (`calcular_sinais`); classes
  `PascalCase` com um único conceito (`AgenteSentinela`); constantes `UPPER_SNAKE_CASE`;
  booleanos com prefixo afirmativo (`esta_disponivel`, `tem_sinais`), nunca negativo.
- Sem valores soltos: limiares, caminhos, tamanhos e URLs ficam em `src/config.py`; textos de
  tela em `src/interface/textos.py`; cores, ícones e rótulos de decisão em `src/interface/tema.py`.
- Tipagem: anotações de tipo em todas as funções públicas.
- Tamanho: função com no máximo 50 linhas; módulo com uma responsabilidade e, de preferência,
  até 150 linhas. Passou disso, divida.
- Mais de 4 parâmetros: agrupe numa `dataclass` (exceto assinaturas já fixadas na ESPECIFICACAO).
- Sem duplicação: a interface nunca reimplementa regra do agente; importa de `src.agente` e
  `src.config`.
- Sem código morto nem código comentado. TODO só no formato
  `# TODO(#<issue>, AAAA-MM-DD): o que falta e por quê`.

## 7. Documentação no código

- Docstring no estilo Google, em português, em todo módulo, classe e função pública, com
  `Args:`, `Returns:` e `Raises:` quando houver.
- Comentário explica o PORQUÊ de uma decisão, nunca o que a linha faz.

## 8. Erros e logs

- Nunca `except:` nem `except Exception:` genérico; capture o tipo específico
  (`requests.RequestException`, `FileNotFoundError`, `ValueError`, `KeyError`).
- Todo `except` trata, relança ou registra em log. Nunca `pass` silencioso.
- Logs com `logging.getLogger(__name__)`; `print` só nos scripts executados com `python -m`
  para mostrar o resumo pedido pela ESPECIFICACAO.
- Erro para o usuário: em português, dizendo o que aconteceu e como resolver, com texto de
  `textos.py`. Nunca mostre stack trace, nome de exceção ou `st.exception` na tela.
- Falhe cedo: arquivo ausente é verificado na entrada, com mensagem clara.

## 9. Dados, privacidade e segredos

- Leia do CSV somente as 16 colunas da ESPECIFICACAO, seção 4. Nunca leia colunas pessoais
  (nomes, e-mails, telefones, documentos, endereços) nem as colunas proibidas da seção 5.
- Nunca abra, imprima ou cole linhas dos arquivos de `data/` (o `.bobignore` bloqueia a leitura;
  scripts Python podem usá-los normalmente). Para conferir, mostre só contagens e agregados.
- Log nunca registra identificadores de cartão, cliente ou estabelecimento.
- Testes usam somente valores inventados, nunca linhas da base.
- Este projeto não tem segredos. Se surgir algum, use variável de ambiente e `.env.example`;
  nunca escreva token ou senha no código.

## 10. Testes

- pytest. Obrigatório testar: regra de negócio, cálculo, validação de entrada e todo defeito
  corrigido (o teste reproduz o defeito antes da correção).
- Nome do teste é uma frase: `test_bloqueia_transacao_com_ip_desconhecido`.
- Um comportamento por teste, no padrão Arranjo–Ação–Asserção, com linhas em branco separando.
- Testes independentes, sem depender de ordem, da pasta `data/` ou do Ollama (use `monkeypatch`).
- Teste que precisa do modelo usa `pytest.mark.skipif` quando `modelos/sentinela.joblib` não existir.

## 11. Interface (Streamlit)

- Siga `docs/08-design-da-interface.md` à risca: layout, componentes, textos e estados.
- Todo estado previsto no design é implementado: carregando, vazio, erro, sucesso.
- Cache: dados e fila com `st.cache_data`; agente com `st.cache_resource`; a análise de cada
  transação (com a explicação) guardada em `st.session_state["analises"]`, para não chamar o
  Granite de novo a cada clique. A resposta do analista é sempre lida do arquivo.
- Nunca exiba as colunas `fraude` ou `decisao_sistema_atual` na fila ou no painel da transação.
- Toda ação produz resposta visível (spinner, toast ou mensagem).

## 12. Portão de qualidade (rode antes de todo commit)

    python -m black --check .
    python -m ruff check .
    python -m pytest -q

Os três precisam passar. Depois rode as verificações específicas da tarefa.
Invariantes: depois de qualquer tarefa, `python -m src.avaliar_agente` continua mostrando os
números da ESPECIFICACAO, seção 11. Se mudarem, você quebrou algo: pare e investigue.

**Conformidade** (o `pytest -q` acima já inclui; rode também isolado para o relatório):

    python -m pytest tests/test_conformidade_nucleo.py tests/test_conformidade_interface.py -q -rs

- Os dois arquivos de conformidade são intocáveis. Não os edite, apague ou renomeie; não use
  `skip`, `xfail`, `-k`, `--deselect`, `conftest.py` nem a configuração do pytest no
  `pyproject.toml` para escondê-los.
- Teste de conformidade falhando significa erro no código, nunca no teste. Se você tiver certeza
  de que um teste contradiz a ESPECIFICACAO ou o design, pare e relate (seção 14).
- Na sua máquina, com `data/` presente, nenhum teste do núcleo pode ser pulado. Na interface, só
  podem ser pulados os testes com o motivo "Issue #N ainda não implementada" de Issues futuras.
- No CI não há `data/`: os testes que precisam dos dados são pulados lá, e isso é esperado.

## 13. Relatório final (formato obrigatório)

1. **Resumo** em até 5 linhas.
2. **Critérios de aceite:** tabela `critério | esperado | obtido | OK?`.
3. **Portão de qualidade:** a última linha REAL da saída de cada comando da seção 12, inclusive
   a da conformidade com as contagens de passed, failed e skipped, e os motivos dos skips.
   Nunca escreva "tudo passou" sem colar a linha. Na tabela do item 2, "OK? = sim" só com evidência.
4. **Arquivos criados ou alterados.**
5. **Achados fora do escopo** (ou "nenhum").
6. **Pull Request pronto para colar:** título no padrão Conventional Commits com `(#<numero>)`
   no fim, e corpo preenchido com o modelo de `.github/pull_request_template.md`, incluindo
   `Closes #<numero>`.
7. **Próximo passo para o humano:** abrir o PR com base em `develop` e pedir revisão a quem
   está indicado na tarefa.

## 14. Quando parar e perguntar

- Um documento da seção 1 contradiz outro, ou a tarefa contradiz este arquivo.
- Precisa alterar arquivo fora da lista permitida, adicionar biblioteca ou mudar assinatura
  pública fixada na ESPECIFICACAO.
- Um número invariante mudou, ou um teste que já passava começou a falhar sem motivo claro.
- Um teste de conformidade parece contradizer a ESPECIFICACAO ou o design.
- Há alterações locais não commitadas, conflito de merge ou push recusado.
Ao perguntar, explique o problema em até 5 linhas e proponha 2 opções.

## 15. Economia de créditos

- Não leia arquivos que a tarefa não lista. Não releia arquivos inteiros se só precisa de um trecho.
- Não abra arquivos de `data/` nem binários (`.joblib`, `.parquet`).
- Mostre só o final das saídas longas de comandos.
- Não refaça trabalho já entregue em `develop`.

## 16. Revisão de Pull Request (quando a tarefa for revisar)

Não altere nenhum arquivo. Faça: `git fetch origin`, `git switch <branch-do-PR>`,
`git pull`, rode o portão de qualidade e as verificações da tarefa revisada, leia
`git diff origin/develop...HEAD` e responda com a tabela `verificação | OK? | evidência`:

- resolve a tarefa: todos os critérios de aceite da `docs/backlog.md` atendidos;
- conformidade rodada aqui, com `data/` presente: 0 falhas; skips só de Issues futuras;
- o diff não toca `tests/test_conformidade_*.py` nem a configuração do pytest;
- só alterou arquivos permitidos; nenhum arquivo desnecessário, de dados ou segredo no diff;
- casos de erro tratados, não só o caminho feliz; nenhuma exceção engolida;
- nomes e idioma conforme a seção 6; docstrings conforme a seção 7;
- testes presentes onde a seção 10 exige, e eles falhariam sem a mudança;
- interface: estados, textos e acessibilidade conforme o design;
- diagramas de `docs/` atualizados se a mudança alterou uma assinatura, módulo ou dependência;
- invariantes numéricas preservadas.

Termine com o veredito **Approve** ou **Request changes** e os comentários no formato
`<rótulo>: <assunto>` (rótulos: `issue`, `suggestion`, `question`, `nitpick`), em tom
colaborativo. Formatação não é item de revisão.
