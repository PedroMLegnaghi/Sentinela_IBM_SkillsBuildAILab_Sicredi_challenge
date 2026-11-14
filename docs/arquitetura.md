# Arquitetura

O modelo decide na hora; a IA audita em paralelo; o associado é avisado e responde; o analista
decide no fim (ADR-011, ADR-012 e ADR-015). Tudo roda na máquina de quem usa, com dados
sintéticos. Só duas coisas saem para o IBM watsonx.ai, sempre sem identificadores: a auditoria da
decisão e a redação da mensagem ao associado.

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

    WX["IBM watsonx.ai<br/><small>Granite (ibm/granite-4-h-small)</small>"]

    ANA -->|"localhost:3000"| SITE
    ASS -->|"localhost:3000/associado"| SITE
    AUT -->|"POST /api/analisar"| API
    SITE -->|"HTTP localhost:8000"| API
    API --> NUC
    API -->|"em paralelo"| AUD
    API --> CAN
    AUD -->|"audita com ferramentas, sem identificadores"| WX
    CAN -->|"redige a mensagem, em segundo plano"| WX
    NUC --> ARQ
    API --> ARQ
```

| Pasta | Responsabilidade |
| --- | --- |
| `src/` (raiz) | Dados, modelo, agente, fila e respostas do analista |
| `src/api/` | Rotas (`app.py`), esquemas, serviços, auditorias e respostas |
| `src/auditoria/` | Ferramentas, cliente do watsonx.ai, modo local, relatório e parecer |
| `src/associado/` | Notificações ao associado e mensagem redigida pelo Granite, com as regras contra golpe |
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
    A->>S: criar notificação (mensagem do modelo fixo)
    A-->>C: decisão + id_auditoria + id_notificacao
    A->>T: auditar(transação, análise)
    T->>W: chat com ferramentas
    W-->>T: relatório
    T-->>A: CONFIRMA / DIVERGE / INCONCLUSIVO
    S->>W: redigir a mensagem (segundo plano)
    W-->>S: texto do Granite
    Note over S: o texto só substitui o modelo fixo se passar nas regras contra golpe
    P->>A: "Não fui eu" (App do associado)
    A->>S: status negada → compra bloqueada, caso para o analista
    AN->>A: abre o caso: decisão, parecer da IA e resposta do associado
    AN->>A: Confirmar fraude
```

Passo a passo:

1. A API recebe a compra, calcula os 9 sinais e a nota, e decide na hora: aprovar, pedir
   confirmação ou bloquear.
2. Se a compra é suspeita, o canal do associado cria o aviso com a mensagem do modelo fixo. A
   decisão já volta a quem chamou, sem esperar a IA.
3. Em paralelo, a auditoria pede ao watsonx.ai que confira a decisão com 5 ferramentas. O parecer
   é CONFIRMA, DIVERGE ou INCONCLUSIVO e nunca muda a decisão.
4. Também em segundo plano, o Granite redige uma mensagem melhor para o associado. Ela só é usada
   se passar nas regras contra golpe: começa com "Sicredi:", tem até 160 caracteres, não tem
   link, nunca pede senha ou código e cita só o valor, a data e a hora reais da compra. Senão,
   vale o modelo fixo.
5. O associado responde "Fui eu" ou "Não fui eu" no App do associado. "Não fui eu" bloqueia a
   compra e leva o caso ao analista.
6. O analista abre o caso no painel, vê a decisão, o parecer da IA e a resposta do associado, e
   confirma ou descarta a fraude.

A auditoria e a notificação nunca atrasam a decisão. Sem credenciais do watsonx.ai, a auditoria
e a mensagem usam o modo local (regra dos sinais e modelo fixo) e o resto funciona igual.
