# 01 — Matriz de Requisitos

O Sentinela entrega um agente que analisa, decide e explica cada transação de cartão, e uma
interface em que o analista revisa e responde. Prioridades no método MoSCoW.

## Requisitos funcionais

| ID | Módulo | Descrição | Prioridade | Fase | História |
| --- | --- | --- | --- | --- | --- |
| RF001 | Dados | Preparar as 160 mil transações da Sicredi em formato analítico, sem colunas que vazam a resposta | Must | Etapa 1 (a corrigir na #2) | US001 |
| RF002 | Modelo | Treinar e avaliar um modelo de risco com validação temporal | Must | Etapa 2 (a corrigir na #2) | US002 |
| RF003 | Agente | Calcular sinais de alerta explicáveis para cada transação | Must | Etapa 3 (a corrigir na #2) | US003 |
| RF004 | Agente | Decidir entre aprovar, pedir confirmação ao cliente e bloquear | Must | Etapa 3 (a corrigir na #2) | US003 |
| RF005 | Agente | Explicar a decisão em português com IBM Granite, com texto de reserva por regras | Must | Etapa 3 (a corrigir na #2) | US004 |
| RF006 | Interface | Exibir a fila de transações priorizada pela nota de risco | Must | Issues #3 e #4 | US005 |
| RF007 | Interface | Exibir a análise completa de uma transação: decisão, nota, sinais, explicação e histórico do cartão | Must | Issue #4 | US006 |
| RF008 | Interface | Registrar a resposta do analista (fraude ou legítima) para retreino futuro | Must | Issues #3 e #4 | US007 |
| RF009 | Interface | Comparar o desempenho do Sentinela com o sistema atual | Should | Issue #5 | US008 |
| RF010 | Interface | Explicar como o Sentinela decide, com regras, dados e limitações | Could | Issue #5 | US009 |
| RF011 | Interface | Ajustar os limiares de decisão pela tela | Won't | Fora do escopo | — |
| RF012 | Modelo | Retreinar o modelo automaticamente com as respostas do analista | Won't | Fora do escopo | — |
| RF013 | Integração | Receber transações do autorizador de cartões por uma API e decidir na hora | Must | Issue #38 (API; autorizador simulado) | — |
| RF014 | Integração | Enviar a confirmação ao cliente por notificação no app ou SMS | Won't | Fora do escopo | — |
| RF015 | Acesso | Login e perfis de analista | Won't | Fora do escopo | — |
| RF016 | Implantação | Publicar o sistema num servidor | Won't | Fora do escopo | — |
| RF017 | Agente | Auditar cada decisão com um agente de IA no watsonx.ai, em paralelo e sem mudar a decisão | Must | Issue #39 | — |
| RF018 | Interface | Site web com fila, painel da transação, desempenho, como funciona, simulador e respostas | Must | Issues #40, #43, #44, #45 | US005 a US009 |
| RF019 | Interface | Mostrar ao analista o parecer da IA (confirma, diverge, inconclusivo) com evidências e ferramentas usadas | Must | Issue #43 | — |
| RF020 | Modelo | Mostrar o que pesou na nota de cada transação | Should | Issue #41 | — |
| RF021 | Modelo | Avaliar o modelo com janelas temporais, bootstrap, ablação, calibração e custo da fraude | Should | Issue #42 | — |
| RF022 | Modelo | Comparar a IA com o modelo em latência e concordância | Should | Issue #46 | — |
| RF023 | Dados | Documentar a análise exploratória e a qualidade dos dados | Should | Issue #47 | — |
| RF024 | Interface | Simular a decisão alterando campos de uma transação | Could | Issue #45 | — |

**Por que os Won't ficaram de fora:** RF011 permitiria mudar decisões sem governança e sem
registro; RF012 exige validar o feedback antes de treinar; RF013 a RF016 dependem de sistemas
e credenciais que o desafio não fornece. A tela de "Pedir confirmação" apenas indica a ação; o
envio real ao cliente não existe (RF014). A partir de 12/11 (ADR-011 e ADR-012), RF013 vira
Must por meio da API, e o Streamlit (RF006 a RF010) fica como reserva do site (RF018).

## Requisitos não funcionais

| ID | Requisito | Como é verificado |
| --- | --- | --- |
| RNF01 | Qualidade de código conforme o Manual da IDE (capítulo 2.5) | Black, Ruff e pytest passam no CI de todo Pull Request |
| RNF02 | Rastreabilidade: toda Issue liga a um requisito e muda os diagramas afetados | Revisão do Pull Request |
| RNF03 | Acessibilidade WCAG 2.2 AA nos itens do checklist do capítulo 2.3.11 | Auditoria da Issue #6 (Lighthouse e checklist) |
| RNF04 | Privacidade: nenhuma coluna pessoal lida, nenhum dado no repositório ou em log | Revisão e `git ls-files` |
| RNF05 | Reprodutibilidade: semente 42, versões fixadas, mesmos números em qualquer máquina | Invariantes da ESPECIFICACAO, seção 11 |
| RNF06 | Entrega no portal do desafio: vídeo de até 3 min, dois textos de até 500 palavras e repositório | Checklist da Issue #8 |
