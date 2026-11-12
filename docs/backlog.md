# Backlog — Issues da reta final

Cada seção é uma Issue do GitHub, com o mesmo número. O Bob executa uma Issue seguindo o
protocolo do `AGENTS.md` (seção 3) e só pode alterar os arquivos listados em "Arquivos
permitidos". Ponto de partida: as antigas Etapas 1 a 4 já estão no repositório, com defeitos. A
Issue #1 mede esses defeitos com os testes de conformidade, a #2 corrige o núcleo e as #3 a #5
refazem a interface. Toda Issue com código termina com a conformidade em 0 falhas. Responsáveis por letra: A = Pedro Muller (líder); B, C, D e E são definidos pelo
time na tabela do documento "Kit de Entrega".

| # | Título | Responsável | Revisor | Depende de | Prazo |
| --- | --- | --- | --- | --- | --- |
| 1 | chore: configura padrões, documentação e diagnóstico | A | B | — | qui 12/11, 19h |
| 2 | fix: corrige o núcleo e o adequa aos padrões | B | C | #1 | sex 13/11, 9h |
| 3 | feat: recria a base da interface | C | D | #2 | sex 13/11, 14h |
| 4 | feat: implementa a fila de alertas e o painel de análise | D | E | #3 | sex 13/11, 19h |
| 5 | feat: implementa as páginas Desempenho e Como funciona | E | D | #3 | sex 13/11, 19h |
| 6 | docs: audita o projeto e escreve o README | C | A | #4, #5 | sáb 14/11, 12h |
| 7 | docs: finaliza os textos de entrega | E | A | #4, #5 | sáb 14/11, 14h |
| 8 | chore: publica a versão de entrega, grava o vídeo e envia | A | C | #6, #7 | sáb 14/11, 22h |

---

## #1 — chore: configura padrões, documentação e diagnóstico

- **Rastreia:** RNF01, RNF02, RNF05.
- **Branch:** `feature/1-padroes-do-projeto`.
- **Antes do Bob (feito pelo líder):** os arquivos do kit já foram copiados para a branch:
  `AGENTS.md`, `ESPECIFICACAO.md`, `docs/`, `pyproject.toml`, `requirements-dev.txt`,
  `.bobignore`, `.streamlit/config.toml`, `.github/pull_request_template.md`, `.gitignore.kit`,
  `tests/test_conformidade_nucleo.py`, `tests/test_conformidade_interface.py`.
- **Ler:** `AGENTS.md`; `ESPECIFICACAO.md`, seções 2, 3 e 11.
- **Arquivos permitidos:** os arquivos do kit acima, `.gitignore`, `requirements.txt` e os
  arquivos da interface antiga, só para apagar (passo 3).
- **Fora do escopo:** corrigir qualquer coisa em `src/`, `tests/test_agente.py` ou `modelos/` (é
  a Issue #2); recriar a interface (é a Issue #3); corrigir avisos de Black ou Ruff.

**Passos**

1. Confirme que todos os arquivos do kit existem. Liste os que faltarem e pare se faltar algum.
2. Acrescente ao `.gitignore` as linhas de `.gitignore.kit` que ainda não existirem, sem apagar
   nenhuma linha atual. Depois apague `.gitignore.kit`. Se `git ls-files` listar algo de `data/`,
   rode `git rm -r --cached data` (o arquivo continua no seu disco, só sai do Git).
3. **Remova a interface antiga da Etapa 4** (ADR-010), com `git rm`: `app.py`, a pasta `pages/`
   e `src/interface/` se existirem, todo `.py` da raiz que não seja `conftest.py`, e todo arquivo
   de `tests/` que não seja `test_agente.py` nem um dos dois de conformidade. Liste no relatório o
   que foi apagado. Assim o Black, o Ruff e o CI não tropeçam no código antigo, e a Issue #3 parte
   do zero.
4. Fixe as versões em `requirements.txt`: para pandas, numpy, pyarrow, scikit-learn, joblib,
   streamlit, requests e pytest, escreva `nome==versão` com a versão instalada hoje no `.venv`
   (`python -m pip show <nome>`). Não atualize nenhuma biblioteca. numpy entra para que o modelo
   salvo carregue igual em todas as máquinas. Remova qualquer outra biblioteca que não seja usada
   pelo código; se for usada, não remova e anote em "Achados fora do escopo".
5. Instale `requirements-dev.txt` no `.venv` e fixe também as versões de black e ruff nele.
6. **Diagnóstico.** Se `data/transacoes_preparadas.parquet` não existir, rode
   `python -m src.preparar_dados` (se falhar, anote o erro e siga). Rode
   `python -m pytest tests/test_conformidade_nucleo.py -q -rs --tb=line` e anote a linha final
   (passed, failed, skipped) e a lista de testes que falharam, agrupada por seção da
   ESPECIFICACAO. Não corrija nada: isso é a Issue #2.
7. Rode `python -m black --check .` e `python -m ruff check . --statistics` só para medir.

**Critérios de aceite**

- Todos os arquivos do kit estão no repositório e `.gitignore.kit` foi removido.
- `requirements.txt` e `requirements-dev.txt` têm todas as versões fixadas (os testes de
  requisitos da conformidade passam).
- O corpo do PR tem a seção "Diagnóstico para a Issue #2" com a saída do passo 6 e as contagens
  do passo 7.
- Não existem mais `app.py` nem outros arquivos da interface antiga.
- `git diff --stat origin/develop` não mostra mudança em `src/` (exceto `src/interface/` apagada),
  `tests/test_agente.py` nem `modelos/`.

**Exceção ao portão de qualidade:** nesta Issue, Black, Ruff e pytest podem falhar: o código
antigo ainda não foi corrigido. **Commits:** `chore: adiciona regras do bob, documentação e
testes de conformidade`, `chore: remove a interface antiga da etapa 4` e
`chore: fixa as versões das dependências`.

---

## #2 — fix: corrige o núcleo e o adequa aos padrões

- **Rastreia:** RF001 a RF005, RNF01, RNF02, RNF05.
- **Branch:** `feature/2-correcao-do-nucleo`.
- **Duas partes, dois prompts, um Pull Request.** A parte A deixa o núcleo correto; a parte B
  deixa o código no padrão sem mudar comportamento. Rode a parte B só depois da parte A pronta.
- **Ler:** `AGENTS.md`; `ESPECIFICACAO.md` inteira; `docs/04-arquitetura.md` (nível 3);
  `docs/06-sequencias.md` (primeiro diagrama).
- **Arquivos permitidos:** `src/__init__.py`, `src/config.py`, `src/preparar_dados.py`,
  `src/treinar_modelo.py`, `src/agente.py`, `src/avaliar_agente.py`, `modelos/` (só na parte A,
  gerado pelos scripts), `tests/test_agente.py`, `conftest.py`,
  `.github/workflows/qualidade.yml` (novo, parte B), `docs/04-arquitetura.md` e
  `docs/06-sequencias.md` (só se o código real divergir deles).
- **Fora do escopo:** interface (Issue #3); mudar a ESPECIFICACAO.

### Parte A — correção (commits `fix:`)

1. Prepare os dados com `python -m src.preparar_dados` e rode `python -m pytest tests/test_conformidade_nucleo.py -q -rs --tb=short`.
   No plano (passo 5 do protocolo), agrupe as falhas por causa e por arquivo.
2. Corrija uma causa por vez, na ordem `preparar_dados` → `treinar_modelo` → `agente` →
   `avaliar_agente`, com um commit `fix:` por causa (por exemplo
   `fix: usa feedback_label como rótulo das fraudes`). Faltam constantes em `src/config.py` ou a
   função `granite_disponivel`? Crie-as exatamente como nas seções 8.1 e 8.5.
3. Depois de mudar `preparar_dados`, rode de novo os três scripts, nesta ordem. Depois de mudar
   `treinar_modelo`, rode `treinar_modelo` e `avaliar_agente`. Depois de mudar `agente`, rode
   `avaliar_agente`. Os arquivos novos de `modelos/` entram no mesmo commit da correção que os
   mudou. Nunca edite um JSON de `modelos/` à mão: um teste confere que eles saem do código.
4. Se `tests/test_agente.py` contradiz a ESPECIFICACAO, seção 9, corrija o teste para seguir a
   seção 9 e explique no relatório. Nunca enfraqueça um teste para o código passar.
5. A parte A termina quando `python -m pytest tests/test_conformidade_nucleo.py -q -rs` mostra 0 failed e 0 skipped. Relate (seção 13) com as
   contagens de antes e de depois e pare.

### Parte B — padrões (sem mudar comportamento; `modelos/` não muda)

1. `style: aplica black e ruff ao código existente` — rode `python -m black .` e
   `python -m ruff check . --fix`. Os avisos restantes do Ruff são resolvidos nos passos seguintes.
2. `refactor: centraliza limiares e rótulos em config` — troque no código todos os números e
   textos soltos pelas constantes de `src/config.py` (limiares dos sinais, hora da madrugada,
   datas da divisão, semente, rótulos de decisão, URLs e tempos do Ollama). Os valores não mudam.
3. `refactor: trata erros específicos com log` — troque todo `except` genérico por exceções
   específicas com log via `logging`; o log nunca inclui identificadores de cartão, cliente ou
   estabelecimento. Use `HTTPStatus.OK` em vez de `200`.
4. `docs: documenta os contratos públicos do núcleo` — docstrings no estilo Google, em
   português, em todos os módulos, classes e funções públicas de `src/`.
5. `test: reorganiza os testes do agente e cobre falhas do granite` — reescreva
   `tests/test_agente.py` com nomes em frase, padrão Arranjo–Ação–Asserção e um comportamento
   por teste (use `pytest.mark.parametrize` nos casos de `decidir`), mantendo tudo o que a
   ESPECIFICACAO, seção 9, exige. Acrescente, com `monkeypatch` em `requests`:
   `granite_disponivel` devolve False quando a conexão falha; `explicar` devolve fonte "regras"
   quando o POST estoura o tempo; `explicar` devolve fonte "regras" quando `response` vem vazio;
   `explicar` devolve fonte "granite" e o texto quando a resposta é válida.
6. `chore: adiciona a verificação automática de qualidade` — crie
   `.github/workflows/qualidade.yml` exatamente com o conteúdo abaixo, trocando `"3.12"` pela
   versão principal do Python do `.venv` (por exemplo `"3.11"`).

```yaml
name: Qualidade

on:
  pull_request:
    branches: [develop, main]
  push:
    branches: [develop]

jobs:
  verificar:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
      - name: Instalar dependências
        run: pip install -r requirements.txt -r requirements-dev.txt
      - name: Black
        run: black --check .
      - name: Ruff
        run: ruff check .
      - name: Testes
        run: pytest -q -rs
```

**Critérios de aceite (das duas partes)**

- `python -m pytest tests/test_conformidade_nucleo.py -q -rs` com `data/` presente: 0 failed e 0 skipped.
- Portão de qualidade completo passa (Black, Ruff e pytest).
- `python -m src.avaliar_agente` mostra exatamente as invariantes da ESPECIFICACAO, seção 11.
- A parte B não altera `modelos/` (`git diff --stat <último commit da parte A> -- modelos/` vazio).
- Nenhum `print` fora dos três scripts; nenhum `except Exception`; nenhum limiar numérico fora
  de `src/config.py`.
- O nível 3 de `docs/04-arquitetura.md` corresponde às funções reais de `src/agente.py`.
- O workflow "Qualidade" aparece verde no Pull Request.

**Exceção ao portão de qualidade:** os commits da parte A e os intermediários da parte B podem ter
avisos de Black e Ruff; o portão completo precisa passar no último commit.

---

## #3 — feat: recria a base da interface

- **Rastreia:** RF006, RF008, RNF03 · US005 (cenários 5 e 6), US007 (cenário 6).
- **Branch:** `feature/3-base-da-interface`.
- **Ler:** `AGENTS.md`; `ESPECIFICACAO.md`, seções 3, 8.1 e 10; `docs/08-design-da-interface.md`,
  seções 3, 5, 6, 10, 11, 12, 13 e 17; `docs/02-user-stories.md` (US005 e US007).
- **Ponto de partida:** a interface antiga foi apagada na Issue #1 (ADR-010). Escreva tudo do
  zero; não recupere trechos da interface antiga pelo histórico do Git.
- **Arquivos permitidos:** `app.py`, `src/interface/__init__.py`, `src/interface/tema.py`,
  `src/interface/textos.py`, `src/interface/formatacao.py`, `src/interface/dados.py`,
  `src/interface/feedback.py`, `src/interface/pagina_fila.py`,
  `src/interface/pagina_desempenho.py`, `src/interface/pagina_como_funciona.py`,
  `tests/test_formatacao.py`, `tests/test_feedback.py`, `tests/test_fila.py`, `tests/test_app.py`.
- **Fora do escopo:** o conteúdo das três páginas (Issues #4 e #5); qualquer arquivo de `src/`
  fora de `src/interface/`.

**Passos**

1. `tema.py`, `textos.py`, `formatacao.py`, `dados.py` e `feedback.py` exatamente como nas
   seções 5.2, 11, 12 e 13 do design. `textos.py` contém TODOS os textos da seção 11, inclusive
   os usados só nas Issues #4 e #5.
2. As três páginas, cada uma com uma função `renderizar()` que, por enquanto, mostra só
   `st.title` com o título da página e `st.caption("Página em construção na Issue #4.")` (ou #5).
   Use exatamente esse texto: enquanto ele existir, os testes de conformidade das Issues #4 e #5
   ficam pulados; as Issues #4 e #5 o removem.
3. `app.py` exatamente como na seção 13.3 do design, com o `url_path` de cada página (seção 3).
4. Testes: `tests/test_formatacao.py` com todos os exemplos da seção 12;
   `tests/test_feedback.py` com os casos da seção 13.2; `tests/test_fila.py` com uma base falsa
   de poucas linhas (fevereiro e março, com e sem fraude) e um `analisar_lote` falso, cobrindo:
   só março entra, todas as fraudes entram, a amostra de legítimas respeita o tamanho e a
   semente, a ordem é por nota decrescente, as colunas `fraude` e `decisao_sistema_atual` saem,
   e `contar_por_decisao` devolve zero para decisão ausente; `verificar_arquivos` com caminhos
   temporários inexistentes devolve as duas mensagens na ordem certa.
5. `tests/test_app.py`: testes de fumaça com `streamlit.testing.v1.AppTest`, pulados com
   `pytest.mark.skipif` se faltar `data/transacoes_preparadas.parquet` ou o modelo:
   - `app.py` com `AppTest.from_file(str(RAIZ / "app.py"), default_timeout=120)`, onde
     `RAIZ = Path(__file__).resolve().parents[1]` (caminho relativo é resolvido a partir do
     arquivo de teste, não da raiz);
   - cada página com `AppTest.from_function(funcao, default_timeout=120)`, em que `funcao` importa
     a página dentro do corpo (`from src.interface import pagina_desempenho`) e chama
     `renderizar()`. `AppTest.switch_page` não funciona com páginas definidas por função. Essa
     importação dentro da função leva `# noqa: PLC0415` (o `AppTest` roda só o corpo dela).
   Cada teste verifica `not at.exception`. Testado no Streamlit 1.67.

**Critérios de aceite**

- Portão de qualidade passa; invariantes preservadas.
- `python -m pytest tests/test_conformidade_nucleo.py tests/test_conformidade_interface.py -q -rs`: 0 failed; só os testes das Issues #4 e #5 pulados.
- Não sobrou nada da interface antiga.
- `streamlit run app.py` abre no navegador com as três páginas no menu, o interruptor do Granite
  e o estado do Granite na barra lateral (verificação manual do responsável, registrada no PR).
- Com o Ollama desligado, a barra lateral mostra "IBM Granite: indisponível…".
- Nenhum texto literal de tela fora de `textos.py`.

---

## #4 — feat: implementa a fila de alertas e o painel de análise

- **Rastreia:** RF006, RF007, RF008 · US005, US006, US007.
- **Branch:** `feature/4-fila-de-alertas`.
- **Ler:** `AGENTS.md`; `docs/08-design-da-interface.md`, seções 1, 4.1, 6, 7, 10, 14 e 17;
  `docs/02-user-stories.md` (US005 a US007); `docs/03-user-flows.md` (jornada 2);
  `docs/06-sequencias.md`; `src/interface/` (para usar o que já existe).
- **Arquivos permitidos:** `src/interface/pagina_fila.py`. Só se um texto da seção 11 do design
  estiver faltando: `src/interface/textos.py`, para acrescentá-lo exatamente como no design.
- **Fora do escopo:** outras páginas, `app.py`, `src/agente.py`.
- **Pré-requisito do responsável:** Ollama instalado e `ollama pull granite4:micro` feito, para
  verificar os dois caminhos da explicação. Se existir um `data/feedback.csv` criado pela interface
  antiga, apague-o (é só um arquivo local de teste, com outro formato).

**Passos**

1. Implemente a seção 7 do design na ordem 7.1 a 7.5, inclusive o algoritmo de escolha da 7.4 e
   o cache de análises da 7.5, item 2.
2. Divida em funções privadas de no máximo 50 linhas (`_renderizar_indicadores`,
   `_renderizar_filtro_e_tabela`, `_renderizar_painel`, `_renderizar_resposta`,
   `_renderizar_historico`).
3. Remova o texto "Página em construção" da página. Rode o portão de qualidade,
   `python -m pytest tests/test_conformidade_nucleo.py tests/test_conformidade_interface.py -q -rs` e `streamlit run app.py`.

**Critérios de aceite**

- Conformidade: 0 failed e nenhum teste da Issue #4 pulado (com `data/` presente).

**Verificação manual no navegador, registrada no PR com ✅ ou ❌**

1. Os quatro indicadores somam 2.054 (US005, cenário 1).
2. A tabela abre só com Bloquear e Pedir confirmação, ordenada pela nota (cenário 2).
3. Marcar Aprovar mostra 2.054 linhas; desmarcar tudo mostra a mensagem de filtro vazio (cenários 3 e 4).
4. Clicar numa linha muda o painel; escolher um ID na caixa também (US006, cenários 1 e 2).
5. Faixa de decisão com ícone e texto; barra de nota com "Nota de risco: N de 100" (cenário 4).
6. Uma transação com sinais e uma sem sinais mostram os textos certos (cenário 5).
7. Com o Ollama ligado: spinner e legenda "IBM Granite 4"; com o Ollama parado: legenda "regras
   (IBM Granite indisponível no momento)"; com o interruptor desligado: legenda "regras"
   (cenários 6 a 8).
8. Clicar num botão de resposta não faz o Granite rodar de novo (cenário 9).
9. Histórico abre com até 10 transações (cenário 10).
10. "Confirmar fraude" grava em `data/feedback.csv`, mostra o aviso e a resposta atual; mudar
    para "Marcar como legítima" troca a resposta; recarregar a página mantém a resposta (US007,
    cenários 1 a 4).
11. Nenhum "R$" aparece como fórmula matemática; nenhuma coluna `fraude` na tela.

---

## #5 — feat: implementa as páginas Desempenho e Como funciona

- **Rastreia:** RF009, RF010 · US008, US009.
- **Branch:** `feature/5-desempenho-e-como-funciona`.
- **Ler:** `AGENTS.md`; `docs/08-design-da-interface.md`, seções 4.2, 4.3, 6, 8, 9, 10 e 17;
  `docs/02-user-stories.md` (US008 e US009); `src/interface/`.
- **Arquivos permitidos:** `src/interface/pagina_desempenho.py`,
  `src/interface/pagina_como_funciona.py`. Só se um texto da seção 11 do design estiver
  faltando: `src/interface/textos.py`, para acrescentá-lo exatamente como no design.
- **Fora do escopo:** a página da fila, `app.py`, `src/agente.py`.

**Passos**

1. Implemente as seções 8 e 9 do design, em funções privadas de no máximo 50 linhas.
2. Remova o texto "Página em construção" das duas páginas. Rode o portão de qualidade,
   `python -m pytest tests/test_conformidade_nucleo.py tests/test_conformidade_interface.py -q -rs` e `streamlit run app.py`.

**Critérios de aceite**

- Conformidade: 0 failed e nenhum teste da Issue #5 pulado (com `data/` presente).

**Verificação manual no navegador, registrada no PR**

1. Desempenho mostra os cinco indicadores com os números de `modelos/avaliacao_agente.json`
   (54 fraudes; 54 de 54 com "+28 em relação ao sistema atual"; 26 de 54; 0; 159).
2. O gráfico tem as duas barras e a tabela de comparação repete os números.
3. "Detalhes do modelo" mostra PR-AUC, ROC-AUC e a tabela das notas de corte.
4. Renomear temporariamente `modelos/avaliacao_agente.json` mostra o erro de métricas; ao
   desfazer, a página volta (US008, cenário 5). Desfaça antes do commit.
5. Como funciona mostra os passos, a tabela dos 9 sinais com os limiares de `config.py`, as
   regras de decisão, os números da base (160.000 transações e 146 fraudes) e as limitações.

---

## #6 — docs: audita o projeto e escreve o README

- **Rastreia:** RNF01 a RNF05.
- **Branch:** `feature/6-auditoria-e-readme`.
- **Ler:** `AGENTS.md`; `ESPECIFICACAO.md`; todos os arquivos de `docs/`; `modelos/metricas.json`;
  `modelos/avaliacao_agente.json`.
- **Arquivos permitidos:** `README.md`; arquivos de `docs/` para corrigir divergências com o
  código. Correções de código de até 3 linhas, justificadas no relatório; maiores viram Issue nova.
- **Fora do escopo:** novas funcionalidades.

**Passos**

1. Rode o portão de qualidade, as invariantes e `python -m pytest tests/test_conformidade_nucleo.py tests/test_conformidade_interface.py -q -rs` (0 failed e 0 skipped).
2. Audite o repositório inteiro com a tabela da seção 16 do `AGENTS.md` e com o checklist de
   diagramação: os diagramas de `docs/04` e `docs/06` correspondem às funções e módulos reais;
   a estrutura de pastas é a da ESPECIFICACAO, seção 3; `git ls-files` não lista nada de `data/`.
3. Escreva o `README.md` em português com: o problema; a solução em 5 linhas; os números reais
   dos dois JSON (sem arredondar para cima); como instalar e rodar (`.venv`,
   `pip install -r requirements.txt`, os três scripts, `pytest -q`, `streamlit run app.py`,
   Ollama opcional); a estrutura de pastas; como trabalhamos com o IBM Bob (`AGENTS.md`,
   especificação, Issues, Pull Requests revisados, CI); links para `docs/`; limitações; o time.
4. Verificação humana registrada no PR: nota de Acessibilidade do Lighthouse (Chrome) na página
   Fila de alertas; zoom de 200%; janela estreita; e a revisão heurística feita separadamente por
   duas pessoas (seção 15 do design), com os achados de severidade alta.

**Critérios de aceite**

- README completo, com números iguais aos dos JSON.
- Auditoria sem item reprovado, ou com os reprovados virando Issues novas.
- Lighthouse Acessibilidade com 90 ou mais, ou os problemas listados como Issue.

---

## #7 — docs: finaliza os textos de entrega

- **Rastreia:** RNF06. **Sem branch:** os textos ficam no documento "Kit de Entrega".
- Preencha os trechos "[PREENCHER" dos Textos 1 e 2 com os números de
  `modelos/avaliacao_agente.json` e com exemplos reais de prompts e do fluxo de trabalho. Confira
  que cada texto tem no máximo 500 palavras. O revisor lê os dois e fecha a Issue.

---

## #8 — chore: publica a versão de entrega, grava o vídeo e envia

- **Rastreia:** RNF06.
- **Passos (humanos):**
  1. Abrir Pull Request de `develop` para `main` com o título
     `chore: publica a versão de entrega 1.0`; o revisor aprova e faz o merge com
     "Create a merge commit".
  2. Criar a release `v1.0` no GitHub a partir de `main`.
  3. Gravar o vídeo de até 3 minutos seguindo o roteiro do Kit de Entrega e publicar como "Não
     listado" no YouTube.
  4. Testar numa aba anônima: link do vídeo e repositório abrem sem login.
  5. Enviar na aba Submissions do My Teams: vídeo, Texto 1, Texto 2 e link do repositório.
- **Critério de aceite:** a submissão aparece no portal antes de domingo, 15/11, às 17h.
