# Requisitos

O desafio Sicredi pergunta: como usar IA agêntica para **prever e intervir** em fraudes em compras
com cartão, aumentando a segurança do associado e reduzindo perdas. Esta tabela liga cada pedido do
desafio ao que o Sentinela entrega.

## O que o desafio pede

| Pedido do desafio | Como o Sentinela atende | Onde | Estado |
| --- | --- | --- | --- |
| Prever a fraude antes de concluir a compra | 9 sinais + regressão logística; decisão em cerca de 1,5 ms pela API | `src/agente.py`, `POST /api/analisar` | ✅ |
| Detectar comportamento atípico do associado | Perfil do associado (valor, horário, compras online) comparado à compra atual | `perfil_associado` na API e no painel | ⏳ #64 |
| Alerta preventivo ao associado | Aviso e pedido de confirmação ao associado, com resposta "sim" ou "não" | `src/associado/`, App do associado | ⏳ #62, #63, #65 |
| Intervenção (IA agêntica) | O agente decide, avisa o associado e uma IA no watsonx.ai audita a decisão com ferramentas | API, `src/auditoria/` | ✅ auditoria · ⏳ canal |
| Análise explicável de risco | Sinais, explicação, o que pesou na nota e parecer da IA com evidências | painel da Fila | ✅ · ⏳ #41 |
| Apoio à investigação | Fila priorizada, histórico, auditoria, respostas do analista, simulador | site | ✅ |
| Reduzir perdas financeiras | 54 de 54 fraudes bloqueadas contra 26 do sistema atual; prejuízo evitado em reais | Desempenho | ✅ · ⏳ #42 |
| Experiência do associado | 0 compras legítimas bloqueadas; 1,2% de pedidos de confirmação | Desempenho, Como funciona | ✅ · ⏳ #67 |
| Transparência | Como funciona, explicações, fonte de cada parecer | site | ✅ |
| Privacidade | Só 16 colunas, nada que identifique a pessoa vai para a IA, dados fora do Git | ESPECIFICACAO, seções 4, 5 e 13 | ✅ · ⏳ #67 |

## Requisitos não funcionais

| ID | Requisito | Como é verificado |
| --- | --- | --- |
| RNF01 | Qualidade de código | Black, Ruff, pytest, ESLint, TypeScript e Vitest no CI de todo PR |
| RNF02 | Contrato estável entre site e API | `tests/test_conformidade_api.py` |
| RNF03 | Acessibilidade WCAG 2.2 AA | Lighthouse ≥ 90 (Issue #48) |
| RNF04 | Privacidade | Nenhum dado pessoal lido; nenhum identificador em respostas, logs ou mensagens à IA |
| RNF05 | Reprodutibilidade | Semente 42, versões fixadas, invariantes da ESPECIFICACAO, seção 11 |
| RNF06 | Tempo de resposta | Decisão do modelo em milissegundos; IA fora do caminho crítico (ADR-012) |

## Fora do escopo

Integração real com o autorizador de cartões e com SMS ou push, login de analistas, publicação em
servidor e retreino automático com as respostas do analista. Dependem de sistemas, credenciais e
dados que o desafio não fornece.
