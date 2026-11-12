# 04 — Arquitetura (C4)

O Sentinela roda inteiro na máquina de quem o usa: uma interface Streamlit, um núcleo de agente
em Python, scripts de preparação e treino, arquivos locais e o IBM Granite servido pelo Ollama.
Nada é hospedado (ADR-002).

## Nível 1 — Contexto

```mermaid
graph TB
    subgraph Atores
        ANA["Analista de prevenção a fraudes<br/>revisa alertas e responde"]
        AVA["Avaliador do desafio<br/>assiste ao vídeo e lê o repositório"]
    end

    SYS["<b>Sentinela</b><br/>agente antifraude: sinais, nota,<br/>decisão, explicação e revisão humana"]

    subgraph Externos["Sistemas e arquivos externos"]
        CSV["Base sintética da Sicredi<br/>CSV com 160 mil transações"]
        OLL["Ollama com IBM Granite 4<br/>roda no computador do analista"]
    end

    AUT["Autorizador de cartões da Sicredi<br/>FORA DO ESCOPO: sem integração em tempo real"]
    NOT["Notificação ao cliente por app ou SMS<br/>FORA DO ESCOPO: confirmação apenas indicada"]
    ORC["IBM watsonx Orchestrate e IBM Cloud<br/>FORA DO ESCOPO: não usados"]

    ANA --> SYS
    AVA --> SYS
    SYS -->|"lê 16 colunas"| CSV
    SYS -->|"pede explicação"| OLL
    SYS -.->|"não integrado"| AUT
    SYS -.->|"não integrado"| NOT
    SYS -.->|"não usado"| ORC
```

## Nível 2 — Contêineres

```mermaid
graph TB
    ANA["Analista"]

    subgraph Sentinela["Sentinela (máquina local)"]
        UI["<b>Interface</b><br/>Streamlit · app.py e src/interface<br/><small>fila, painel, desempenho</small>"]
        NUC["<b>Núcleo do agente</b><br/>Python · src/agente.py e src/config.py<br/><small>sinais, nota, decisão, explicação</small>"]
        SCR["<b>Scripts de lote</b><br/>Python · preparar_dados, treinar_modelo, avaliar_agente"]
        ARQ[("<b>Arquivos locais</b><br/>data/: CSV, parquet, feedback.csv<br/>modelos/: joblib e JSON")]
    end

    CSV["CSV da Sicredi"]
    OLL["Ollama · granite4:micro"]

    ANA -->|"navegador · localhost:8501"| UI
    UI -->|"chamada de função Python"| NUC
    UI -->|"lê parquet e JSON · grava feedback.csv"| ARQ
    NUC -->|"lê sentinela.joblib"| ARQ
    NUC -->|"HTTP · localhost:11434 · /api/tags e /api/generate"| OLL
    SCR -->|"lê 16 colunas"| CSV
    SCR -->|"grava parquet, joblib e JSON"| ARQ
```

## Nível 3 — Componentes do núcleo do agente

O núcleo concentra a regra de negócio: se ele errar, o produto inteiro erra.

```mermaid
graph TB
    UI["Interface e scripts"]

    subgraph Nucleo["src/agente.py"]
        AG["AgenteSentinela<br/><small>orquestra: analisar e analisar_lote</small>"]
        SIN["calcular_sinais<br/><small>9 regras com limiares de config</small>"]
        PON["pontuar<br/><small>regressão logística, nota de 0 a 100</small>"]
        DEC["decidir<br/><small>APROVAR, PEDIR_CONFIRMACAO ou BLOQUEAR</small>"]
        HIS["historico_cartao<br/><small>últimas transações do cartão</small>"]
        EXP["explicar<br/><small>Granite ou texto de reserva</small>"]
        DIS["granite_disponivel<br/><small>isola o Ollama: GET /api/tags</small>"]
    end

    CFG["src/config.py<br/><small>limiares, caminhos, URLs</small>"]
    MOD[("modelos/sentinela.joblib")]
    OLL["Ollama"]

    UI --> AG
    AG --> SIN
    AG --> PON
    AG --> DEC
    AG --> HIS
    AG --> EXP
    EXP --> DIS
    DIS -->|"HTTP"| OLL
    EXP -->|"HTTP · POST /api/generate"| OLL
    SIN --> CFG
    DEC --> CFG
    PON --> MOD
```

Regra de manutenção: um Pull Request que muda assinatura pública do agente, cria módulo ou
adiciona dependência externa atualiza este arquivo no mesmo Pull Request.

## Módulos de incremento (Issues #19–#31)

Módulos esqueleto criados na Issue #19; cada Issue subsequente implementa o seu.

| Módulo | Página / painel | Issue |
| --- | --- | --- |
| `src/interface/secao_confiabilidade.py` · `renderizar()` | Desempenho | #28 |
| `src/interface/secao_custos.py` · `renderizar()` | Desempenho | #20 |
| `src/interface/secao_cenario_dificil.py` · `renderizar()` | Desempenho | #29 |
| `src/interface/secao_latencia.py` · `renderizar()` | Desempenho | #27 |
| `src/interface/secao_importancia.py` · `renderizar()` | Como funciona | #21 |
| `src/interface/secao_dados.py` · `renderizar()` | Como funciona | #31 |
| `src/interface/painel_contribuicoes.py` · `renderizar(transacao)` | Fila — painel | #21 |
| `src/interface/painel_mensagem.py` · `renderizar(transacao, analise)` | Fila — painel | #23 |
| `src/interface/pagina_simulador.py` · `renderizar()` | Página Simulador | #22 |
| `src/interface/pagina_respostas.py` · `renderizar()` | Página Respostas do analista | #25 |


## Arquitetura web (ADR-011 e ADR-012, Issue #37)

A partir da Issue #37, o Streamlit fica como reserva e a aplicação passa a ter três contêineres
além do núcleo. A Issue #38 detalha os diagramas.

| Contêiner | Tecnologia | Responsabilidade |
| --- | --- | --- |
| Site | Next.js, TypeScript, Carbon (`web/`) | Telas do analista; fala só com a API |
| API | FastAPI (`src/api/`) | Contrato da ESPECIFICACAO, seção 12; decisão imediata; dispara a auditoria |
| Núcleo | Python (`src/agente.py`, `src/explicabilidade.py`) | Sinais, nota, decisão, contribuições |
| Auditoria | `src/auditoria/` + IBM watsonx.ai (Granite com ferramentas) | Segunda opinião em paralelo; nunca muda a decisão |

Caminho de uma compra: autorizador ou site → `POST /api/analisar` → núcleo decide (milissegundos)
→ resposta imediata; em paralelo, a auditoria chama o watsonx.ai, que pede ferramentas do
Sentinela, e o relatório fica disponível em `GET /api/auditorias/{id}` (segundos).
