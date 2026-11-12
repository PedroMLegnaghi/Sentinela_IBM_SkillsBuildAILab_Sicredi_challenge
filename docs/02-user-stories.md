# 02 — User Stories

Cada história liga a um requisito de [01-requisitos.md](01-requisitos.md). Os critérios em BDD
são a definição de pronto usada por quem implementa e por quem revisa. Textos entre aspas são
exatamente os de `src/interface/textos.py` (ver [08-design-da-interface.md](08-design-da-interface.md)).

Ator principal: **analista de prevenção a fraudes** da cooperativa, numa estação de trabalho
com tela grande, revisando dezenas de alertas por turno. Ator secundário: **avaliador** do
desafio, que assiste ao vídeo e abre o repositório.

## Histórias das Etapas 1 a 3 (implementadas, corrigidas na Issue #2)

- **US001 · RF001 · Preparar os dados.** Como equipe de dados, quero as transações num formato
  limpo e sem colunas que vazam a resposta, para treinar um modelo honesto. Critérios: seção 11
  da ESPECIFICACAO, Etapa 1.
- **US002 · RF002 · Treinar o modelo.** Como equipe de dados, quero um modelo validado no tempo,
  para saber como ele se comportaria em produção. Critérios: ESPECIFICACAO, seção 11, Etapa 2.
- **US003 · RF003, RF004 · Sinais e decisão.** Como analista, quero que cada transação venha com
  sinais e uma decisão, para não começar a investigação do zero. Critérios: ESPECIFICACAO,
  seções 8.2, 8.3 e 9.
- **US004 · RF005 · Explicação.** Como analista, quero a decisão explicada em português, para
  entender o motivo sem ler números. Critérios: ESPECIFICACAO, seção 8.5.

## US005 · RF006 · Fila de alertas priorizada

Como analista de prevenção a fraudes,
eu quero ver as transações ordenadas da mais arriscada para a menos arriscada,
para que eu revise primeiro o que pode causar mais prejuízo.

**Cenário 1 — Fila carregada.** Dado que os dados preparados e o modelo existem, quando abro a
página "Fila de alertas", então vejo quatro indicadores ("Na fila", "Bloquear", "Pedir
confirmação", "Aprovar") que somam 2.054, e uma tabela ordenada pela nota, da maior para a menor,
com a decisão escrita por extenso e com ícone.

**Cenário 2 — Filtro padrão.** Dado que a fila carregou, quando olho a tabela pela primeira vez,
então só aparecem as decisões "Bloquear" e "Pedir confirmação", e o texto "Mostrando N de 2.054
transações." mostra quantas linhas estão visíveis.

**Cenário 3 — Filtro alterado.** Dado que a fila carregou, quando marco também "Aprovar", então a
tabela passa a mostrar as 2.054 transações e os quatro indicadores não mudam.

**Cenário 4 — Filtro vazio.** Dado que a fila carregou, quando desmarco todas as decisões, então
não aparece tabela nem painel, e aparece a mensagem "Nenhuma transação com os filtros escolhidos.
Marque ao menos uma decisão em “Mostrar decisões”."

**Cenário 5 — Carregamento.** Dado que abro o app pela primeira vez na sessão, quando a fila
ainda está sendo montada, então vejo o indicador de progresso com "Carregando e analisando as
transações de março…"; nas interações seguintes a fila não é recalculada.

**Cenário 6 — Dados ausentes.** Dado que `data/transacoes_preparadas.parquet` não existe, quando
abro o app, então vejo só a mensagem de erro com o comando `python -m src.preparar_dados`, e nada
mais é carregado. O mesmo vale para o modelo ausente, com o comando `python -m src.treinar_modelo`.

## US006 · RF007 · Painel de análise da transação

Como analista de prevenção a fraudes,
eu quero ver decisão, nota, sinais, explicação e histórico do cartão num só painel,
para que eu decida em segundos sem consultar outro sistema.

**Cenário 1 — Seleção pela tabela.** Dado que a fila está visível, quando clico numa linha da
tabela, então o painel à direita mostra a análise daquela transação.

**Cenário 2 — Seleção pelo teclado.** Dado que a fila está visível, quando escolho um ID na caixa
"Ou escolha pelo ID da transação", então o painel mostra aquela transação.

**Cenário 3 — Nenhuma linha clicada.** Dado que acabei de abrir a página ou mudei o filtro,
quando ainda não escolhi nenhuma transação, então o painel mostra a primeira linha visível, a de
maior nota.

**Cenário 4 — Decisão e nota.** Dado uma transação no painel, então vejo a decisão numa faixa com
cor, ícone e texto ("Bloquear e enviar ao analista", "Pedir confirmação ao cliente" ou
"Aprovar"), e a nota numa barra com o texto "Nota de risco: 97,3 de 100".

**Cenário 5 — Sinais.** Dado uma transação com sinais, então vejo "Sinais de alerta (N)" e uma
linha por sinal com a descrição do agente. Dado uma transação sem sinais, então vejo "Nenhum sinal
de alerta: a transação segue o padrão das compras legítimas."

**Cenário 6 — Explicação com IBM Granite.** Dado que "Explicar com IBM Granite" está ligado e o
Ollama responde, quando abro uma transação, então vejo o indicador de progresso "O IBM Granite
está escrevendo a explicação… A primeira pode levar até 1 minuto." e depois o texto, com a
legenda "Explicação gerada por: IBM Granite 4".

**Cenário 7 — Granite indisponível.** Dado que "Explicar com IBM Granite" está ligado e o Ollama
não responde, quando abro uma transação, então vejo a explicação por regras com a legenda
"Explicação gerada por: regras (IBM Granite indisponível no momento)", sem mensagem de erro técnica.

**Cenário 8 — Granite desligado.** Dado que "Explicar com IBM Granite" está desligado, quando
abro uma transação, então vejo a explicação por regras com a legenda "Explicação gerada por: regras".

**Cenário 9 — Explicação não é refeita.** Dado que a explicação de uma transação já foi gerada,
quando clico num botão de resposta ou volto a essa transação, então o Granite não é chamado de
novo nesta sessão.

**Cenário 10 — Histórico.** Dado uma transação com cartão identificado, quando abro "Histórico do
cartão", então vejo até 10 transações anteriores desse cartão, da mais recente para a mais
antiga. Sem transações anteriores: "Nenhuma transação anterior deste cartão na base." Sem
identificação de cartão: "Esta transação não tem identificação de cartão; o histórico não está
disponível."

**Cenário 11 — Rótulo real escondido.** Dado qualquer transação, então as colunas `fraude` e
`decisao_sistema_atual` não aparecem em lugar nenhum da página.

## US007 · RF008 · Resposta do analista

Como analista de prevenção a fraudes,
eu quero registrar se a transação era fraude ou legítima,
para que o modelo possa ser retreinado no futuro com casos confirmados.

**Cenário 1 — Registrar.** Dado uma transação no painel, quando clico em "Confirmar fraude",
então uma linha é acrescentada em `data/feedback.csv`, aparece o aviso "Resposta registrada:
fraude confirmada." e o painel mostra "Sua resposta: Fraude confirmada em DD/MM/AAAA HH:MM.
Você pode mudar; vale a última." O mesmo vale para "Marcar como legítima", com "Transação legítima".

**Cenário 2 — Mudar de ideia.** Dado que já respondi uma transação, quando clico no outro botão,
então uma nova linha é acrescentada e o painel passa a mostrar a nova resposta. Clicar duas vezes
no mesmo botão acrescenta duas linhas iguais e não muda o resultado (vale a última).

**Cenário 3 — Resposta lembrada.** Dado que respondi uma transação e recarreguei a página, quando
volto a ela, então o painel mostra a última resposta gravada no arquivo.

**Cenário 4 — Sem resposta.** Dado uma transação nunca respondida, então o painel mostra "Ainda
sem resposta para esta transação."

**Cenário 5 — Falha ao gravar.** Dado que o arquivo não pode ser gravado (por exemplo, aberto no
Excel no Windows), quando clico num botão, então vejo "Não foi possível salvar a resposta em
data/feedback.csv. Feche o arquivo se ele estiver aberto em outro programa e tente de novo." e
nenhuma resposta é dada como registrada.

**Cenário 6 — Valor inválido.** Dado o módulo de respostas, quando alguém tenta gravar uma
resposta diferente de "fraude" ou "legitima", então a gravação é recusada com `ValueError`
(teste automatizado).

## US008 · RF009 · Desempenho comparado

Como avaliador do desafio,
eu quero comparar o Sentinela com o sistema atual em março,
para saber se a solução bloqueia mais fraudes sem bloquear clientes legítimos.

**Cenário 1 — Indicadores.** Dado que `modelos/avaliacao_agente.json` existe, quando abro
"Desempenho", então vejo: "Fraudes em março", "Bloqueadas pelo Sentinela" (com a diferença em
relação ao sistema atual), "Bloqueadas pelo sistema atual", "Compras legítimas bloqueadas" e
"Pedidos de confirmação", com os números do arquivo.

**Cenário 2 — Gráfico e tabela.** Então vejo o gráfico de barras "Fraudes de março bloqueadas"
com as duas barras e uma tabela com os mesmos números, para quem não enxerga cores.

**Cenário 3 — Detalhes do modelo.** Quando abro "Detalhes do modelo (regressão logística)", então
vejo PR-AUC, ROC-AUC e a tabela das notas de corte de `modelos/metricas.json`.

**Cenário 4 — Aviso.** Então vejo o aviso "Dados sintéticos: o resultado é otimista. Em produção,
o modelo precisaria de monitoramento e retreino com as respostas dos analistas."

**Cenário 5 — Métricas ausentes.** Dado que um dos arquivos JSON não existe, quando abro
"Desempenho", então vejo só o erro com os comandos que faltam rodar.

## US009 · RF010 · Como o Sentinela decide

Como avaliador do desafio,
eu quero ver como o Sentinela decide e quais são seus limites,
para confiar na decisão e entender o que ainda não está pronto.

**Cenário 1 — Passos.** Quando abro "Como funciona", então vejo os passos do agente (sinais,
nota, decisão, explicação, revisão humana) e a frase de que a IA explica, mas quem decide são
regras e um modelo auditáveis.

**Cenário 2 — Sinais.** Então vejo a tabela "Os 9 sinais de alerta" com os limiares lidos de
`src/config.py`; se uma constante mudar, a tabela muda junto.

**Cenário 3 — Dados.** Então vejo quantas transações e quantas fraudes a base tem, calculados na
hora a partir dos dados preparados, e como a fila de demonstração foi montada.

**Cenário 4 — Limitações.** Então vejo a lista de limitações da seção correspondente do design.
