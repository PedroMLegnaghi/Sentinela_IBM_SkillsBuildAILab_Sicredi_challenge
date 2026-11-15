# Arquitetura

O modelo decide na hora; a IA audita em paralelo; o associado é avisado e responde; a filial
acompanha (ADR-011, ADR-012 e ADR-015). O site tem duas áreas: a do associado e a da filial
(auditor e gerente), cada uma vendo só o que pode (ESPECIFICACAO, seção 17). Tudo roda na máquina de quem usa, com dados
sintéticos; só a auditoria sai para o IBM watsonx.ai, sem identificadores.

## Contêineres

```mermaid
graph TB
    FIL["Auditor e gerente<br/><small>área da filial</small>"]
    ASS["Associado<br/><small>área do associado, simulada</small>"]
    AUT["Autorizador de cartões<br/><small>simulado pela API</small>"]

    subgraph Sentinela["Sentinela"]
        SITE["<b>Site</b> · Next.js + Carbon · web/<br/><small>/associado: início, extrato, compra, avisos, chat<br/>/filial: fila, painel do gerente, desempenho</small>"]
        API["<b>API</b> · FastAPI · src/api/<br/><small>decisão imediata, sessão, rotas do associado<br/>e da filial, auditoria, notificações</small>"]
        APL["<b>Aplicação e domínio</b> · src/aplicacao/, src/dominio/<br/><small>casos de uso e regras puras</small>"]
        POR["<b>Portas</b> · src/portas/<br/><small>interfaces dos repositórios</small>"]
        MEM["<b>Adaptador em memória</b> · src/adaptadores/memoria/<br/><small>escolhido só em src/composicao.py</small>"]
        NUC["<b>Núcleo</b> · src/agente.py, explicabilidade.py<br/><small>sinais, nota, decisão, contribuições</small>"]
        AUD["<b>Auditoria</b> · src/auditoria/<br/><small>5 ferramentas, modo local</small>"]
        CAN["<b>Canal do associado</b> · src/associado/<br/><small>mensagem e respostas</small>"]
        ARQ[("data/ · modelos/")]
    end

    WX["IBM watsonx.ai<br/><small>Granite com ferramentas</small>"]

    FIL -->|"localhost:3000/filial"| SITE
    ASS -->|"localhost:3000/associado"| SITE
    AUT -->|"POST /api/analisar"| API
    SITE -->|"HTTP localhost:8000"| API
    API --> NUC
    API -->|"em paralelo"| AUD
    API --> CAN
    API --> APL
    APL --> POR
    MEM -.->|"implementa"| POR
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
| `src/dominio/`, `src/aplicacao/` | Entidades, regras puras e casos de uso do associado e da filial |
| `src/portas/`, `src/adaptadores/` | Interfaces dos repositórios e o adaptador em memória; `src/composicao.py` liga os dois |
| `web/app/` | Uma pasta por página: `associado/`, `filial/` e `entrar/` |
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
    actor AN as Auditor da filial

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
    A->>S: status negada → compra bloqueada, caso na fila da filial
    AN->>A: abre o caso na fila da agência: decisão, parecer da IA e resposta do associado
```

A auditoria e a notificação nunca atrasam a decisão. Sem credenciais do watsonx.ai, a auditoria
e a mensagem usam o modo local e o resto funciona igual.
