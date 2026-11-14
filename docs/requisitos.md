# Requisitos

O desafio Sicredi pergunta: como usar IA agêntica para **prever e intervir** em fraudes em compras
com cartão, aumentando a segurança do associado e reduzindo perdas. Esta tabela liga cada pedido do
desafio ao que o Sentinela entrega.

## O que o desafio pede

| Pedido do desafio | Como o Sentinela atende | Onde | Estado |
| --- | --- | --- | --- |
| Prever a fraude antes de concluir a compra | 9 sinais + regressão logística; decisão em cerca de 1,5 ms pela API | `src/agente.py`, `POST /api/analisar` | ✅ |
| Detectar comportamento atípico do associado | Perfil do associado (valor, horário, compras online) comparado à compra atual | `perfil_associado` na API e no painel | ✅ |
| Alerta preventivo ao associado | Aviso e pedido de confirmação ao associado, com resposta "Fui eu" ou "Não fui eu" | `src/associado/`, App do associado (`/associado`) | ✅ |
| Mensagem clara e segura ao associado | O Granite redige o aviso; ele só é usado se passar nas regras contra golpe, senão vale um modelo fixo | `src/associado/`, `docs/privacidade.md` | ✅ |
| Intervenção (IA agêntica) | O agente decide, avisa o associado e uma IA no watsonx.ai audita a decisão com 5 ferramentas | API, `src/auditoria/` | ✅ |
| Análise explicável de risco | Sinais, explicação, o que pesou na nota e parecer da IA com evidências | painel da Fila | ✅ |
| Apoio à investigação | Fila priorizada, histórico, auditoria, respostas do analista, simulador | site | ✅ |
| Comparar a IA com o modelo | 254 compras de março (as 54 fraudes e 200 legítimas): recall de 100% nos dois; precisão de 96,4% no modelo e 44,3% na IA; 56 alertas contra 122; 5 ms contra 6,1 s por compra. Por isso o modelo decide e a IA audita (ADR-012) | `modelos/ia_contra_modelo.json`, README | ✅ |
| Reduzir perdas financeiras | 54 de 54 fraudes bloqueadas contra 26 do sistema atual; prejuízo evitado de R$ 6.495,16 (já descontado R$ 1,00 por confirmação) | Desempenho, `docs/avaliacao.md`, `modelos/custos.json` | ✅ |
| Rigor da avaliação | Validação temporal em duas janelas, bootstrap, ablação, comparação com regras e calibração | `docs/avaliacao.md`, `modelos/avaliacao_rigorosa.json` | ✅ |
| Entender os dados | 160.000 compras e 146 fraudes; todas de madrugada (0h a 4h) | `docs/analise-exploratoria.md`, `modelos/eda.json` | ✅ |
| Experiência do associado | 0 compras legítimas bloqueadas; 159 pedidos de confirmação (1,2%) | Desempenho, Como funciona, `modelos/avaliacao_agente.json` | ✅ |
| Transparência | Como funciona, explicações, fonte de cada parecer | site | ✅ |
| Privacidade | Só 16 colunas, nada que identifique a pessoa vai para a IA, dados fora do Git | ESPECIFICACAO, seções 4, 5 e 13; `docs/privacidade.md` | ✅ |

Os dados são sintéticos e muito separáveis; com dados reais, os números seriam menores e o modelo
precisaria de monitoramento e retreino.

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
