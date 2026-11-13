# Sentinela — agente antifraude para compras com cartão

**Desafio Sicredi · IBM SkillsBuild AI Experiential Learning Lab · time Loucurada pela IDE II**

Para cada compra, o Sentinela calcula 9 sinais de alerta, dá uma nota de risco de 0 a 100
(regressão logística) e decide **na hora**: aprovar, pedir confirmação ao associado ou bloquear.
Em paralelo, um agente no **IBM watsonx.ai** audita a decisão com ferramentas (confirma, diverge
ou inconclusivo) sem atrasá-la, e o associado é avisado pelo app. Um analista revisa tudo no site.

## Resultados (março de 2025: 13.608 compras, 54 fraudes)

| Indicador | Sentinela | Sistema atual |
| --- | --- | --- |
| Fraudes bloqueadas | **54 de 54** | 26 de 54 |
| Compras legítimas bloqueadas | **0** | — |
| Pedidos de confirmação | 159 (1,2%) | — |
| Tempo de decisão | cerca de 1,5 ms | — |

Os dados são 100% sintéticos; com dados reais, os números seriam menores e o modelo precisaria de
monitoramento e retreino.

## Arquitetura

```
Site (Next.js + Carbon, web/)  ──HTTP──>  API (FastAPI, src/api/)
                                            ├─ Núcleo: sinais, nota e decisão (src/agente.py)
                                            ├─ Auditoria em paralelo (src/auditoria/) ──> watsonx.ai
                                            └─ Canal do associado (src/associado/)
```

Detalhes em [docs/arquitetura.md](docs/arquitetura.md).

## Como rodar

Pré-requisitos: Python 3.14, Node 22 e o CSV da Sicredi em
`data/case_transacoes_cartoes_sintetico_900k.csv` (não versionado).

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
python -m src.preparar_dados                        # gera data/transacoes_preparadas.parquet
uvicorn src.api.app:app --port 8000                 # API em http://localhost:8000/docs
```

Em outro terminal:

```bash
cd web && npm install && npm run dev                # site em http://localhost:3000
```

Sem a API, o site roda com dados simulados: `NEXT_PUBLIC_USAR_MOCK=1 npm run dev`.

**watsonx.ai (opcional):** copie `.env.example` para `.env` e preencha as credenciais. Sem elas, a
auditoria usa o modo local (regra dos sinais) e todo o resto funciona igual.

## Qualidade

```bash
python -m black --check . && python -m ruff check . && python -m pytest -q
python -m src.avaliar_agente                        # confere os números acima
cd web && npm run lint && npm run typecheck && npm test && npm run build
```

O CI "Qualidade" roda tudo isso em todo Pull Request (sem `data/`, ele pula os testes que dependem
dos dados).

## Estrutura

```
AGENTS.md           regras de trabalho do IBM Bob
ESPECIFICACAO.md    dados, modelo, agente, API, auditoria, canal e números esperados
src/                núcleo: preparar_dados, treinar_modelo, agente, avaliar_agente, fila, feedback
  api/              API FastAPI
  auditoria/        agente auditor (watsonx.ai ou local)
web/                site Next.js
tests/              pytest; test_conformidade_*.py são a régua de "pronto"
modelos/            modelo treinado e métricas (versionados)
docs/               requisitos, arquitetura, decisões (ADRs) e backlog
data/               dados da Sicredi (fora do Git)
```

## Documentação

| Arquivo | Conteúdo |
| --- | --- |
| [docs/requisitos.md](docs/requisitos.md) | O que o desafio pede e como cada item é atendido |
| [docs/arquitetura.md](docs/arquitetura.md) | Contêineres e o fluxo de uma compra suspeita |
| [docs/decisoes.md](docs/decisoes.md) | Decisões de arquitetura (ADRs) |
| [docs/backlog.md](docs/backlog.md) | Issues, donos e critérios de aceite |

## Como usamos o IBM Bob

O time trabalha com o Bob a partir de Issues com escopo fechado. O `AGENTS.md` define o protocolo
(branch, arquivos permitidos, portão de qualidade, quando parar); a `ESPECIFICACAO.md` fixa o
contrato e os números; os testes de conformidade, escritos pelo líder, dizem quando uma Issue
está pronta, e o Bob não pode alterá-los.
