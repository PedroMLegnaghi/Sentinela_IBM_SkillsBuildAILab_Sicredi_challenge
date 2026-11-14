# Sentinela — agente antifraude para compras com cartão

**Desafio Sicredi · IBM SkillsBuild AI Experiential Learning Lab · time Loucurada pela IDE II**

Para cada compra, o Sentinela calcula 9 sinais de alerta, dá uma nota de risco de 0 a 100
(regressão logística) e decide **na hora**: aprovar, pedir confirmação ao associado ou bloquear.
Em paralelo, um agente no **IBM watsonx.ai** (IBM Granite) audita a decisão com 5 ferramentas
(confirma, diverge ou inconclusivo) sem atrasá-la. O associado recebe no app um aviso redigido
pelo Granite e responde "fui eu" ou "não fui eu". Um analista revisa tudo no site.

## Resultados (março de 2025: 13.608 compras, 54 fraudes)

O modelo foi treinado só com janeiro e fevereiro e testado em março.

| Indicador | Sentinela | Sistema atual |
| --- | --- | --- |
| Fraudes bloqueadas | **54 de 54** | 26 de 54 |
| Compras legítimas bloqueadas | **0** | — |
| Pedidos de confirmação | 159 (1,2%) | — |
| Valor das fraudes que passaram | **R$ 0,00** | R$ 6.654,16 |
| Prejuízo evitado contra o sistema atual | **R$ 6.495,16** (já descontado R$ 1,00 por confirmação) | — |
| Tempo de decisão | cerca de 1,5 ms | — |

Os dados são 100% sintéticos e muito separáveis; com dados reais, os números seriam menores e o
modelo precisaria de monitoramento e retreino.

### O que os dados mostram ([docs/analise-exploratoria.md](docs/analise-exploratoria.md))

- 160.000 compras e 146 fraudes (0,09%), todas entre janeiro e março.
- Todas as 146 fraudes aconteceram de madrugada (0h a 4h); 124 foram no crédito e 135 sem cartão
  presente.
- Os sinais de velocidade separam quase tudo: uso do cartão em terminais na última hora aparece em
  93,2% das fraudes e em 0% das compras legítimas; rajada no último minuto, em 91,1% e 0,001%.

### Avaliação com rigor ([docs/avaliacao.md](docs/avaliacao.md))

- Validação temporal em duas janelas (jan → fev e jan–fev → mar): PR-AUC 1,00 nas duas.
- Bootstrap com 1.000 reamostras: recall e precisão de 1,0 em todas.
- Ablação: sem as 3 variáveis de velocidade, a PR-AUC cai para 0,861; elas carregam o sinal.
- Só regras (4 sinais ou mais) dá 57 alertas para as mesmas 54 fraudes; o gradient boosting empata
  com a regressão logística, que ficou por ser explicável.
- Calibração: Brier 0,000007; as 13.554 legítimas têm nota abaixo de 10 e as 54 fraudes, acima de 70.

### A IA audita o modelo (`modelos/ia_contra_modelo.json`)

254 compras de março (as 54 fraudes e 200 legítimas), todas auditadas pelo watsonx.ai
(`ibm/granite-4-h-small`):

| | Modelo | IA sozinha |
| --- | --- | --- |
| Alertas | 56 | 122 |
| Fraudes encontradas | 54 (recall 100%) | 54 (recall 100%) |
| Precisão | 96,4% | 44,3% |
| Tempo por compra (mediana neste teste) | 5 ms | 6,1 s |

A IA concorda com 88,9% dos bloqueios e com 100% dos pedidos de confirmação; diverge mais nas
compras aprovadas, que o analista pode revisar. Ela acha todas as fraudes, mas alerta mais que o
dobro e é mil vezes mais lenta: por isso o modelo decide e a IA audita (ADR-012).

### O associado no centro ([docs/privacidade.md](docs/privacidade.md))

Quando o Sentinela pede confirmação ou bloqueia, o associado recebe no app uma mensagem redigida
pelo IBM Granite. Ela só é usada se passar nas regras contra golpe (começa com "Sicredi:", até 160
caracteres, sem link, nunca pede senha ou código) e se citar apenas o valor, a data e a hora reais
da compra; senão, vale um modelo fixo. Nenhum identificador de cartão, cliente ou estabelecimento
vai para a IA, para os logs ou para as respostas da API.

## Arquitetura

```
Site (Next.js + Carbon, web/)  ──HTTP──>  API (FastAPI, src/api/)
                                            ├─ Núcleo: sinais, nota e decisão (src/agente.py)
                                            ├─ Auditoria em paralelo (src/auditoria/) ──> watsonx.ai
                                            └─ Canal do associado (src/associado/) ──> watsonx.ai
```

Detalhes em [docs/arquitetura.md](docs/arquitetura.md).

## Como rodar

Pré-requisitos: Python 3.14 e Node 22. Os dados sintéticos da Sicredi já vêm em `data/` (o CSV
comprimido e o parquet preparado).

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
uvicorn src.api.app:app --port 8000                 # API em http://localhost:8000/docs
```

Em outro terminal:

```bash
cd web && npm install && npm run dev                # site em http://localhost:3000
```

Sem a API, o site roda com dados simulados: `NEXT_PUBLIC_USAR_MOCK=1 npm run dev`.

**watsonx.ai (opcional):** copie `.env.example` para `.env` e preencha as credenciais (API key do
IBM Cloud, Project ID do projeto no watsonx.ai, URL da região e `ibm/granite-4-h-small`). Sem elas,
a auditoria usa o modo local (regra dos sinais), a mensagem ao associado usa o modelo fixo e todo
o resto funciona igual.

## Qualidade

```bash
python -m black --check . && python -m ruff check . && python -m pytest -q
python -m src.avaliar_agente                        # confere os números acima
cd web && npm run lint && npm run typecheck && npm test && npm run build
```

O CI "Qualidade" roda tudo isso em todo Pull Request.

Os números das análises saem de scripts que leem o parquet e gravam um JSON em `modelos/`:

```bash
python -m src.analisar_dados      # modelos/eda.json (análise exploratória)
python -m src.avaliar_rigor       # modelos/avaliacao_rigorosa.json
python -m src.analisar_custos     # modelos/custos.json
python -m src.avaliar_ia          # modelos/ia_contra_modelo.json (precisa do .env; ~30 min)
```

Para recriar o parquet a partir do CSV:
`gunzip -k data/case_transacoes_cartoes_sintetico_900k.csv.gz && python -m src.preparar_dados`.

## Estrutura

```
AGENTS.md           regras de trabalho do IBM Bob
ESPECIFICACAO.md    dados, modelo, agente, API, auditoria, canal e números esperados
.bob/               modo personalizado do Bob (Auditor Sentinela)
src/                núcleo: preparar_dados, treinar_modelo, agente, avaliar_agente, fila, feedback
  api/              API FastAPI
  auditoria/        agente auditor (watsonx.ai ou local)
  associado/        mensagem e notificações ao associado
web/                site Next.js
tests/              pytest; test_conformidade_*.py são a régua de "pronto"
modelos/            modelo treinado, métricas e resultados das análises (versionados)
docs/               requisitos, arquitetura, decisões, backlog, análises, privacidade e uso do Bob
data/               dados sintéticos da Sicredi (CSV comprimido, dicionário, parquet)
```

## Documentação

| Arquivo | Conteúdo |
| --- | --- |
| [docs/requisitos.md](docs/requisitos.md) | O que o desafio pede e como cada item é atendido |
| [docs/arquitetura.md](docs/arquitetura.md) | Contêineres e o fluxo de uma compra suspeita |
| [docs/decisoes.md](docs/decisoes.md) | Decisões de arquitetura (ADRs) |
| [docs/analise-exploratoria.md](docs/analise-exploratoria.md) | O que os dados mostram |
| [docs/avaliacao.md](docs/avaliacao.md) | Janelas temporais, bootstrap, comparação, ablação, calibração e custo |
| [docs/privacidade.md](docs/privacidade.md) | O que o Sentinela lê, o que vai para a IA e as regras contra golpe |
| [docs/uso-do-bob.md](docs/uso-do-bob.md) | Como o time usou o IBM Bob, com números do GitHub |
| [docs/backlog.md](docs/backlog.md) | Issues, donos e critérios de aceite |

## Como usamos o IBM Bob

O time trabalha com o Bob a partir de Issues com escopo fechado. O `AGENTS.md` define o protocolo
(branch, arquivos permitidos, portão de qualidade, quando parar); a `ESPECIFICACAO.md` fixa o
contrato e os números; os testes de conformidade, escritos pelo líder, dizem quando uma Issue
está pronta, e o Bob não pode alterá-los. O relato completo, com o que a régua pegou e os números
do processo, está em [docs/uso-do-bob.md](docs/uso-do-bob.md).
