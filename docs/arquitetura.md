# Arquitetura

O modelo decide na hora; a IA audita em paralelo; o associado é avisado e responde; o analista
decide no fim (ADR-011, ADR-012 e ADR-015). Tudo roda na máquina de quem usa, com dados
sintéticos; só a auditoria sai para o IBM watsonx.ai, sem identificadores.

## Contêineres

```mermaid
graph TB
    ANA["Analista"]
    ASS["Associado<br/><small>App do associado, simulado</small>"]
    AUT["Autorizador de cartões<br/><small>simulado pela API</small>"]

    subgraph Sentinela["Sentinela"]
        SITE["<b>Site</b> · Next.js + Carbon · web/<br/><small>fila, painel, desempenho, simulador,<br/>respostas, app do associado</small>"]
        API["<b>API</b> · FastAPI · src/api/<br/><small>decisão imediata, auditoria, notificações</small>"]
        NUC["<b>Núcleo</b> · src/agente.py, explicabilidade.py<br/><small>sinais, nota, decisão, contribuições</small>"]
        AUD["<b>Auditoria</b> · src/auditoria/<br/><small>5 ferramentas, modo local</small>"]
        CAN["<b>Canal do associado</b> · src/associado/<br/><small>mensagem e respostas</small>"]
        ARQ[("data/ · modelos/")]
    end

    WX["IBM watsonx.ai<br/><small>Granite com ferramentas</small>"]

    ANA -->|"localhost:3000"| SITE
    ASS -->|"localhost:3000/associado"| SITE
    AUT -->|"POST /api/analisar"| API
    SITE -->|"HTTP localhost:8000"| API
    API --> NUC
    API -->|"em paralelo"| AUD
    API --> CAN
    AUD -->|"sem identificadores"| WX
    CAN -->|"redige a mensagem"| WX
    NUC --> ARQ
    API --> ARQ
```

| Pasta | Responsabilidade |
| --- | --- |
| `src/` (raiz) | Dados, modelo, agente, fila e respostas do analista |
| `src/api/` | Rotas (`app.py`), esquemas, serviços, auditorias e respostas |
| `src/auditoria/` | Ferramentas, cliente do watsonx.ai, modo local, relatório e parecer |
| `src/associado/` | Notificações e mensagem ao associado (Issue #62) |
| `web/app/` | Uma pasta por página |
| `web/components/` | Componentes por página (`fila/`, `painel/`, `desempenho/`…) e `comuns/` |
| `web/lib/` | Cliente da API, tipos, textos, formatação, mocks |

## Uma compra suspeita, do começo ao fim

```mermaid
sequenceDiagram
    actor C as Autorizador / Site
    participant A as API
    participant N as Núcleo
    participant T as Auditoria (em paralelo)
    participant W as watsonx.ai
    participant S as Canal do associado
    actor P as Associado
    actor AN as Analista

    C->>A: POST /api/analisar
    A->>N: sinais, nota, decisão
    N-->>A: PEDIR_CONFIRMACAO (≈1,5 ms)
    A->>S: criar notificação (mensagem validada)
    A-->>C: decisão + id_auditoria + id_notificacao
    A->>T: auditar(transação, análise)
    T->>W: chat com ferramentas
    W-->>T: relatório
    T-->>A: CONFIRMA / DIVERGE / INCONCLUSIVO
    P->>A: "Não fui eu" (App do associado)
    A->>S: status negada → compra bloqueada, caso para o analista
    AN->>A: abre o caso: decisão, parecer da IA e resposta do associado
    AN->>A: Confirmar fraude
```

A auditoria e a notificação nunca atrasam a decisão. Sem credenciais do watsonx.ai, a auditoria
e a mensagem usam o modo local e o resto funciona igual.
