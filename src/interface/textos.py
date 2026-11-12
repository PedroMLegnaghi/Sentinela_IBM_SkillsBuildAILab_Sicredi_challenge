"""Todos os textos da interface do Sentinela.

Nenhum texto literal de tela aparece fora deste módulo.
Formate com str.format onde indicado.
"""

# Aplicação e barra lateral
TITULO_APP = "Sentinela"
ROTULO_TOGGLE_GRANITE = "Explicar com IBM Granite"
AJUDA_TOGGLE_GRANITE = (
    "Usa o modelo IBM Granite 4 rodando no seu computador pelo Ollama. "
    "Desligado, a explicação é montada a partir dos sinais de alerta."
)
STATUS_GRANITE_ON = "IBM Granite: conectado"
STATUS_GRANITE_OFF = "IBM Granite: indisponível. As explicações serão montadas a partir dos sinais."
STATUS_GRANITE_DESLIGADO = "IBM Granite: desligado nesta sessão."
RODAPE_DADOS = (
    "Sentinela · agente antifraude do Desafio Sicredi. Dados 100% sintéticos "
    "fornecidos pela Sicredi. Protótipo do IBM SkillsBuild AI Lab."
)

# Erros de inicialização
ERRO_SEM_DADOS = (
    "Dados preparados não encontrados. Coloque o arquivo da Sicredi em data/ "
    "e rode no terminal: python -m src.preparar_dados"
)
ERRO_SEM_MODELO = "Modelo não encontrado. Rode no terminal: python -m src.treinar_modelo"
ERRO_SEM_METRICAS = (
    "Métricas não encontradas. Rode no terminal: python -m src.treinar_modelo "
    "e depois python -m src.avaliar_agente"
)

# Página Fila de alertas
TITULO_FILA = "Fila de alertas"
LEGENDA_FILA = (
    "Transações de março de 2025, da mais arriscada para a menos arriscada. "
    "Clique numa linha para analisar."
)
CARREGANDO_FILA = "Carregando e analisando as transações de março…"
METRICA_NA_FILA = "Na fila"
AJUDA_NA_FILA = (
    "Todas as fraudes de março mais 2.000 compras legítimas sorteadas, para demonstração."
)
FILTRO_DECISOES = "Mostrar decisões"
CONTAGEM_TABELA = "Mostrando {mostradas} de {total} transações."
VAZIO_FILTRO = (
    "Nenhuma transação com os filtros escolhidos. "
    "Marque ao menos uma decisão em \u201cMostrar decisões\u201d."
)
AJUDA_COLUNA_SINAIS = "Quantidade de sinais de alerta disparados."
BUSCA_ID = "Ou escolha pelo ID da transação"

# Painel da transação
TITULO_PAINEL = "Transação {id}"
RESUMO_PAINEL = "{data_hora} · {tipo} · {modalidade} · {valor}"
NOTA_TEXTO = "Nota de risco: {nota} de 100"
TITULO_SINAIS = "Sinais de alerta ({quantidade})"
SEM_SINAIS = "Nenhum sinal de alerta: a transação segue o padrão das compras legítimas."
TITULO_EXPLICACAO = "Explicação do agente"
GERANDO_EXPLICACAO = (
    "O IBM Granite está escrevendo a explicação… A primeira pode levar até 1 minuto."
)
MONTANDO_EXPLICACAO = "Montando a explicação…"
FONTE_GRANITE = "Explicação gerada por: IBM Granite 4"
FONTE_REGRAS = "Explicação gerada por: regras"
FONTE_REGRAS_INDISPONIVEL = "Explicação gerada por: regras (IBM Granite indisponível no momento)"
TITULO_RESPOSTA = "Sua avaliação"
BOTAO_FRAUDE = "Confirmar fraude"
BOTAO_LEGITIMA = "Marcar como legítima"
TOAST_FRAUDE = "Resposta registrada: fraude confirmada."
TOAST_LEGITIMA = "Resposta registrada: transação legítima."
RESPOSTA_ATUAL = "Sua resposta: {resposta} em {data_hora}. Você pode mudar; vale a última."
SEM_RESPOSTA = "Ainda sem resposta para esta transação."
ROTULOS_RESPOSTA = {"fraude": "Fraude confirmada", "legitima": "Transação legítima"}
ERRO_GRAVAR = (
    "Não foi possível salvar a resposta em data/feedback.csv. Feche o arquivo se ele "
    "estiver aberto em outro programa e tente de novo."
)
ERRO_LER_RESPOSTAS = (
    "O arquivo data/feedback.csv está com formato inválido. Renomeie ou apague "
    "o arquivo e registre as respostas de novo."
)
TITULO_HISTORICO = "Histórico do cartão (últimas {n} transações antes desta)"
HISTORICO_VAZIO = "Nenhuma transação anterior deste cartão na base."
HISTORICO_SEM_CARTAO = (
    "Esta transação não tem identificação de cartão; o histórico não está disponível."
)
ROTULOS_TIPO = {"credito": "Crédito", "debito": "Débito"}
ROTULOS_MODALIDADE = {"cartao_presente": "Presente", "cartao_nao_presente": "Não presente"}

# Página Desempenho
TITULO_DESEMPENHO = "Desempenho em março de 2025"
LEGENDA_DESEMPENHO = (
    "Comparação entre o Sentinela e o sistema atual da Sicredi nas "
    "{transacoes} transações de teste."
)
DELTA_SENTINELA = "{diferenca:+d} em relação ao sistema atual"
AJUDA_LEGITIMAS_BLOQUEADAS = "Compras legítimas que o Sentinela bloqueou por engano."
AJUDA_CONFIRMACOES = "{percentual} das transações de março."
TITULO_GRAFICO = "Fraudes de março bloqueadas"
TITULO_COMPARACAO = "Comparação"
TITULO_DETALHES_MODELO = "Detalhes do modelo (regressão logística)"
AVISO_SINTETICO = (
    "Dados sintéticos: o resultado é otimista. Em produção, o modelo precisaria "
    "de monitoramento e retreino com as respostas dos analistas."
)

# Página Como funciona
TITULO_COMO = "Como o Sentinela decide"
LEAD_COMO = (
    "Para cada compra, o agente usa suas ferramentas e um analista humano dá a palavra "
    "final. A IA explica; quem decide são regras e um modelo auditáveis."
)
TITULO_PASSOS = "Os passos do agente"
PASSOS = [
    "Calcula 9 sinais de alerta com regras simples, como rajadas de uso e saltos geográficos.",
    "Dá uma nota de risco de 0 a 100 com um modelo de regressão logística.",
    "Decide entre aprovar, pedir confirmação ao cliente ou bloquear e enviar ao analista.",
    "Explica a decisão em português com o IBM Granite, ou a partir dos sinais.",
    "O analista confirma a fraude ou marca como legítima, e a resposta fica registrada.",
]
TITULO_SINAIS_COMO = "Os 9 sinais de alerta"
SINAIS_EXPLICADOS = [
    (
        "Uso acelerado em terminais",
        "Cartão usado {LIMIAR_VELOCIDADE_TERMINAL} vezes ou mais em terminais na última hora",
    ),
    (
        "Rajada de transações",
        "{LIMIAR_RAJADA_1MIN} transações ou mais do cartão no último minuto",
    ),
    (
        "Token de carteira digital",
        "Token usado {LIMIAR_TOKEN_CARTEIRA} vezes ou mais em 3 meses",
    ),
    (
        "Salto geográfico",
        "Terminal a mais de {LIMIAR_DISTANCIA_KM} km do anterior em menos de uma hora",
    ),
    (
        "Madrugada",
        "Compra feita antes das {HORA_FIM_MADRUGADA}h da manhã",
    ),
    (
        "Valor alto",
        "Valor acima de R$ {LIMIAR_VALOR_ALTO}",
    ),
    (
        "Crédito sem cartão presente",
        "Compra online no crédito",
    ),
    (
        "IP de país desconhecido",
        "Endereço IP sem país identificado (código ZZ)",
    ),
    (
        "Estabelecimento de risco",
        "Risco do estabelecimento igual ou acima de {LIMIAR_RISCO_ESTABELECIMENTO}",
    ),
]
TITULO_DECISAO = "Como a decisão é tomada"
REGRAS_DECISAO = [
    "Bloquear e enviar ao analista: nota de {NOTA_BLOQUEAR} ou mais, ou IP de país desconhecido.",
    (
        "Pedir confirmação ao cliente: nota de {NOTA_CONFIRMAR} ou mais, "
        "ou {MIN_SINAIS_CONFIRMAR} sinais ou mais."
    ),
    "Aprovar: nos demais casos.",
]
TITULO_DADOS = "Sobre os dados"
SOBRE_DADOS = (
    "A base tem {linhas} transações sintéticas de 2025, das quais {fraudes} são fraude "
    "({percentual}). A fila de demonstração tem todas as fraudes de março e {amostra} "
    "compras legítimas de março sorteadas."
)
TITULO_LIMITACOES = "Limitações"
LIMITACOES = [
    "Os dados são sintéticos e fáceis de separar; em dados reais o desempenho seria menor.",
    (
        "Todas as fraudes da base estão entre janeiro e março de 2025; "
        "em uso real, o modelo precisa de monitoramento."
    ),
    "Pedir confirmação ao cliente é só indicado na tela; nenhuma notificação é enviada.",
    "As respostas do analista ficam salvas, mas ainda não retreinam o modelo automaticamente.",
]
