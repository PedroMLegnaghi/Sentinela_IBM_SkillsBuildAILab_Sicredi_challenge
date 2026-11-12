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

---

# Incrementos da reta final (Issues #19 a #32)

> **Substituída em 12/11 à noite pela parte "Aplicação web", no fim deste arquivo (ADR-011 e
> ADR-012).** Valem daqui só a #19 (integrada) e as regras comuns abaixo; #20 a #29, #31 e #33 a
> #35 foram fechadas; #30 e #32 seguem, com a descrição atualizada na parte nova.

Depois da versão 1.0 (Issues #1 a #8 e #13), o time faz incrementos em três frentes: rigor e
interpretabilidade dos dados e do modelo, comportamento de agente e uso visível do IBM Bob.
Regras que valem para TODAS as Issues desta parte, além do `AGENTS.md`:

- **O campeão não muda.** Nenhuma Issue altera `src/treinar_modelo.py`, `src/preparar_dados.py`,
  `src/agente.py`, `modelos/sentinela.joblib`, `modelos/metricas.json` nem
  `modelos/avaliacao_agente.json`. Modelos novos são só desafiantes, treinados em memória pelos
  scripts novos; nada é salvo em `.joblib`.
- **Invariantes intactas.** `python -m src.avaliar_agente` continua mostrando os números da
  ESPECIFICACAO, seção 11, e a conformidade continua com 0 falhas.
- **Portão completo com `data/` presente.** `python -m pytest -q` roda com `data/` na máquina; o
  CI pula os testes que precisam dos dados, então a sua máquina é a única que os confere.
- **Um arquivo, um dono.** Cada Issue só altera os arquivos listados nela. A Issue #19 cria um
  módulo vazio para cada seção nova; as páginas existentes só chamam esses módulos.
- **Textos de tela.** Ficam em `src/interface/textos.py`, dentro do bloco comentado da própria
  Issue (criado pela #19). Quando a Issue não fixar o texto exato, escreva-o em português claro,
  no tom da seção 11 do design, e liste no relatório os textos criados para o revisor conferir.
- **Scripts novos.** São executados com `python -m src.<nome>`, leem só
  `data/transacoes_preparadas.parquet` (nunca o CSV), gravam um JSON em `modelos/` e imprimem um
  resumo curto. O JSON nunca é editado à mão e entra no mesmo commit do script que o gera.
- **Seções novas na interface.** Se o JSON da seção não existir, a seção mostra
  `st.info` com o comando que falta rodar e não quebra a página.
- **Testes.** Cada função pública nova tem teste em `tests/test_<modulo>.py`, com dados
  inventados (DataFrame pequeno montado no teste), sem depender de `data/` nem do Ollama.
- **Privacidade.** Nenhum JSON, documento ou log contém id de transação, cartão, cliente ou
  estabelecimento: só contagens, médias, medianas, percentuais e somas.

| # | Título | Dono | Revisor | Branch |
| --- | --- | --- | --- | --- |
| 19 | chore: prepara a base dos incrementos | Pedro Muller | Lucas | `feature/19-base-dos-incrementos` |
| 20 | feat: calcula o custo da fraude e o prejuízo evitado | Lucas | Pedro Machado | `feature/20-custo-da-fraude` |
| 21 | feat: mostra o que pesou na nota | Bruno | Mariana | `feature/21-o-que-pesou-na-nota` |
| 22 | feat: cria o simulador "e se" | Bruno | Mariana | `feature/22-simulador` |
| 23 | feat: redige a mensagem de confirmação ao cliente | Bruno | Mariana | `feature/23-mensagem-ao-cliente` |
| 24 | fix: corrige os problemas de acessibilidade | Mariana | Bruno | `feature/24-acessibilidade` |
| 25 | feat: cria a página de respostas do analista | Mariana | Bruno | `feature/25-respostas-do-analista` |
| 26 | feat: expõe o agente numa API | Pedro Machado | Lucas | `feature/26-api-do-agente` |
| 27 | feat: mede a latência em tempo real | Pedro Machado | Lucas | `feature/27-tempo-real` |
| 28 | feat: avalia o modelo com rigor | Lucas | Pedro Machado | `feature/28-avaliacao-rigorosa` |
| 29 | feat: avalia o cenário sem as colunas de velocidade | Lucas | Pedro Machado | `feature/29-cenario-dificil` |
| 30 | docs: registra o uso do IBM Bob | Pedro Muller | Mariana | `feature/30-uso-do-bob` |
| 31 | feat: documenta a análise exploratória e a qualidade dos dados | Pedro Machado | Lucas | `feature/31-analise-exploratoria` |
| 32 | docs: atualiza o README e os textos de entrega | Pedro Muller | Lucas | `feature/32-readme-e-textos` |
| 33 | feat: conecta o agente ao watsonx Orchestrate (opcional) | Pedro Machado | Lucas | `feature/33-watsonx-orchestrate` |
| 34 | feat: monitora o drift das variáveis (opcional) | Lucas | Pedro Machado | `feature/34-monitor-de-drift` |
| 35 | feat: treina um desafiante com as respostas do analista (opcional) | Lucas | Pedro Machado | `feature/35-retreino-desafiante` |

As Issues #33 a #35 são opcionais: só começam depois que as obrigatórias do dono estiverem
integradas e nunca depois do congelamento do código (sábado, 12h).

---

## #19 — chore: prepara a base dos incrementos

- **Branch:** `feature/19-base-dos-incrementos`. O líder já acrescentou esta parte do backlog
  na branch; ela entra no primeiro commit da Issue.
- **Ler:** `AGENTS.md`; esta parte do backlog; `app.py`; `src/config.py`; as três páginas de
  `src/interface/`; `tests/test_app.py`.
- **Arquivos permitidos:** `docs/backlog.md` (só o commit do líder), `docs/01-requisitos.md`,
  `docs/04-arquitetura.md`, `app.py`, `src/config.py`, `src/interface/textos.py`,
  `src/interface/pagina_desempenho.py`, `src/interface/pagina_como_funciona.py`,
  `src/interface/pagina_fila.py`, `tests/test_app.py` e os 10 módulos novos do passo 2.

**Passos**

1. Em `src/config.py`, acrescente no fim, num bloco comentado "Incrementos":
   `CAMINHO_CUSTOS = RAIZ / "modelos" / "custos.json"`,
   `CAMINHO_AVALIACAO_RIGOROSA = RAIZ / "modelos" / "avaliacao_rigorosa.json"`,
   `CAMINHO_CENARIO_DIFICIL = RAIZ / "modelos" / "cenario_dificil.json"`,
   `CAMINHO_LATENCIA = RAIZ / "modelos" / "latencia.json"`,
   `CAMINHO_EDA = RAIZ / "modelos" / "eda.json"`,
   `CAMINHO_NOTIFICACOES = RAIZ / "data" / "notificacoes.csv"`,
   `CUSTO_PEDIDO_CONFIRMACAO = 1.0` (reais por pedido de confirmação; premissa do time, com
   comentário dizendo isso), `REPETICOES_BOOTSTRAP = 1000` e
   `COLUNAS_VELOCIDADE = ["vel_cartao_terminal_1h", "qtd_transacoes_cartao_1min", "qtd_token_carteira_3m"]`.
   Não mude nenhuma constante existente.
2. Crie os módulos-esqueleto, cada um com docstring de módulo e uma função pública com docstring
   e `# TODO(#N, 2026-11-13): <o que a Issue N faz aqui>`, que por enquanto não mostra nada:
   - `src/interface/secao_confiabilidade.py` → `renderizar() -> None` (#28);
   - `src/interface/secao_custos.py` → `renderizar() -> None` (#20);
   - `src/interface/secao_cenario_dificil.py` → `renderizar() -> None` (#29);
   - `src/interface/secao_latencia.py` → `renderizar() -> None` (#27);
   - `src/interface/secao_dados.py` → `renderizar() -> None` (#31);
   - `src/interface/secao_importancia.py` → `renderizar() -> None` (#21);
   - `src/interface/painel_contribuicoes.py` → `renderizar(transacao: dict) -> None` (#21);
   - `src/interface/painel_mensagem.py` → `renderizar(transacao: dict, analise: dict) -> None` (#23);
   - `src/interface/pagina_simulador.py` → `renderizar() -> None` (#22);
   - `src/interface/pagina_respostas.py` → `renderizar() -> None` (#25).
   As duas páginas novas mostram `st.title` e `st.caption` com textos do passo 4.
3. Ligue os módulos sem mudar nada visível:
   - `pagina_desempenho.renderizar()` chama, no fim e nesta ordem, `secao_confiabilidade`,
     `secao_custos`, `secao_cenario_dificil` e `secao_latencia`;
   - `pagina_como_funciona.renderizar()` chama `secao_importancia` logo depois da tabela dos 9
     sinais e `secao_dados` logo depois de "Sobre os dados";
   - no painel de `pagina_fila.py`, chame `painel_contribuicoes.renderizar(transacao)` logo
     depois dos sinais de alerta e `painel_mensagem.renderizar(transacao, analise)` logo depois
     da legenda da fonte da explicação. Nenhuma outra mudança em `pagina_fila.py`.
4. Em `src/interface/textos.py`, acrescente no fim um bloco comentado por Issue
   (`# --- Issue #20: custo da fraude ---` etc., de #20 a #31) e, nos blocos #22 e #25:
   `TITULO_SIMULADOR = "Simulador"`, `LEGENDA_SIMULADOR_PROVISORIA = "Em preparação na Issue #22."`,
   `TITULO_RESPOSTAS = "Respostas do analista"` e
   `LEGENDA_RESPOSTAS_PROVISORIA = "Em preparação na Issue #25."`.
5. Em `app.py`, acrescente as duas páginas ao menu, depois das três atuais, com
   `url_path="simulador"` e `url_path="respostas"` e ícones Material coerentes com os existentes.
6. Em `tests/test_app.py`, acrescente um teste de fumaça para cada página nova, no mesmo padrão
   dos existentes (`AppTest.from_function`, import dentro da função com `# noqa: PLC0415`).
7. Em `docs/01-requisitos.md`, acrescente RF017 a RF028, um por Issue de #20 a #31 (prioridade
   "Could", fase "Incremento #N"), e mude a prioridade de RF014 para "Could (simulado na #23)".
   Em `docs/04-arquitetura.md`, acrescente os módulos novos ao nível 3.

**Critérios de aceite**

- Portão completo passa; conformidade 0 failed e 0 skipped; invariantes iguais.
- `streamlit run app.py`: as três páginas antigas ficam idênticas; o menu tem 5 páginas.
- Cada módulo novo existe com docstring, função pública tipada e TODO no formato do AGENTS.md.

---

## #20 — feat: calcula o custo da fraude e o prejuízo evitado

- **Branch:** `feature/20-custo-da-fraude`. **Depende de:** #19.
- **Arquivos permitidos:** `src/analisar_custos.py` (novo), `modelos/custos.json` (gerado),
  `src/interface/secao_custos.py`, bloco #20 de `src/interface/textos.py`,
  `tests/test_analisar_custos.py` (novo).

**Passos**

1. `src/analisar_custos.py`, função pública `calcular_custos(teste: pd.DataFrame,
   custo_confirmacao: float) -> dict` que recebe as transações de março já com as colunas
   `valor`, `fraude`, `decisao` (do Sentinela, via `analisar_lote` do agente salvo) e
   `decisao_sistema_atual`, e devolve:
   - `fraudes_valor_total`: soma de `valor` das fraudes;
   - `sentinela`: `{"valor_fraudes_bloqueadas", "valor_fraudes_nao_bloqueadas", "pedidos_confirmacao", "custo_confirmacoes", "custo_total"}`,
     onde `custo_total = valor_fraudes_nao_bloqueadas + pedidos_confirmacao * custo_confirmacao`;
   - `sistema_atual`: `{"valor_fraudes_bloqueadas", "valor_fraudes_nao_bloqueadas", "custo_total"}`
     (bloqueio do sistema atual = `decisao_sistema_atual == "deny"`);
   - `prejuizo_evitado`: `sistema_atual.custo_total - sentinela.custo_total`;
   - `curva`: para cada nota de corte de 0 a 100 de 5 em 5, o custo total se o Sentinela
     bloqueasse a partir dessa nota e pedisse confirmação no resto acima de `NOTA_CONFIRMAR`.
   Valores em reais com 2 casas; valor vazio conta como 0 e é contado em `valores_vazios`.
2. `main()` lê o parquet, filtra março (`INICIO_TESTE` ≤ data < `FIM_TESTE`), roda o agente salvo
   em lote, chama `calcular_custos` com `CUSTO_PEDIDO_CONFIRMACAO`, grava `CAMINHO_CUSTOS` e imprime
   o prejuízo evitado.
3. `secao_custos.renderizar()`: título "Custo da fraude em março"; três `st.metric`
   (prejuízo evitado, custo com o Sentinela, custo com o sistema atual) com `formatar_moeda`;
   `st.line_chart` da curva; uma legenda com a premissa de R$ 1,00 por pedido de confirmação.
4. Testes com um DataFrame inventado de 6 a 10 linhas: soma certa, valor vazio contado,
   prejuízo evitado = diferença dos custos, curva com 21 pontos.

**Critérios de aceite:** portão completo; `python -m src.analisar_custos` gera o JSON; a seção
aparece em Desempenho com os números do JSON; nenhum id no JSON.

---

## #21 — feat: mostra o que pesou na nota

- **Branch:** `feature/21-o-que-pesou-na-nota`. **Depende de:** #19.
- **Arquivos permitidos:** `src/explicabilidade.py` (novo), `src/interface/painel_contribuicoes.py`,
  `src/interface/secao_importancia.py`, bloco #21 de `src/interface/textos.py`,
  `tests/test_explicabilidade.py` (novo).

**Passos**

1. `src/explicabilidade.py`, usando o pipeline salvo (`imputer` → `scaler` → `modelo`) sem
   treinar nada:
   - `contribuicoes(pipeline, transacao: dict) -> list[dict]`: aplica `imputer` e `scaler` à
     transação e devolve, para cada coluna que entra na regressão (as 11 variáveis e os
     indicadores de vazio do imputer), `{"variavel", "valor_padronizado", "contribuicao"}` com
     `contribuicao = coef * valor_padronizado`, ordenado por `abs(contribuicao)` decrescente.
     A soma das contribuições mais o intercepto é o log-odds da nota; teste isso.
   - `importancia_global(pipeline) -> list[dict]`: `{"variavel", "coeficiente"}` ordenado por
     `abs(coeficiente)`.
   - `NOMES_LEGIVEIS`: dicionário variável → nome em português ("Rajadas no último minuto" etc.;
     os indicadores de vazio viram "<nome> ausente").
2. `painel_contribuicoes.renderizar(transacao)`: título "O que pesou na nota"; gráfico de barras
   horizontais com as 6 maiores contribuições (positivas aumentam o risco, negativas diminuem),
   com nomes legíveis; uma legenda curta explicando a leitura. Use o agente em cache
   (`dados.carregar_agente()`) para pegar o pipeline.
3. `secao_importancia.renderizar()`: título "O que o modelo aprendeu"; barras com os
   coeficientes das 11 variáveis e uma frase sobre o sinal de cada barra.
4. Testes com um pipeline pequeno treinado no próprio teste com dados inventados: ordenação,
   soma = log-odds, nomes legíveis para todas as colunas.

**Critérios de aceite:** portão completo; no painel, uma transação bloqueada mostra barras
positivas grandes e uma aprovada mostra barras pequenas; a seção aparece em Como funciona.

---

## #22 — feat: cria o simulador "e se"

- **Branch:** `feature/22-simulador`. **Depende de:** #19 (e usa a #21 se já estiver integrada).
- **Arquivos permitidos:** `src/interface/pagina_simulador.py`, bloco #22 de
  `src/interface/textos.py`, `tests/test_simulador.py` (novo).

**Passos**

1. A página carrega a fila (`dados.carregar_fila()`) e oferece um `st.selectbox` de transação
   (mesmo formato de rótulo da Fila). Abaixo, controles com o valor inicial da transação:
   `valor` (`st.number_input`, R$), `hora` (`st.slider` 0–23), `credito` e `nao_presente`
   (`st.toggle`), `ip_pais_desconhecido` (`st.toggle`), `qtd_transacoes_cartao_1min`,
   `vel_cartao_terminal_1h`, `qtd_token_carteira_3m` (`st.number_input` inteiros ≥ 0),
   `dist_terminal_anterior_km` (`st.number_input` ≥ 0) e `risco_estabelecimento` (`st.slider` 0–100).
   `madrugada` é recalculada da hora com `HORA_FIM_MADRUGADA`, nunca editada.
2. A cada mudança, monte a transação alterada (função pura `montar_transacao_simulada(base: dict,
   alteracoes: dict) -> dict`) e mostre, lado a lado, "Original" e "Simulada": decisão (faixa com
   o estilo de `tema`), nota, sinais. Use `pontuar`, `calcular_sinais` e `decidir` do agente; nunca
   chame o Granite aqui. Se a #21 já estiver em `develop`, mostre também as contribuições.
3. Botão "Voltar aos valores originais".
4. Testes da função pura: `madrugada` recalculada, campos não alterados preservados, tipos
   numéricos garantidos.

**Critérios de aceite:** portão completo; mudar a hora para 3 acende o sinal de madrugada;
zerar as rajadas de uma fraude baixa a nota; a página não grava nada.

---

## #23 — feat: redige a mensagem de confirmação ao cliente

- **Branch:** `feature/23-mensagem-ao-cliente`. **Depende de:** #19.
- **Arquivos permitidos:** `src/mensagem_cliente.py` (novo), `src/interface/painel_mensagem.py`,
  bloco #23 de `src/interface/textos.py`, `tests/test_mensagem_cliente.py` (novo), `.gitignore`
  (só se `data/` não cobrir `notificacoes.csv`).

**Passos**

1. `src/mensagem_cliente.py`: `redigir_mensagem(transacao: dict, usar_llm: bool) -> tuple[str, str]`
   devolve `(texto, fonte)`. Com `usar_llm` e `granite_disponivel()`, pede ao Granite (mesmo
   endpoint e tempo-limite de `explicar`) um SMS de até 160 caracteres, em português, sem link e
   sem pedir senha ou código; se falhar, ou sem `usar_llm`, usa o modelo fixo:
   "Sicredi: compra de {valor} em {data_hora} no cartão final ****. Foi você? Responda SIM ou NÃO."
   (o número do cartão NUNCA aparece; use `formatar_moeda` e `formatar_data_hora`). Valide o texto
   do Granite: mais de 160 caracteres, "http", "senha" ou "código" → usa o modelo fixo.
2. `painel_mensagem.renderizar(transacao, analise)`: só aparece quando a decisão é
   `PEDIR_CONFIRMACAO`. Mostra "Mensagem que seria enviada ao cliente", o texto num `st.code`, a
   fonte, e o botão "Simular envio", que grava `registrado_em, id_transacao, canal="sms", fonte`
   em `CAMINHO_NOTIFICACOES` (sem o texto) e mostra um `st.toast`. A mensagem fica em
   `st.session_state` para não chamar o Granite de novo a cada clique.
3. Testes com `monkeypatch`: modelo fixo sem Granite; texto do Granite inválido cai no modelo
   fixo; nenhuma saída contém dígitos do cartão; gravação em arquivo temporário.

**Critérios de aceite:** portão completo; só transações "Pedir confirmação" mostram a mensagem;
nada é enviado; `data/notificacoes.csv` fora do Git.

---

## #24 — fix: corrige os problemas de acessibilidade

- **Branch:** `feature/24-acessibilidade`. **Fecha também:** #17.
- **Antes do Bob (responsável):** no Chrome, Lighthouse → Accessibility na Fila de alertas;
  zoom de 200%; janela de 768 px. Registre a nota e os problemas num comentário da Issue #24.
- **Arquivos permitidos:** `src/interface/pagina_fila.py`, `src/interface/tema.py`,
  `src/interface/textos.py`, `.streamlit/config.toml`, `docs/08-design-da-interface.md` (só para
  registrar decisões novas, numa seção "Ajustes da Issue #24").

**Passos**

1. Corrija cada problema registrado, um commit por problema. Já conhecido: em janela estreita os
   botões "Confirmar fraude" e "Marcar como legítima" ficam cortados ("C…", "M…") — use
   `width="stretch"` e, se preciso, empilhe os botões abaixo de 900 px de largura útil.
2. Não mude a ordem nem os textos definidos no design, a não ser para acrescentar um rótulo
   acessível que falte.
3. Refaça o Lighthouse e registre a nota final no PR.

**Critérios de aceite:** Lighthouse Accessibility ≥ 90 (ou os itens restantes como Issue nova);
zoom de 200% e janela de 768 px sem conteúdo cortado; conformidade de interface 0 falhas.

---

## #25 — feat: cria a página de respostas do analista

- **Branch:** `feature/25-respostas-do-analista`. **Depende de:** #19.
- **Arquivos permitidos:** `src/interface/pagina_respostas.py`, bloco #25 de
  `src/interface/textos.py`, `tests/test_respostas.py` (novo).

**Passos**

1. A página lê `data/feedback.csv` (via `feedback.py`; vale a última resposta de cada transação)
   e junta com a fila (`dados.carregar_fila()`) pelo `id_transacao`.
2. Mostra: quantas transações têm resposta; quantas o analista confirmou como fraude; a taxa de
   concordância (resposta "fraude" com decisão BLOQUEAR, ou "legitima" com APROVAR ou
   PEDIR_CONFIRMACAO); uma tabela com ID, decisão do agente, nota, resposta e data; e
   `st.download_button` para exportar essa tabela em CSV.
3. Sem respostas: `st.info` explicando que as respostas aparecem depois de usar os botões da Fila.
4. Função pura `resumir_respostas(respostas: pd.DataFrame, fila: pd.DataFrame) -> dict` testada
   com dados inventados (concordância, última resposta vale, fila sem resposta).

**Critérios de aceite:** portão completo; responder 2 transações na Fila e abrir a página mostra
as 2; exportar baixa o CSV.

---

## #26 — feat: expõe o agente numa API

- **Branch:** `feature/26-api-do-agente`. **Depende de:** #19.
- **Arquivos permitidos:** `src/api.py` (novo), `requirements-api.txt` (novo),
  `tests/test_api.py` (novo), `.github/workflows/qualidade.yml`, `docs/04-arquitetura.md`,
  `docs/06-sequencias.md`.
- **Por que outro arquivo de requisitos:** a conformidade só permite as 8 bibliotecas de
  `requirements.txt`. A API é um componente opcional com dependências próprias.

**Passos**

1. `requirements-api.txt` com `fastapi`, `uvicorn` e `httpx`, versões fixadas com `==` (as que o
   `pip` instalar hoje no `.venv`).
2. `src/api.py` com FastAPI:
   - `GET /saude` → `{"status": "ok", "modelo_carregado": bool, "granite_disponivel": bool}`;
   - `POST /analisar` recebe um JSON validado por um modelo Pydantic com as 11 variáveis de
     `VARIAVEIS_MODELO` (todas opcionais, numéricas) e `usar_llm: bool = False`, e devolve
     `{"nota", "decisao", "decisao_legivel", "sinais", "explicacao", "fonte_explicacao", "latencia_ms"}`
     usando o agente carregado uma única vez na subida;
   - erro de validação → 422 com mensagem em português.
3. `tests/test_api.py` com `pytest.importorskip("fastapi")` e `TestClient`: `/saude` responde
   200; uma transação inventada de alto risco volta BLOQUEAR; campo inválido volta 422; pulado
   se o modelo não existir.
4. No CI, instale também `requirements-api.txt` antes dos testes.
5. Atualize o C4 (contêiner "API do agente") e acrescente uma sequência "autorizador chama a API".

**Critérios de aceite:** portão completo; `uvicorn src.api:app` sobe e `http://localhost:8000/docs`
mostra os dois endpoints; CI verde.

---

## #27 — feat: mede a latência em tempo real

- **Branch:** `feature/27-tempo-real`. **Depende de:** #19.
- **Arquivos permitidos:** `src/simular_fluxo.py` (novo), `modelos/latencia.json` (gerado),
  `src/interface/secao_latencia.py`, bloco #27 de `src/interface/textos.py`,
  `tests/test_simular_fluxo.py` (novo).

**Passos**

1. `src/simular_fluxo.py`: `medir_latencias(agente, transacoes: list[dict]) -> dict` processa
   uma transação por vez, em ordem de `data_hora`, com `calcular_sinais`, `pontuar` e `decidir`
   (sem Granite), e devolve `{"transacoes", "p50_ms", "p95_ms", "p99_ms", "maximo_ms",
   "transacoes_por_segundo"}`.
2. `main()` usa as transações de março, grava `CAMINHO_LATENCIA` e imprime p50 e p95. Registre
   no JSON o processador (`platform.processor()` ou `platform.machine()`).
3. `secao_latencia.renderizar()`: título "Pronto para tempo real"; `st.metric` de p50 e p95 em
   milissegundos e transações por segundo; legenda dizendo que a medição é sem o Granite.
4. Testes com um agente falso (monkeypatch) e 5 transações inventadas: chaves presentes,
   percentis ordenados (p50 ≤ p95 ≤ p99 ≤ máximo).

**Critérios de aceite:** portão completo; JSON gerado; seção visível em Desempenho.

---

## #28 — feat: avalia o modelo com rigor

- **Branch:** `feature/28-avaliacao-rigorosa`. **Depende de:** #19.
- **Arquivos permitidos:** `src/avaliar_rigor.py` (novo), `modelos/avaliacao_rigorosa.json`
  (gerado), `docs/11-avaliacao.md` (novo), `src/interface/secao_confiabilidade.py`, bloco #28 de
  `src/interface/textos.py`, `tests/test_avaliar_rigor.py` (novo).

**Passos**

1. `src/avaliar_rigor.py` treina em memória, com a MESMA receita do campeão (imputer mediana com
   indicador → scaler → regressão logística `class_weight="balanced"`, `SEMENTE`), e mede:
   - **Janelas temporais:** treino jan → teste fev; treino jan–fev → teste mar. PR-AUC, ROC-AUC,
     e recall, precisão e alertas no corte `NOTA_CONFIRMAR`.
   - **Intervalo de confiança:** bootstrap com `REPETICOES_BOOTSTRAP` reamostragens de março
     (semente `SEMENTE`) para recall e precisão do Sentinela completo (função `decidir`); IC 95%.
   - **Comparação:** só regras (alerta com 3 ou mais sinais; e com 4 ou mais), só modelo (nota ≥
     `NOTA_CONFIRMAR`), Sentinela completo e `HistGradientBoostingClassifier`
     (`class_weight="balanced"`, `random_state=SEMENTE`): alertas, fraudes pegas, precisão.
   - **Ablação:** PR-AUC sem cada uma das 11 variáveis e sem as 3 de `COLUNAS_VELOCIDADE` juntas.
   - **Calibração:** Brier e uma tabela de 10 faixas de nota com a fração real de fraude.
2. `main()` grava `CAMINHO_AVALIACAO_RIGOROSA` e escreve `docs/11-avaliacao.md` com as tabelas e
   uma leitura em português de cada uma (até 3 frases por tabela). Referência medida pelo líder
   em 12/11, para conferir: sem qualquer variável isolada a PR-AUC continua 1,000; sem as 3 de
   velocidade cai para cerca de 0,86; só regras com 4 sinais ou mais dá 57 alertas e 54 fraudes.
3. `secao_confiabilidade.renderizar()`: título "Quão confiável é o resultado"; recall e precisão
   com o IC 95%; a tabela de comparação; um gráfico da ablação; uma frase dizendo que a base é
   fácil e que três colunas de velocidade carregam o resultado.
4. Testes com dados inventados (duas classes bem separadas): funções de bootstrap, ablação e
   calibração devolvem as chaves e os intervalos ordenados.

**Critérios de aceite:** portão completo; JSON e documento gerados pelo script; números do
documento iguais aos do JSON; seção visível em Desempenho.

---

## #29 — feat: avalia o cenário sem as colunas de velocidade

- **Branch:** `feature/29-cenario-dificil`. **Depende de:** #19 e, de preferência, #28.
- **Arquivos permitidos:** `src/avaliar_cenario_dificil.py` (novo),
  `modelos/cenario_dificil.json` (gerado), `src/interface/secao_cenario_dificil.py`, bloco #29 de
  `src/interface/textos.py`, `tests/test_avaliar_cenario_dificil.py` (novo), `docs/11-avaliacao.md`
  (só acrescentar uma seção no fim).

**Passos**

1. Sem as 3 colunas de `COLUNAS_VELOCIDADE`, treine (jan–fev) e teste (mar) a regressão
   logística e o `HistGradientBoostingClassifier`; registre PR-AUC e recall no corte 30.
2. Reconstrua variáveis de velocidade a partir do histórico do arquivo, por cartão e por cliente,
   só com `id_cartao`, `id_cliente`, `data_hora` e `valor`: transações nos últimos 60 s e 3.600 s,
   soma de valor na última hora, segundos desde a transação anterior. Treine os dois modelos de
   novo com elas. Referência do líder: não recupera (cerca de 0,83 e 0,77), porque as rajadas não
   estão nas 160 mil linhas — isso é o achado, não um erro.
3. **Robustez:** com o pipeline salvo, transforme em vazio, em março, 10%, 30% e 50% dos valores
   de cada uma das 3 colunas de velocidade (semente `SEMENTE`) e meça o recall do Sentinela.
4. Grave `CAMINHO_CENARIO_DIFICIL`; acrescente a seção "Cenário difícil" em `docs/11-avaliacao.md`.
5. `secao_cenario_dificil.renderizar()`: título "E se faltarem os dados de velocidade?"; tabela
   dos modelos nos três cenários; gráfico do recall por percentual de vazios; uma frase com a
   conclusão (o agente depende de agregados em tempo real, o que justifica a API da #26).
6. Testes com dados inventados para a reconstrução (contagens em janelas de tempo corretas).

**Critérios de aceite:** portão completo; JSON gerado; seção visível em Desempenho.

---

## #30 — docs: registra o uso do IBM Bob

- **Branch:** `feature/30-uso-do-bob`. **Depende de:** todas as anteriores integradas.
- **Arquivos permitidos:** `docs/09-uso-do-bob.md` (novo), `.bob/custom_modes.yaml` (novo) ou o
  arquivo de modos personalizados que a documentação do Bob indicar para projeto,
  `docs/README.md`.

**Passos**

1. `docs/09-uso-do-bob.md`: como o time usou o Bob — `AGENTS.md`, `.bobignore`, os modos (Plan,
   Agent, Ask), os 4 prompts padrão, a tabela de Issues e PRs (número, autor, revisor, veredito do
   Bob, se houve "Request changes" e por quê), os defeitos que as revisões e a conformidade
   pegaram, e o que aprendemos. Tire os dados de `git log` e dos PRs (`gh pr list --state all`).
2. Um modo personalizado do Bob chamado `revisor-sentinela`, versionado no projeto, cujas
   instruções são a seção 16 do `AGENTS.md` mais "rode o portão completo com data/ presente" e
   "confira o limite de 50 linhas por função". Consulte a documentação de modos personalizados do
   Bob antes de criar o arquivo e cite a página no documento.
3. Link para o novo documento em `docs/README.md`.

**Critérios de aceite:** documento com números reais do GitHub; o modo aparece no seletor do Bob
ao abrir o projeto; portão completo.

---

## #31 — feat: documenta a análise exploratória e a qualidade dos dados

- **Branch:** `feature/31-analise-exploratoria`. **Depende de:** #19.
- **Arquivos permitidos:** `src/analisar_dados.py` (novo), `modelos/eda.json` (gerado),
  `docs/10-analise-exploratoria.md` (novo), `src/interface/secao_dados.py`, bloco #31 de
  `src/interface/textos.py`, `tests/test_analisar_dados.py` (novo).

**Passos**

1. `src/analisar_dados.py` lê só o parquet e calcula, sem nenhum id:
   - visão geral: linhas, fraudes, percentual, transações e fraudes por mês, por tipo e por
     modalidade;
   - por variável de `VARIAVEIS_MODELO`: percentual de vazios, mediana e percentis 10/90 em
     fraudes e em legítimas;
   - percentual de fraudes com cada sinal de alerta e de legítimas com o mesmo sinal;
   - distribuição por hora (24 contagens) para fraude e legítima.
2. Auditoria de vazamento: lista fixa das colunas proibidas da ESPECIFICACAO, seção 5, com o
   motivo de cada uma (texto do script, sem ler o CSV).
3. `main()` grava `CAMINHO_EDA` e escreve `docs/10-analise-exploratoria.md` com as tabelas e uma
   leitura em português (até 3 frases por tabela).
4. `secao_dados.renderizar()`: título "O que os dados mostram"; três gráficos (fraude ×
   legítima por hora; percentual com cada sinal; vazios por variável) e uma frase por gráfico.
5. Testes com dados inventados: contagens por mês, percentis, nenhum id na saída.

**Critérios de aceite:** portão completo; 160.000 linhas e 146 fraudes no JSON; documento e
seção coerentes com o JSON.

---

## #32 — docs: atualiza o README e os textos de entrega

- **Branch:** `feature/32-readme-e-textos`. **Depende de:** todas as anteriores integradas.
- **Arquivos permitidos:** `README.md`, `docs/README.md`.

**Passos**

1. Acrescente ao README as funcionalidades novas, os novos comandos (`python -m src.<script>` de
   cada Issue e `uvicorn src.api:app`), os achados de `docs/10` e `docs/11` com números dos JSON e
   um link para `docs/09-uso-do-bob.md`.
2. Entregue no relatório uma proposta de ajuste dos Textos 1 e 2 (até 500 palavras cada), sem
   alterar arquivos para isso: o líder atualiza o documento de entrega.

**Critérios de aceite:** números iguais aos dos JSON; todos os comandos do README funcionam.

---

## #33 — feat: conecta o agente ao watsonx Orchestrate (opcional)

- **Branch:** `feature/33-watsonx-orchestrate`. **Depende de:** #26 integrada.
- **Por quê:** o watsonx Orchestrate não é obrigatório no desafio, mas mostra o Sentinela como uma
  ferramenta que um agente da IBM chama, conversando em português com o analista.
- **Arquivos permitidos:** pasta nova `orchestrate/` (definição do agente e da ferramenta),
  `docs/12-watsonx-orchestrate.md` (novo), `docs/04-arquitetura.md`.
- **Antes do Bob (responsável):** ative o trial do watsonx Orchestrate (foi prorrogado; Slack,
  28/10) e instale o ADK seguindo a documentação oficial da IBM. Nenhuma chave entra no
  repositório: use variáveis de ambiente e um `.env` fora do Git.

**Passos**

1. Gere a especificação OpenAPI da API da #26 (`/openapi.json`) e guarde em
   `orchestrate/sentinela-openapi.json`, só com `/analisar` e `/saude`.
2. Seguindo a documentação do ADK do watsonx Orchestrate (cite as páginas consultadas no
   documento), defina em `orchestrate/` uma ferramenta a partir dessa OpenAPI e um agente
   "Sentinela" com instruções em português: receber os dados de uma compra, chamar `/analisar`,
   responder com a decisão, a nota e os sinais, e lembrar que a palavra final é do analista.
3. Para o Orchestrate alcançar a API local, use um túnel temporário só durante a demonstração;
   documente o passo a passo e desligue o túnel depois. Nunca publique dados da base.
4. `docs/12-watsonx-orchestrate.md`: arquitetura (desenho), passo a passo reproduzível, limitações
   e capturas de tela da conversa.

**Critérios de aceite:** um avaliador consegue reproduzir com o documento; uma conversa no
Orchestrate devolve a mesma decisão da API para a mesma transação inventada; nenhuma chave no Git.

---

## #34 — feat: monitora o drift das variáveis (opcional)

- **Branch:** `feature/34-monitor-de-drift`. **Depende de:** #19.
- **Arquivos permitidos:** `src/monitorar_drift.py` (novo), `modelos/drift.json` (gerado),
  `src/interface/secao_drift.py` (novo), `src/interface/pagina_desempenho.py` (só a chamada da
  seção, no fim), bloco #34 (novo, no fim) de `src/interface/textos.py`,
  `tests/test_monitorar_drift.py` (novo).

**Passos**

1. `calcular_psi(referencia: pd.Series, atual: pd.Series, faixas: int = 10) -> float`: Population
   Stability Index com faixas pelos decis da referência; vazios numa faixa própria.
2. `main()`: referência = jan–fev, atual = mar; PSI de cada variável de `VARIAVEIS_MODELO` e da
   nota do modelo; classificação "estável" (< 0,1), "atenção" (0,1 a 0,25) e "mudou" (> 0,25);
   grava `modelos/drift.json`.
3. Seção "Os dados mudaram?" em Desempenho: tabela com o PSI e a classificação; uma frase sobre
   o que fazer quando algo "mudou" (revisar e retreinar).
4. Testes: séries iguais dão PSI perto de 0; deslocadas dão PSI alto; vazios não quebram.

**Critérios de aceite:** portão completo; JSON gerado; seção visível.

---

## #35 — feat: treina um desafiante com as respostas do analista (opcional)

- **Branch:** `feature/35-retreino-desafiante`. **Depende de:** #25 integrada.
- **Arquivos permitidos:** `src/retreinar_desafiante.py` (novo), `modelos/desafiante.json`
  (gerado; só métricas), `tests/test_retreinar_desafiante.py` (novo), `docs/11-avaliacao.md` (só
  acrescentar uma seção no fim).
- **Regra:** o campeão nunca é substituído automaticamente (RF012 continua "Won't" para troca
  automática). O script só compara e recomenda.

**Passos**

1. Leia `data/feedback.csv` (última resposta por transação). Monte o rótulo de treino: o rótulo da
   base, trocado pela resposta do analista quando houver.
2. Treine em memória um desafiante com a mesma receita do campeão e os mesmos meses; avalie os dois
   em março; grave em `modelos/desafiante.json` só métricas e a contagem de rótulos trocados.
3. Se houver menos de 20 respostas, não treine: grave o motivo no JSON e imprima o aviso.
4. Seção nova no fim de `docs/11-avaliacao.md` explicando o fluxo de governança: o analista
   responde, o desafiante é medido, uma pessoa decide a troca.
5. Testes com dados inventados: poucas respostas não treinam; resposta do analista troca o rótulo.

**Critérios de aceite:** portão completo; o campeão em `modelos/` não muda.

---

# Aplicação web (Issues #37 a #48, #30 e #32)

O Sentinela vira uma aplicação web: API em FastAPI (`src/api/`), auditoria por IA no watsonx.ai
(`src/auditoria/`) e site em Next.js com Carbon (`web/`). Fontes: ESPECIFICACAO, seções 12 a 14;
ADR-011 a ADR-013. As regras comuns da parte "Incrementos" continuam valendo (campeão intocável,
invariantes, portão com `data/`, um arquivo um dono, scripts novos, privacidade), e mais estas:

- **O contrato manda.** Campos, rotas e códigos de resposta são os da ESPECIFICACAO, seção 12. O
  site usa só os tipos de `web/lib/tipos.ts`. Faltou algo? Pare e pergunte (AGENTS.md, seção 14).
- **Conformidade da API.** `tests/test_conformidade_api.py` é do líder e intocável; cada Issue de
  API termina com ele sem falhas (com `data/` presente).
- **Site com mocks.** Até a API estar em `develop`, o site roda com `NEXT_PUBLIC_USAR_MOCK=1`.
  Depois, a verificação manual é feita com a API real.
- **Streamlit congelado.** `app.py` e `src/interface/` só recebem correção de defeito.
- **Sem Docker e sem Playwright** (disco). Testes do site com Vitest e Testing Library.

| # | Título | Dono | Revisor | Branch | Depende de |
| --- | --- | --- | --- | --- | --- |
| 37 | docs: redefine a arquitetura para web com auditoria por IA | Pedro Muller | Pedro Machado | `feature/37-arquitetura-web` | — |
| 38 | feat: cria a API do Sentinela | Pedro Machado | Lucas | `feature/38-api` | #37 |
| 39 | feat: audita as decisões com IA no watsonx.ai | Pedro Muller | Bruno | `feature/39-auditoria-ia` | #37 (liga na API depois da #38) |
| 40 | feat: cria a base do site | Mariana | Bruno | `feature/40-base-do-site` | #37 |
| 41 | feat: explica o que pesou na nota | Bruno | Mariana | `feature/41-explicabilidade` | #37 (liga na API depois da #38) |
| 42 | feat: avalia o modelo com rigor e calcula o custo da fraude | Lucas | Pedro Machado | `feature/42-avaliacao-e-custo` | #37 |
| 43 | feat: cria a fila de alertas e o painel da transação no site | Bruno | Mariana | `feature/43-fila-e-painel` | #40 |
| 44 | feat: cria as páginas Desempenho e Como funciona no site | Lucas | Pedro Machado | `feature/44-desempenho-e-como-funciona` | #40 |
| 45 | feat: cria o simulador e a página de respostas no site | Mariana | Bruno | `feature/45-simulador-e-respostas` | #40 |
| 46 | feat: compara a auditoria por IA com o modelo | Pedro Muller | Lucas | `feature/46-ia-contra-modelo` | #38, #39 |
| 47 | feat: documenta a análise exploratória dos dados | Pedro Machado | Lucas | `feature/47-analise-exploratoria` | #37 |
| 48 | fix: corrige a acessibilidade e a responsividade do site | Mariana | Bruno | `feature/48-acessibilidade` | #43, #44, #45 |
| 30 | docs: registra o uso do IBM Bob | Pedro Muller | Mariana | `feature/30-uso-do-bob` | todas |
| 32 | docs: atualiza o README e os textos e aposenta o Streamlit | Pedro Muller | Lucas | `feature/32-readme-e-textos` | todas |

---

## #37 — docs: redefine a arquitetura para web com auditoria por IA

- **Branch:** `feature/37-arquitetura-web`. Feita pelo líder (documentação e testes do líder).
- **Entrega:** ESPECIFICACAO, seções 10 (nota) e 12 a 14; ADR-011 a ADR-013 em
  `docs/07-decisoes.md`; AGENTS.md (seções 2, 9, 11 e 12); `tests/test_conformidade_api.py`;
  `.env.example`; `.gitignore`; esta parte do backlog; `docs/01-requisitos.md`;
  `docs/04-arquitetura.md`.
- **Critérios de aceite:** portão completo; `tests/test_conformidade_api.py` todo pulado com o
  motivo "Issue #38 ainda não implementada"; revisão do Bob (seção 16) sem pendência.

---

## #38 — feat: cria a API do Sentinela

- **Branch:** `feature/38-api`.
- **Ler:** AGENTS.md; ESPECIFICACAO, seções 8, 10, 12 e 13 (só a interface `auditar` e o objeto
  Auditoria); `src/agente.py`; `src/interface/dados.py` (`montar_fila`) e
  `src/interface/feedback.py`; `tests/test_conformidade_api.py`.
- **Arquivos permitidos:** `src/api/__init__.py`, `src/api/app.py`, `src/api/esquemas.py`
  (modelos Pydantic), `src/api/servicos.py` (carga de dados, fila, análise, respostas e métricas),
  `src/api/auditorias.py` (execução em segundo plano e dicionário em memória),
  `src/explicabilidade.py` (só o esqueleto: `contribuicoes(pipeline, transacao) -> list[dict]`
  devolvendo `[]`, com TODO para a #41), `src/config.py` (só `API_ORIGENS_PERMITIDAS`),
  `requirements-api.txt`, `.github/workflows/qualidade.yml` (instalar `requirements-api.txt`),
  `tests/test_api.py`, `docs/04-arquitetura.md`, `docs/06-sequencias.md`.

**Passos**

1. `requirements-api.txt` com `fastapi`, `uvicorn` e `httpx`, versões fixadas com `==` (as que o
   `pip` instalar hoje). Instale no `.venv`.
2. Implemente cada rota da seção 12.2 com modelos Pydantic de entrada e saída. Reaproveite o
   núcleo: `calcular_sinais`, `pontuar`, `decidir` e o texto de reserva de `explicar(...,
   usar_llm=False)`; `montar_fila(base, agente.analisar_lote)`; `RespostaAnalista` e
   `registrar_resposta`/`ler_ultima_resposta` de `feedback.py`. Não reescreva regra de negócio.
   Atenção a três diferenças do contrato: (a) a Analise da API não é o dicionário de
   `analisar()`: não expõe `fonte_explicacao` e acrescenta `contribuicoes` (lista vazia até a
   #41) e `latencia_ms`; (b) a coluna `resposta_analista` do CSV vira o campo `resposta` no JSON;
   (c) `POST /api/respostas` confere se `id_transacao` está na fila antes de gravar, senão 404.
3. Carga única na subida (`lifespan`): parquet, agente com `base` e fila. Falta de arquivo não
   derruba a API: `/api/saude` informa e as rotas de dados respondem 503 com o comando a rodar.
4. Auditoria: `POST /api/analisar` com `auditar` e `POST /api/transacoes/{id}/auditoria` criam um
   id (`uuid4().hex`), guardam `status="pendente"` e disparam em segundo plano
   `src.auditoria.auditar(transacao, analise)`. Se `src.auditoria` ainda não existir (antes da
   #39), a auditoria termina com `status="erro"` e `mensagem` "Auditoria por IA ainda não
   instalada.". `/api/saude` devolve `"auditoria": "watsonx"` só se as duas variáveis
   `WATSONX_APIKEY` e `WATSONX_PROJECT_ID` estiverem definidas; senão `"local"`.
5. `latencia_ms` com `time.perf_counter()` em volta de sinais + nota + decisão.
6. Converta `NaN` em `null` e datas em ISO 8601 antes de responder.
7. `tests/test_api.py`: casos que a conformidade não cobre (por exemplo, 503 sem dados com
   `monkeypatch`, conversão de NaN, concordância de `/api/respostas` com dados inventados).
8. Atualize o C4 (contêineres API e site) e acrescente a sequência "decisão imediata e auditoria
   em paralelo".

**Conflito previsto:** a #40 acrescenta um job "Site" ao mesmo `.github/workflows/qualidade.yml`.
A #38 só acrescenta a instalação de `requirements-api.txt` no job existente; quem integrar depois
roda `git merge develop` e preserva os dois.

**Critérios de aceite:** portão completo; `tests/test_conformidade_api.py` sem falhas, com os
testes da auditoria concluída pulados ("Issue #39 ainda não implementada"); `uvicorn
src.api.app:app --port 8000` sobe e `http://localhost:8000/docs` lista as rotas; invariantes iguais.

---

## #39 — feat: audita as decisões com IA no watsonx.ai

- **Branch:** `feature/39-auditoria-ia`. **Antes do Bob (responsável):** criar no IBM Cloud o
  projeto do watsonx.ai e a API key, preencher o `.env` local e conferir no Prompt Lab qual Granite
  com chamada de ferramentas está disponível (vai em `WATSONX_MODELO`).
- **Ler:** AGENTS.md; ESPECIFICACAO, seções 5, 8, 12 e 13; ADR-012 e ADR-013; `src/agente.py`;
  `src/api/` (depois da #38).
- **Arquivos permitidos:** `src/auditoria/__init__.py`, `src/auditoria/ferramentas.py`,
  `src/auditoria/watsonx.py`, `src/auditoria/local.py`, `src/auditoria/relatorio.py`
  (validação e parecer), `src/config.py` (só `AUDITORIA_MAX_ITERACOES`, `AUDITORIA_TIMEOUT_S`,
  `WATSONX_URL_PADRAO` e `AUDITORIA_MODELO_PADRAO`), `src/api/servicos.py` e
  `src/api/auditorias.py` (só para passar a base às ferramentas), `tests/test_auditoria.py`,
  `docs/06-sequencias.md`.

**Passos**

1. `ferramentas.py`: as 5 ferramentas da seção 13, cada uma uma função pura sobre o parquet
   carregado, com o envelope `{"status", "dados", "campos_ausentes"}` e a definição de ferramenta
   (nome, descrição em português, esquema JSON dos parâmetros) para o chat do watsonx.ai.
2. `relatorio.py`: validação do Relatorio (campos, valores permitidos, 600 caracteres) e a
   função do parecer da seção 13.
3. `local.py`: o modo local da seção 13.
4. `watsonx.py`: token IAM com cache até expirar; laço do chat com ferramentas (o modelo pede uma
   ferramenta, o código executa e devolve o resultado) até a resposta final, com
   `AUDITORIA_MAX_ITERACOES` e `AUDITORIA_TIMEOUT_S`; instruções da seção 13; resposta final em
   JSON validada, uma nova tentativa se inválida. Toda falha (`requests.RequestException`,
   `ValueError`, `KeyError`, tempo esgotado) cai no modo local, com log sem a chave.
5. `__init__.py`: `auditar(transacao, analise)` escolhe watsonx (com credenciais) ou local e
   devolve o Relatorio com `ferramentas_usadas` preenchido.
6. `tests/test_auditoria.py` com `monkeypatch` em `requests` (sem rede): laço com uma chamada de
   ferramenta e resposta final; JSON inválido duas vezes cai no modo local; tempo esgotado cai no
   modo local; parecer CONFIRMA, DIVERGE e INCONCLUSIVO; nenhuma ferramenta devolve chave proibida.
7. Verificação manual com credenciais: 3 transações da fila (uma de cada decisão) auditadas pelo
   watsonx.ai, com o relatório colado no PR (sem identificadores).

**Critérios de aceite:** portão completo; conformidade da API sem falhas e sem pulos da #39;
relatórios reais do watsonx.ai no PR; sem credenciais, tudo funciona em modo local.

---

## #40 — feat: cria a base do site

- **Branch:** `feature/40-base-do-site`.
- **Ler:** AGENTS.md (seções 6 e 11); ESPECIFICACAO, seções 12 e 14;
  `docs/08-design-da-interface.md`, seções 1 a 6 e 11 (tom, cores e textos, para reaproveitar).
- **Arquivos permitidos:** tudo dentro de `web/` e `.github/workflows/qualidade.yml` (job novo
  do site).

**Passos**

1. Projeto Next.js (App Router) com TypeScript estrito em `web/`, com `@carbon/react` e `sass`;
   scripts `dev`, `build`, `lint` (ESLint), `typecheck` (`tsc --noEmit`), `test` (Vitest) e
   `format` (Prettier). Versões fixadas no `package.json` e `package-lock.json` versionado.
2. Tema Carbon claro (`g10`), cabeçalho "Sentinela" e menu lateral com as 5 rotas da seção 14, e
   uma página por rota com título e "Em preparação na Issue #N.", assim: `/` → #43,
   `/desempenho` → #44, `/como-funciona` → #44, `/simulador` → #45, `/respostas` → #45.
3. `web/lib/tipos.ts` (espelho da seção 12), `web/lib/api.ts` (uma função por rota, com erro em
   português quando a API não responde), `web/lib/mocks/` (dados inventados para cada rota,
   incluindo uma auditoria que passa de "pendente" a "concluida"), `web/lib/textos.ts` e
   `web/lib/formatacao.ts` com testes de todos os formatos da seção 14. Em `web/lib/textos.ts`,
   crie um bloco comentado vazio por Issue (`// --- Issue #43 ---`, #44, #45, #48): cada Issue
   seguinte só acrescenta textos dentro do próprio bloco, para os merges não conflitarem.
   O job "Site" no CI é novo; não altere o job Python existente (a #38 mexe nele).
4. Componentes comuns: `FaixaDecisao` (Aprovar, Pedir confirmação, Bloquear, com ícone e texto,
   nunca só cor), `BarraNota`, `EstadoCarregando`, `EstadoVazio`, `EstadoErro`.
5. Job "Site" no CI: `npm ci`, lint, typecheck, test e build dentro de `web/`.

**Critérios de aceite:** portão do site e do Python; `NEXT_PUBLIC_USAR_MOCK=1 npm run dev` abre
as 5 páginas; os componentes comuns têm teste; CI verde.

---

## #41 — feat: explica o que pesou na nota

- **Branch:** `feature/41-explicabilidade`.
- **Arquivos permitidos:** `src/explicabilidade.py`, `src/api/servicos.py` (só para preencher
  `contribuicoes`), `tests/test_explicabilidade.py`.

**Passos**

1. Com o pipeline salvo (`imputer` → `scaler` → `modelo`), sem treinar nada:
   `contribuicoes(pipeline, transacao) -> list[dict]` aplica `imputer` e `scaler` e devolve
   `{"variavel", "nome", "contribuicao"}` para cada coluna da regressão (as 11 variáveis e os
   indicadores de vazio), com `contribuicao = coeficiente × valor padronizado`, ordenado por
   valor absoluto; `importancia_global(pipeline) -> list[dict]`; `NOMES_LEGIVEIS` em português
   (indicador de vazio vira "<nome> ausente").
2. A API passa a preencher `contribuicoes` em toda Analise.
3. Testes com um pipeline pequeno treinado no teste com dados inventados: a soma das
   contribuições mais o intercepto é o log-odds; ordenação; nomes para todas as colunas.

**Critérios de aceite:** portão completo; conformidade da API sem falhas; `/api/transacoes/{id}`
traz contribuições coerentes (transação bloqueada com contribuições positivas grandes).

---

## #42 — feat: avalia o modelo com rigor e calcula o custo da fraude

- **Branch:** `feature/42-avaliacao-e-custo`.
- **Arquivos permitidos:** `src/avaliar_rigor.py`, `src/analisar_custos.py`,
  `modelos/avaliacao_rigorosa.json`, `modelos/custos.json` (gerados), `docs/11-avaliacao.md`,
  `tests/test_avaliar_rigor.py`, `tests/test_analisar_custos.py`.

**Passos:** os passos 1 e 2 da #28 (avaliação rigorosa) e os passos 1 e 2 da #20 (custo), na parte
"Incrementos" acima, sem as seções do Streamlit. `docs/11-avaliacao.md` traz as duas análises,
com uma leitura em português de cada tabela.

**Critérios de aceite:** portão completo; os dois JSON gerados pelos scripts e expostos em
`/api/metricas` (`extras`); números do documento iguais aos dos JSON.

---

## #43 — feat: cria a fila de alertas e o painel da transação no site

- **Branch:** `feature/43-fila-e-painel`.
- **Ler:** ESPECIFICACAO, seções 12 a 14; `docs/08-design-da-interface.md`, seção 7 (a fila e o
  painel do Streamlit, como referência de conteúdo e textos); `web/`.
- **Arquivos permitidos:** `web/app/page.tsx`, `web/components/fila/**`,
  `web/components/painel/**`, `web/lib/textos.ts` (só acrescentar), testes desses componentes.

**Passos**

1. Fila: quatro indicadores (na fila, bloquear, pedir confirmação, aprovar) de `contagens`; filtro
   de decisões (padrão: Bloquear e Pedir confirmação); tabela do Carbon com ID, nota (barra),
   decisão, valor, data e hora, tipo, modalidade e sinais, ordenável, com seleção de linha.
2. Painel da transação selecionada (`/api/transacoes/{id}`): cabeçalho com data, tipo,
   modalidade e valor; `FaixaDecisao`; `BarraNota` com "Nota de risco: N de 100"; sinais; gráfico
   de barras horizontais "O que pesou na nota" (6 maiores contribuições; vazio enquanto a #41 não
   entrar); explicação do modelo.
3. Cartão "Auditoria da IA": ao abrir a transação, `POST /api/transacoes/{id}/auditoria` e
   consulta a cada 2 s (seção 14). Pendente: carregando com "A IA está auditando esta decisão…".
   Concluída: parecer em destaque (Confirma, Diverge, Inconclusivo; Diverge com aviso de
   atenção), risco e confiança, explicação, evidências a favor e contra, dados ausentes, fonte
   (watsonx.ai ou modo local) e a lista "Ferramentas usadas" na ordem. Erro: mensagem e "Tentar de
   novo".
4. Resposta do analista: botões "Confirmar fraude" e "Marcar como legítima" de mesmo peso,
   `POST /api/respostas`, aviso de sucesso e "Sua resposta: …".
5. Testes com os mocks: filtro, seleção, os três estados da auditoria e a gravação da resposta.

**Critérios de aceite:** portão do site; com a API real, a fila mostra 2.054 / 54 / 25 / 1.975 e a
auditoria aparece depois da decisão; verificação manual no PR.

---

## #44 — feat: cria as páginas Desempenho e Como funciona no site

- **Branch:** `feature/44-desempenho-e-como-funciona`.
- **Arquivos permitidos:** `web/app/desempenho/**`, `web/app/como-funciona/**`,
  `web/components/desempenho/**`, `web/components/como-funciona/**`, `web/lib/textos.ts` (só
  acrescentar), testes desses componentes.

**Passos**

1. Desempenho (`/api/metricas`): os cinco indicadores e a comparação com o sistema atual (os da
   seção 8 do design); detalhes do modelo; e, quando presentes nos `extras`: "Quão confiável é o
   resultado" (avaliação rigorosa), "Custo da fraude" (custos), "Modelo e IA lado a lado"
   (`ia_contra_modelo`: latência e concordância). Extra ausente: a seção não aparece.
2. Como funciona: o caminho de uma compra (decisão imediata e auditoria em paralelo), os 9 sinais
   com os limiares, as regras de decisão, "O que os dados mostram" (`eda`, quando presente) e as
   limitações.
3. Gráficos com componentes do Carbon Charts (`@carbon/charts-react`) ou SVG simples; legenda e
   texto alternativo em todos.
4. Testes com os mocks, incluindo extras ausentes.

**Critérios de aceite:** portão do site; números iguais aos dos JSON; verificação manual no PR.

---

## #45 — feat: cria o simulador e a página de respostas no site

- **Branch:** `feature/45-simulador-e-respostas`.
- **Arquivos permitidos:** `web/app/simulador/**`, `web/app/respostas/**`,
  `web/components/simulador/**`, `web/components/respostas/**`, `web/lib/textos.ts` (só
  acrescentar), testes desses componentes.

**Passos**

1. Simulador: escolher uma transação da fila; controles para valor, hora, crédito, cartão não
   presente, IP desconhecido, rajada no minuto, uso em terminais na hora, token em 3 meses,
   distância e risco do estabelecimento (madrugada calculada pela hora, nunca editada). Botão
   "Analisar" → `POST /api/analisar` com `auditar: true`: mostra "Original" e "Simulada" lado a
   lado (decisão, nota, sinais) na hora e, quando chegar, o parecer da IA para a simulada.
   "Voltar aos valores originais".
2. Respostas: `GET /api/respostas` com total, fraudes, legítimas e concordância; tabela; botão
   "Exportar CSV" gerado no navegador; estado vazio explicando como responder na Fila.
3. Testes com os mocks.

**Critérios de aceite:** portão do site; mudar a hora para 3 acende "madrugada"; zerar as rajadas
de uma fraude baixa a nota; verificação manual no PR.

---

## #46 — feat: compara a auditoria por IA com o modelo

- **Branch:** `feature/46-ia-contra-modelo`. **Precisa:** credenciais do watsonx.ai.
- **Arquivos permitidos:** `src/avaliar_ia.py`, `modelos/ia_contra_modelo.json` (gerado),
  `docs/11-avaliacao.md` (só acrescentar uma seção), `tests/test_avaliar_ia.py`.

**Passos**

1. Amostra de março: todas as 54 fraudes e 200 legítimas sorteadas com `SEMENTE`.
2. Para cada transação: decisão do modelo (com tempo) e auditoria (com tempo), em sequência, com
   pausa se o watsonx.ai limitar a taxa.
3. Grave só agregados: latência p50 e p95 do modelo e da IA (ms); distribuição dos pareceres;
   concordância por decisão; recall e precisão da IA sozinha (risco ALTO ou SUSPEITO conta como
   alerta) comparados aos do modelo na mesma amostra; quantas auditorias caíram no modo local.
4. Seção "Modelo e IA lado a lado" em `docs/11-avaliacao.md`, com a leitura: por que o modelo
   decide e a IA audita.
5. Testes com uma auditoria falsa (monkeypatch) e 5 transações inventadas.

**Critérios de aceite:** portão completo; JSON gerado com o watsonx.ai real (registrar no PR
quantas foram para o modo local); exposto em `/api/metricas`.

---

## #47 — feat: documenta a análise exploratória dos dados

- **Branch:** `feature/47-analise-exploratoria`.
- **Arquivos permitidos:** `src/analisar_dados.py`, `modelos/eda.json` (gerado),
  `docs/10-analise-exploratoria.md`, `tests/test_analisar_dados.py`.

**Passos:** os passos 1 a 3 e 5 da #31, na parte "Incrementos" acima (sem a seção do Streamlit).
O JSON fica exposto em `/api/metricas` (`extras.eda`).

**Critérios de aceite:** portão completo; 160.000 linhas e 146 fraudes no JSON; documento coerente
com o JSON.

---

## #48 — fix: corrige a acessibilidade e a responsividade do site

- **Branch:** `feature/48-acessibilidade`.
- **Antes do Bob (responsável):** Lighthouse (Accessibility) no Chrome nas 5 páginas, zoom de
  200% e janela de 768 px; registre as notas e os problemas num comentário da Issue.
- **Arquivos permitidos:** `web/**` (exceto `web/lib/tipos.ts` e `web/lib/api.ts`).

**Passos:** corrigir cada problema registrado, um commit por problema; refazer o Lighthouse e
registrar as notas finais no PR.

**Critérios de aceite:** Lighthouse Accessibility ≥ 90 nas 5 páginas (ou os itens restantes como
Issue nova); zoom de 200% e 768 px sem conteúdo cortado; portão do site.

---

## #30 (atualizada) — docs: registra o uso do IBM Bob

Como na parte "Incrementos", passos 1 a 3, acrescentando ao documento a mudança de arquitetura de
12/11 (Streamlit → web com auditoria por IA) e como o contrato da API e os testes de conformidade
deixaram backend e site serem feitos em paralelo pelo Bob.

---

## #32 (atualizada) — docs: atualiza o README e os textos e aposenta o Streamlit

- **Arquivos permitidos:** `README.md`, `docs/README.md` e, se o site cobrir tudo o que o
  Streamlit mostra, a remoção de `app.py`, `src/interface/pagina_*.py`, `src/interface/secao_*.py`,
  `src/interface/painel_*.py` e dos testes deles, com um ADR novo (o líder decide e escreve o ADR).
  `src/interface/dados.py` e `feedback.py` ficam (a API usa).
- **Passos:** README com a arquitetura nova, como rodar a API e o site, os achados de
  `docs/10` e `docs/11` com números dos JSON e o link para `docs/09-uso-do-bob.md`; proposta dos
  Textos 1 e 2 no relatório.
