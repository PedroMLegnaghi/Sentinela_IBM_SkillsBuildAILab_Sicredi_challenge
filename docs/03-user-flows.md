# 03 — User Flows

Um diagrama por jornada. Cada cenário das histórias US005 a US007 tem um caminho aqui; os
caminhos de erro estão desenhados, não subentendidos.

## Jornada 1 — Abrir o Sentinela (US005, cenários 1, 5 e 6)

```mermaid
graph TD
    Inicio([Analista roda streamlit run app.py]) --> Dados{Dados preparados existem?}
    Dados -- Não --> ErroDados[Mostra erro com o comando python -m src.preparar_dados]
    ErroDados --> FimErro([Analista roda o comando e reabre o app])
    Dados -- Sim --> Modelo{Modelo existe?}
    Modelo -- Não --> ErroModelo[Mostra erro com o comando python -m src.treinar_modelo]
    ErroModelo --> FimErro
    Modelo -- Sim --> Carrega[Mostra Carregando e analisando as transações de março]
    Carrega --> Fila[Fila de alertas com indicadores, tabela e painel]
    Fila --> Fim([Analista começa a revisar])
```

## Jornada 2 — Revisar um alerta (US005 cenários 2 a 4, US006, US007)

```mermaid
graph TD
    Inicio([Analista está na Fila de alertas]) --> Filtro{Alguma decisão marcada no filtro?}
    Filtro -- Não --> Vazio[Mostra Nenhuma transação com os filtros escolhidos]
    Vazio --> Filtro
    Filtro -- Sim --> Tabela[Tabela ordenada pela nota]
    Tabela --> Escolha{Analista escolheu uma linha?}
    Escolha -- Não --> Primeira[Painel mostra a primeira linha visível]
    Escolha -- Pela tabela ou pelo ID --> Escolhida[Painel mostra a transação escolhida]
    Primeira --> Painel[Decisão, nota e sinais]
    Escolhida --> Painel
    Painel --> Cache{Explicação já gerada nesta sessão?}
    Cache -- Sim --> Explicacao[Mostra explicação e legenda da fonte]
    Cache -- Não --> Toggle{Explicar com IBM Granite ligado?}
    Toggle -- Não --> Regras[Explicação por regras]
    Toggle -- Sim --> Granite{Ollama responde?}
    Granite -- Sim --> TextoGranite[Explicação do IBM Granite]
    Granite -- Não --> RegrasIndisp[Explicação por regras, Granite indisponível]
    Regras --> Explicacao
    TextoGranite --> Explicacao
    RegrasIndisp --> Explicacao
    Explicacao --> Resposta{Analista clica em um botão de resposta?}
    Resposta -- Não --> Tabela
    Resposta -- Sim --> Grava{Gravou em data/feedback.csv?}
    Grava -- Sim --> Registrada[Aviso Resposta registrada e painel mostra a resposta atual]
    Grava -- Não --> ErroGravar[Mostra Não foi possível salvar a resposta]
    ErroGravar --> Resposta
    Registrada --> Proxima{Revisar outra transação?}
    Proxima -- Sim --> Tabela
    Proxima -- Não --> Fim([Fim do turno])
```
