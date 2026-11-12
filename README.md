# Sentinela — Agente antifraude para transações de cartão

**Desafio IBM SkillsBuild AI Lab · Sicredi**

O Sentinela analisa transações de cartão de crédito e débito, calcula uma nota de risco de 0 a 100
com regressão logística, decide entre _Aprovar_, _Pedir confirmação ao cliente_ ou _Bloquear e
enviar ao analista_, explica a decisão em português (IBM Granite 4 via Ollama ou texto automático
de reserva) e registra a resposta do analista para retreino futuro. Um analista humano revisa
tudo numa interface Streamlit rodando na própria máquina.

---

## O problema

Fraudes em cartões causam prejuízo imediato à cooperativa e ao associado. O sistema atual da
Sicredi bloqueou 26 das 54 fraudes no período de teste (48,1 %), deixando passar 28 fraudes. O Sentinela
bloqueia as 54 (100 %), sem bloquear nenhuma compra legítima, e ainda sinaliza 159 transações para
confirmação do cliente — tudo com dados 100 % sintéticos fornecidos pela Sicredi.

## A solução em 5 linhas

1. Prepara as 160.000 transações sintéticas, retendo apenas as 16 colunas necessárias.
2. Treina uma regressão logística com validação temporal (treino: jan–fev/2025; teste: mar/2025).
3. Para cada transação: calcula 9 sinais de alerta por regras, atribui uma nota de risco de 0 a
   100 e decide APROVAR, PEDIR\_CONFIRMACAO ou BLOQUEAR.
4. Explica a decisão em 3 frases via IBM Granite 4 (local) ou monta texto automático por regras.
5. O analista revisa numa interface Streamlit, confirma ou discorda, e a resposta é gravada para
   retreino futuro.

---

## Resultados reais (março de 2025, 13.608 transações, 54 fraudes)

| Indicador | Sentinela | Sistema atual |
| --- | --- | --- |
| Fraudes bloqueadas | **54 de 54** (100,0 %) | 26 de 54 (48,1 %) |
| Compras legítimas bloqueadas | **0** | — |
| Pedidos de confirmação | **159** | — |
| PR-AUC / ROC-AUC | **1,0 / 1,0** | — |

> Os dados são 100 % sintéticos. Valores próximos de 1,0 são esperados e não refletem
> desempenho em produção com dados reais.

---

## Pré-requisitos

- Python 3.14 (a versão usada no desenvolvimento e no CI)
- O arquivo `data/case_transacoes_cartoes_sintetico_900k.csv` (fornecido pela Sicredi; ~294 MB;
  não versionado)
- **Ollama com IBM Granite 4 (opcional):** sem ele, o agente usa o texto automático de reserva.

## Como instalar e rodar

```bash
# 1. Criar e ativar o ambiente virtual
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate         # Windows

# 2. Instalar dependências
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 3. Preparar os dados (precisa do CSV em data/)
python -m src.preparar_dados

# 4. Treinar o modelo
python -m src.treinar_modelo

# 5. Avaliar o agente (gera modelos/avaliacao_agente.json)
python -m src.avaliar_agente

# 6. Verificar qualidade e rodar os testes
python -m black --check .
python -m ruff check .
python -m pytest -q

# 7. Abrir a interface
streamlit run app.py
```

### Ollama e IBM Granite 4 (opcional)

Se quiser as explicações geradas pelo IBM Granite 4, instale o Ollama e baixe o modelo:

```bash
# Instalar o Ollama (https://ollama.com)
curl -fsSL https://ollama.com/install.sh | sh   # Linux/macOS
# ou baixe o instalador em https://ollama.com/download/windows  # Windows

# Baixar o modelo
ollama pull granite4:micro
```

Com o Ollama em execução, ative o interruptor "Explicar com IBM Granite" na barra lateral da
interface. Sem o Ollama, a interface usa o texto automático de reserva — o fluxo completo
funciona normalmente.

---

## Estrutura de pastas

```
AGENTS.md                         regras de trabalho do IBM Bob
ESPECIFICACAO.md                  dados, modelo, agente e números esperados
README.md
requirements.txt                  dependências de execução, versões fixadas
requirements-dev.txt              black e ruff
pyproject.toml                    configuração de Black, Ruff e pytest
conftest.py
app.py                            ponto de entrada da interface (navegação)
.streamlit/config.toml            tema da interface
.github/workflows/qualidade.yml   CI: Black, Ruff e pytest em todo Pull Request
src/
  config.py                       limiares, caminhos, URLs e constantes
  preparar_dados.py               etapa 1: parquet com 16 colunas
  treinar_modelo.py               etapa 2: regressão logística + métricas
  agente.py                       etapa 3: sinais, nota, decisão, explicação
  avaliar_agente.py               etapa 4: avaliação em março de 2025
  interface/
    tema.py                       ícones, cores e rótulos de cada decisão
    textos.py                     todos os textos da tela
    formatacao.py                 moeda, data, nota e percentual em pt-BR
    dados.py                      carga em cache, fila e estado do Granite
    feedback.py                   gravação e leitura das respostas do analista
    pagina_fila.py                página principal: fila e painel
    pagina_desempenho.py          comparação com o sistema atual
    pagina_como_funciona.py       como o agente decide
tests/
  test_agente.py                  testes do núcleo (sinais, decisão, agente)
  test_formatacao.py              testes de formatação pt-BR
  test_feedback.py                testes de gravação e leitura de respostas
  test_fila.py                    testes da fila de alertas
  test_app.py                     testes de fumaça da interface (pula sem dados)
  test_conformidade_nucleo.py     testes do líder: invariantes do núcleo
  test_conformidade_interface.py  testes do líder: invariantes da interface
modelos/
  sentinela.joblib                modelo treinado (versionado)
  metricas.json                   métricas no conjunto de teste
  avaliacao_agente.json           avaliação do agente em março de 2025
data/                             não versionado (CSV, parquet, feedback.csv)
docs/                             documentação do projeto (ver abaixo)
```

---

## Documentação

| Arquivo | O que responde |
| --- | --- |
| [docs/01-requisitos.md](docs/01-requisitos.md) | Requisitos funcionais e não funcionais (MoSCoW) |
| [docs/02-user-stories.md](docs/02-user-stories.md) | Histórias e critérios em BDD |
| [docs/03-user-flows.md](docs/03-user-flows.md) | Jornadas do analista, incluindo caminhos de erro |
| [docs/04-arquitetura.md](docs/04-arquitetura.md) | Arquitetura C4 (contexto, contêineres, componentes) |
| [docs/06-sequencias.md](docs/06-sequencias.md) | Sequências com o Granite e com duplo clique |
| [docs/07-decisoes.md](docs/07-decisoes.md) | Registro de decisões arquiteturais (ADRs) |
| [docs/08-design-da-interface.md](docs/08-design-da-interface.md) | Design da interface: layout, textos e estados |
| [docs/backlog.md](docs/backlog.md) | Issues, responsáveis, critérios de aceite |

---

## Como trabalhamos com o IBM Bob

O IBM Bob escreveu e revisou todo o código desta reta final do projeto, seguindo regras explícitas:

- **[`AGENTS.md`](AGENTS.md)** define o protocolo de trabalho: como criar branches, o que pode
  ser alterado em cada Issue, as convenções de código (Black, Ruff, pytest), o idioma
  (português do Brasil), o formato de commits (Conventional Commits) e quando parar e
  perguntar ao líder.
- **[`ESPECIFICACAO.md`](ESPECIFICACAO.md)** define os invariantes: colunas, constantes, modelo,
  sinais, decisão, formato dos arquivos e números exatos esperados. O Bob não inventa nenhum
  valor que não esteja aqui.
- **Issues e Pull Requests:** cada tarefa do [`docs/backlog.md`](docs/backlog.md) é uma Issue
  com branch própria, lista de arquivos permitidos e critérios de aceite objetivos. O Bob
  implementa, o líder (ou um colega designado) revisa segundo a seção 16 do `AGENTS.md`
  (checklist de conformidade, cobertura de testes, nomes, docstrings e diagramas), e o merge
  só acontece com aprovação.
- **CI "Qualidade"** ([`.github/workflows/qualidade.yml`](.github/workflows/qualidade.yml)):
  Black, Ruff e pytest rodam automaticamente em todo Pull Request.
- **Testes de conformidade** (`tests/test_conformidade_nucleo.py` e
  `tests/test_conformidade_interface.py`): escritos pelo líder a partir da especificação e
  do design, independentemente do Bob. Uma Issue com código só é considerada pronta com
  0 falhas nesses testes. O Bob não pode alterá-los.

---

## Limitações

- **Dados 100 % sintéticos:** os números são intencionalmente otimistas. Em produção, com dados
  reais e padrões de fraude variando ao longo do tempo, o modelo precisaria de monitoramento
  contínuo e retreino periódico com as respostas dos analistas.
- **Um usuário por vez:** não há login, multiusuário nem deploy — é um protótipo local.
- **Retreino não automatizado:** as respostas gravadas em `data/feedback.csv` ainda não alimentam
  o treino automaticamente (RF012 fora do escopo).
- **Confirmação ao cliente não integrada:** a decisão PEDIR\_CONFIRMACAO indica a ação, mas o
  envio real ao cliente por app ou SMS não foi implementado (RF014 fora do escopo).
- **IBM Granite local:** a qualidade da explicação depende da disponibilidade do Ollama e do
  tempo de resposta na máquina de cada pessoa.

---

## O time

**Loucurada pela IDE II**

<!-- integrantes: preencher -->

