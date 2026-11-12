# 06 — Diagramas de sequência

Só os fluxos que acionam os gatilhos do Manual (2.4.5): integração externa (Ollama) e operação
que o usuário pode repetir (clique duplo no botão de resposta).

## Analisar e explicar uma transação (US006, cenários 6 a 9)

```mermaid
sequenceDiagram
    actor A as Analista
    participant P as pagina_fila
    participant S as st.session_state
    participant G as AgenteSentinela
    participant O as Ollama

    A->>P: Escolher transação: clique na tabela
    P->>S: Buscar análise em cache: analises[(id, usar_llm)]
    alt análise já existe
        S-->>P: Retornar análise guardada: dict
    else análise não existe
        P->>G: Analisar transação: analisar(transacao, usar_llm)
        G->>G: Calcular sinais, nota e decisão: calcular_sinais, pontuar, decidir
        alt usar_llm ligado
            G->>O: Verificar disponibilidade: GET /api/tags (2 s)
            alt Ollama responde 200
                O-->>G: Retornar modelos instalados: JSON
                G->>O: Pedir explicação: POST /api/generate (até 60 s)
                alt resposta válida e não vazia
                    O-->>G: Retornar texto: str
                else erro, JSON inválido ou texto vazio
                    G->>G: Montar texto de reserva e registrar log: explicar
                end
            else falha de conexão ou tempo esgotado
                G->>G: Montar texto de reserva e registrar log: explicar
            end
        else usar_llm desligado
            G->>G: Montar texto de reserva: explicar
        end
        G-->>P: Retornar análise: dict com nota, sinais, decisão e explicação
        P->>S: Guardar análise: analises[(id, usar_llm)]
    end
    P-->>A: Mostrar painel com legenda da fonte
```

## Decisão imediata e auditoria em paralelo (Issue #38)

```mermaid
sequenceDiagram
    actor C as Autorizador / Site
    participant A as API (src/api/app.py)
    participant S as servicos.py
    participant N as Núcleo (agente.py)
    participant T as Thread (auditorias.py)
    participant AI as src/auditoria

    C->>A: POST /api/analisar {transacao, auditar:true}
    A->>S: analisar_transacao(transacao_dict)
    S->>N: calcular_sinais + pontuar + decidir
    N-->>S: nota, sinais, decisao
    S->>S: explicar(usar_llm=False) — texto de reserva
    S-->>A: dict Analise + latencia_ms
    A->>T: registrar "pendente" + disparar thread
    A-->>C: 200 {analise, id_auditoria} — resposta imediata

    Note over T,AI: Em segundo plano (thread daemon)
    T->>AI: auditar(transacao, analise)
    alt src/auditoria existe (#39)
        AI-->>T: Relatorio
        T->>T: registrar "concluida" em memória
    else src/auditoria não existe ainda
        T->>T: registrar "erro" em memória
    end

    C->>A: GET /api/auditorias/{id}
    A-->>C: Auditoria {status, relatorio, ...}
```

## Registrar a resposta do analista (US007)

O clique pode se repetir (duplo clique, ou o analista muda de ideia). Cada clique acrescenta
uma linha; a leitura usa sempre a última linha da transação, então repetir não muda o resultado.

```mermaid
sequenceDiagram
    actor A as Analista
    participant P as pagina_fila
    participant F as feedback
    participant C as data/feedback.csv

    A->>P: Clicar em Confirmar fraude
    P->>F: Registrar resposta: registrar_resposta(caminho, RespostaAnalista)
    F->>F: Validar resposta em fraude ou legitima: registrar_resposta
    alt resposta inválida
        F-->>P: Lançar erro: ValueError
    else resposta válida
        F->>C: Acrescentar linha, com cabeçalho se o arquivo não existir
        alt gravação ok
            C-->>F: Confirmar gravação: None
            F-->>P: Retornar sucesso: None
            P-->>A: Mostrar aviso Resposta registrada
        else arquivo bloqueado ou sem permissão
            C-->>F: Lançar erro: PermissionError
            F-->>P: Relançar erro: OSError
            P-->>A: Mostrar Não foi possível salvar a resposta
        end
    end
    P->>F: Ler última resposta: ler_ultima_resposta(caminho, id_transacao)
    F-->>P: Retornar resposta atual: RespostaAnalista ou None
    P-->>A: Mostrar Sua resposta
```
