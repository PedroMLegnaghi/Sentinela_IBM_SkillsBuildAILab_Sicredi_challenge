/**
 * Textos de tela do site Sentinela.
 * Todos os textos visíveis ao usuário ficam aqui; nenhum texto literal nos componentes.
 * Cada Issue acrescenta textos dentro do próprio bloco; merges não conflitam.
 */

// --- Aplicação ---
export const TITULO_APP = "Sentinela";
export const SUBTITULO_APP = "Agente antifraude · Desafio Sicredi";
export const RODAPE_DADOS =
  "Sentinela · agente antifraude do Desafio Sicredi. Dados 100% sintéticos fornecidos pela Sicredi. Protótipo do IBM SkillsBuild AI Lab.";

// --- Navegação ---
export const NAV_FILA = "Fila de alertas";
export const NAV_DESEMPENHO = "Desempenho";
export const NAV_COMO_FUNCIONA = "Como funciona";
export const NAV_SIMULADOR = "Simulador";
export const NAV_RESPOSTAS = "Respostas";

// --- Estados comuns ---
export const CARREGANDO = "Carregando…";
export const VAZIO_PADRAO = "Nenhum item encontrado.";
export const ERRO_API =
  "Não foi possível carregar os dados. Verifique se a API está em execução (python -m uvicorn src.api.app:app --port 8000) e tente de novo.";
export const TENTAR_NOVAMENTE = "Tentar de novo";

// --- Decisões ---
export const ROTULOS_DECISAO: Record<string, string> = {
  BLOQUEAR: "Bloquear e enviar ao analista",
  PEDIR_CONFIRMACAO: "Pedir confirmação ao cliente",
  APROVAR: "Aprovar",
};

export const ROTULOS_CURTOS_DECISAO: Record<string, string> = {
  BLOQUEAR: "Bloquear",
  PEDIR_CONFIRMACAO: "Pedir confirmação",
  APROVAR: "Aprovar",
};

// --- Issue #43 ---
export const LEGENDA_FILA =
  "Transações de março de 2025, da mais arriscada para a menos arriscada. O modelo decide na hora; a IA audita em seguida.";
export const INDICADOR_NA_FILA = "Na fila";
export const FILTRO_DECISOES = "Mostrar decisões";
export const FILTRO_VAZIO =
  "Nenhuma transação com os filtros escolhidos. Marque ao menos uma decisão.";
export const MOSTRANDO = (mostradas: string, total: string) =>
  `Mostrando ${mostradas} de ${total} transações.`;
export const COLUNAS_FILA = {
  id: "ID",
  nota: "Nota",
  decisao: "Decisão",
  valor: "Valor",
  dataHora: "Data e hora",
  tipo: "Tipo",
  sinais: "Sinais",
};
export const ROTULO_TABELA_FILA =
  "Fila de alertas: clique numa linha para analisar";
export const ABRIR_TRANSACAO = (id: number) => `Abrir a transação ${id}`;
export const ITENS_POR_PAGINA = "Itens por página";
export const PAGINACAO = {
  intervaloItens: (min: number, max: number, total: number) =>
    `${min.toLocaleString("pt-BR")}–${max.toLocaleString("pt-BR")} de ${total.toLocaleString("pt-BR")}`,
  intervaloPaginas: (_atual: number, total: number) => `de ${total} páginas`,
  anterior: "Página anterior",
  proxima: "Próxima página",
  pagina: "Página",
};
export const SELECIONE_TRANSACAO =
  "Selecione uma transação na fila para ver a análise.";
export const TITULO_PAINEL = (id: number) => `Transação ${id}`;
export const TITULO_DECISAO_MODELO = "Decisão do modelo";
export const LEGENDA_LATENCIA = (ms: string) =>
  `Decidido em ${ms} ms, na hora da compra.`;
export const TITULO_SINAIS = (n: number) => `Sinais de alerta (${n})`;
export const SEM_SINAIS =
  "Nenhum sinal de alerta: a transação segue o padrão das compras legítimas.";
export const TITULO_CONTRIBUICOES = "O que pesou na nota";
export const LEGENDA_CONTRIBUICOES =
  "Barras para a direita aumentaram o risco; para a esquerda, diminuíram.";
export const SEM_CONTRIBUICOES =
  "As contribuições de cada variável ainda não estão disponíveis.";
export const TITULO_EXPLICACAO = "Explicação do modelo";
export const TITULO_AUDITORIA = "Auditoria da IA";
export const AUDITORIA_PENDENTE = "A IA está auditando esta decisão…";
export const AUDITORIA_DEMOROU =
  "A auditoria demorou mais que o esperado. A decisão do modelo continua válida.";
export const ROTULOS_PARECER: Record<string, string> = {
  CONFIRMA: "A IA confirma a decisão do modelo",
  DIVERGE: "A IA diverge do modelo: analise com atenção",
  INCONCLUSIVO: "A IA não chegou a uma conclusão",
};
export const ROTULOS_RISCO_IA: Record<string, string> = {
  BAIXO: "baixo",
  SUSPEITO: "suspeito",
  ALTO: "alto",
};
export const ROTULOS_CONFIANCA: Record<string, string> = {
  BAIXA: "baixa",
  MEDIA: "média",
  ALTA: "alta",
};
export const RISCO_E_CONFIANCA = (risco: string, confianca: string) =>
  `Risco segundo a IA: ${risco} · confiança ${confianca}`;
export const RISCO_INDEFINIDO = "indefinido";
export const EVIDENCIAS_A_FAVOR = "Evidências de risco";
export const EVIDENCIAS_CONTRA = "Evidências contra o risco";
export const DADOS_AUSENTES = "Dados que faltaram";
export const FERRAMENTAS_USADAS = "Ferramentas que a IA usou, na ordem";
export const FONTE_AUDITORIA = (fonte: string, modelo: string, ms: string) =>
  fonte === "watsonx"
    ? `Auditado pelo IBM watsonx.ai (${modelo}) em ${ms} ms.`
    : `Auditado em modo local por regras (watsonx.ai indisponível) em ${ms} ms.`;
export const NOMES_FERRAMENTAS: Record<string, string> = {
  sinais_da_transacao: "Sinais da transação",
  contribuicoes_da_nota: "O que pesou na nota",
  historico_do_cartao: "Histórico do cartão",
  perfil_do_cliente: "Perfil do cliente",
  perfil_do_estabelecimento: "Perfil do estabelecimento",
};
export const TITULO_RESPOSTA = "Sua avaliação";
export const BOTAO_FRAUDE = "Confirmar fraude";
export const BOTAO_LEGITIMA = "Marcar como legítima";
export const RESPOSTA_ATUAL = (resposta: string, quando: string) =>
  `Sua resposta: ${resposta} em ${quando}. Você pode mudar; vale a última.`;
export const SEM_RESPOSTA = "Ainda sem resposta para esta transação.";
export const ERRO_GRAVAR = "Não foi possível gravar a resposta. Tente de novo.";
export const TITULO_HISTORICO = (n: number) =>
  `Histórico do cartão (últimas ${n} compras antes desta)`;
export const HISTORICO_VAZIO = "Nenhuma compra anterior deste cartão na base.";
export const COLUNAS_HISTORICO = {
  dataHora: "Data e hora",
  valor: "Valor",
  tipo: "Tipo",
  modalidade: "Modalidade",
  distancia: "Distância do terminal anterior (km)",
};

// --- Issue #44 ---
export const TITULO_DESEMPENHO = "Desempenho em março de 2025";
export const LEGENDA_DESEMPENHO = (transacoes: string) =>
  `Comparação entre o Sentinela e o sistema atual da Sicredi nas ${transacoes} transações de teste.`;
export const INDICADORES_DESEMPENHO = {
  fraudes: "Fraudes em março",
  sentinela: "Bloqueadas pelo Sentinela",
  sistemaAtual: "Bloqueadas pelo sistema atual",
  legitimas: "Compras legítimas bloqueadas",
  confirmacoes: "Pedidos de confirmação",
};
export const DE_TOTAL = (parte: string, total: string) =>
  `${parte} de ${total}`;
export const DELTA_SENTINELA = (diferenca: number) =>
  `${diferenca >= 0 ? "+" : ""}${diferenca} em relação ao sistema atual`;
export const AJUDA_CONFIRMACOES = (percentual: string) =>
  `${percentual} das transações de março.`;
export const TITULO_GRAFICO_FRAUDES = "Fraudes de março bloqueadas";
export const ROTULO_SENTINELA = "Sentinela";
export const ROTULO_SISTEMA_ATUAL = "Sistema atual";
export const TITULO_COMPARACAO = "Comparação";
export const COLUNAS_COMPARACAO = {
  indicador: "Indicador",
  sistemaAtual: "Sistema atual",
  sentinela: "Sentinela",
};
export const LINHAS_COMPARACAO = {
  bloqueadas: "Fraudes bloqueadas",
  naoBloqueadas: "Fraudes não bloqueadas",
  percentual: "Percentual das fraudes bloqueadas",
  legitimas: "Compras legítimas bloqueadas",
};
export const TITULO_DETALHES_MODELO =
  "Detalhes do modelo (regressão logística)";
export const LEGENDA_DETALHES_MODELO = (
  treino: string,
  fraudesTreino: string,
) =>
  `Treinado com ${treino} transações de janeiro e fevereiro (${fraudesTreino} fraudes) e testado em março, como seria em produção.`;
export const COLUNAS_LIMIARES = {
  limiar: "Nota de corte",
  alertas: "Alertas",
  fraudes: "Fraudes detectadas",
  precisao: "Precisão",
  recall: "Recall",
};
export const COMPARACAO_HGB = (prAuc: string) =>
  `Um gradient boosting treinado para comparação chegou à mesma PR-AUC (${prAuc}); ficamos com a regressão logística por ser explicável variável a variável.`;
export const TITULO_IA_CONTRA_MODELO = "Modelo e IA lado a lado";
export const LEGENDA_IA_CONTRA_MODELO = (transacoes: string, fraudes: string) =>
  `Amostra de março com ${transacoes} transações (${fraudes} fraudes). O modelo decide; a IA audita a mesma compra em paralelo.`;
export const LINHAS_IA_CONTRA_MODELO = {
  latenciaP50: "Tempo típico (p50)",
  latenciaP95: "Tempo no pior caso comum (p95)",
  alertas: "Alertas",
  fraudes: "Fraudes pegas",
  precisao: "Precisão",
  recall: "Recall",
};
export const COLUNAS_IA_CONTRA_MODELO = {
  medida: "Medida",
  modelo: "Modelo (decide)",
  ia: "IA sozinha (audita)",
};
export const CONCORDANCIA_IA = (confirma: string) =>
  `A IA confirmou ${confirma} das decisões do modelo; as divergências viram casos para o analista olhar com atenção.`;
export const FONTES_IA = (fontes: string) => `Fonte das auditorias: ${fontes}.`;
export const TITULO_CUSTOS = "Custo da fraude em março";
export const ROTULOS_CUSTOS = {
  evitado: "Prejuízo evitado",
  sentinela: "Custo com o Sentinela",
  sistemaAtual: "Custo com o sistema atual",
};
export const AVISO_SINTETICO =
  "Dados sintéticos: o resultado é otimista. Em produção, o modelo precisaria de monitoramento e retreino com as respostas dos analistas.";
export const TITULO_COMO = "Como o Sentinela decide";
export const LEAD_COMO =
  "Uma compra no cartão precisa de resposta em milissegundos. O Sentinela decide na hora, avisa o associado quando algo foge do padrão e entrega à filial cada caso com uma segunda opinião da IA.";
export const TITULO_CAMINHO = "Do associado à filial em quatro passos";
export const PASSOS_CAMINHO = [
  "O associado faz a compra no cartão.",
  "O Sentinela decide na hora: calcula 9 sinais, dá uma nota de 0 a 100 e aprova, pede confirmação ou bloqueia.",
  'A IA audita a decisão e o associado confirma: a IA investiga a compra e diz se concorda; o associado responde "Foi você?" no app.',
  "A filial acompanha: o auditor revisa a fila da agência e o gerente vê os números da carteira.",
];
export const TITULO_SINAIS_COMO = "Os 9 sinais de alerta";
export const COLUNAS_SINAIS = { sinal: "Sinal", quando: "Dispara quando" };
// Limiares de src/config.py (ESPECIFICACAO, seção 8.1): mudar lá exige mudar aqui.
export const SINAIS_EXPLICADOS: Array<[string, string]> = [
  [
    "Uso acelerado em terminais",
    "Cartão usado 10 vezes ou mais em terminais na última hora",
  ],
  ["Rajada de transações", "5 transações ou mais do cartão no último minuto"],
  ["Token de carteira digital", "Token usado 30 vezes ou mais em 3 meses"],
  [
    "Salto geográfico",
    "Terminal a mais de 100 km do anterior em menos de uma hora",
  ],
  ["Madrugada", "Compra feita antes das 5h da manhã"],
  ["Valor alto", "Valor acima de R$ 150"],
  ["Crédito sem cartão presente", "Compra online no crédito"],
  ["IP de país desconhecido", "Endereço IP sem país identificado (código ZZ)"],
  ["Estabelecimento de risco", "Risco do estabelecimento igual ou acima de 40"],
];
export const TITULO_DECISAO_COMO = "Como a decisão é tomada";
export const REGRAS_DECISAO = [
  "Bloquear na hora e avisar o associado: nota de 70 ou mais, ou IP de país desconhecido.",
  "Pedir confirmação ao associado: nota de 30 ou mais, ou 3 sinais ou mais.",
  "Aprovar: nos demais casos.",
];
export const TITULO_IA_COMO = "Como a IA audita";
export const IA_COMO = [
  "A IA nunca muda a decisão do modelo: ela dá uma segunda opinião.",
  'Ela escolhe quais ferramentas usar e só afirma o que as ferramentas mostraram; o que faltou aparece em "dados que faltaram".',
  "O parecer (confirma, diverge ou inconclusivo) é calculado comparando o risco que a IA viu com a decisão do modelo.",
  "Sem conexão com o watsonx.ai, a auditoria roda em modo local, com as mesmas ferramentas e uma regra simples.",
];
export const TITULO_DADOS_COMO = "Sobre os dados";
export const SOBRE_DADOS =
  "A base tem 160.000 transações sintéticas de 2025, das quais 146 são fraude (0,09%). A fila de demonstração tem todas as fraudes de março e 2.000 compras legítimas de março sorteadas. Colunas que entregam a resposta (scores prontos, decisão do sistema atual, disputas) foram removidas.";
export const TITULO_LIMITACOES = "Limitações";
export const LIMITACOES = [
  "Os dados são sintéticos e fáceis de separar: três colunas de velocidade já calculadas carregam o resultado; em dados reais o desempenho seria menor.",
  "Todas as fraudes da base estão entre janeiro e março de 2025; em uso real, o modelo precisa de monitoramento.",
  "O aviso ao associado é simulado no app do site; nada é enviado por SMS ou push.",
  "As respostas do associado e do auditor ainda não retreinam o modelo automaticamente.",
];

// --- Issue #45 ---
export const TITULO_SIMULADOR = 'Simulador "e se"';
export const LEGENDA_SIMULADOR =
  "Escolha uma transação da fila, mude o que quiser e veja a decisão do modelo na hora e o parecer da IA logo depois. Nada é gravado.";
export const ESCOLHA_TRANSACAO = "Transação de partida";
export const OPCAO_TRANSACAO = (id: number, nota: string, decisao: string) =>
  `ID ${id} · nota ${nota} · ${decisao}`;
export const CAMPOS_SIMULADOR = {
  valor: "Valor (R$)",
  hora: "Hora da compra",
  credito: "Crédito",
  naoPresente: "Cartão não presente (online)",
  ip: "IP de país desconhecido",
  rajada: "Transações do cartão no último minuto",
  terminais: "Uso do cartão em terminais na última hora",
  token: "Uso do token de carteira em 3 meses",
  distancia: "Distância do terminal anterior (km)",
  risco: "Risco do estabelecimento (0 a 100)",
};
export const SIM = "Sim";
export const NAO = "Não";
export const BOTAO_ANALISAR = "Analisar a compra simulada";
export const BOTAO_VOLTAR_ORIGINAL = "Voltar aos valores originais";
export const TITULO_ORIGINAL = "Original";
export const TITULO_SIMULADA = "Simulada";
export const SIMULADA_VAZIA =
  'Mude algum valor e clique em "Analisar a compra simulada".';
export const MADRUGADA_CALCULADA = (sim: boolean) =>
  sim ? "Madrugada: sim (antes das 5h)" : "Madrugada: não";
export const TITULO_RESPOSTAS = "Respostas do analista";
export const LEGENDA_RESPOSTAS =
  "As respostas gravadas na Fila de alertas. Vale a última resposta de cada transação.";
export const INDICADORES_RESPOSTAS = {
  total: "Respostas",
  fraudes: "Fraudes confirmadas",
  legitimas: "Marcadas como legítimas",
  concordancia: "Concordância com o modelo",
};
export const AJUDA_CONCORDANCIA =
  "Fraude confirmada em transação bloqueada, ou legítima em transação aprovada ou com pedido de confirmação.";
export const COLUNAS_RESPOSTAS = {
  id: "ID",
  resposta: "Resposta",
  quando: "Respondida em",
  decisao: "Decisão do modelo",
  nota: "Nota",
};
export const BOTAO_EXPORTAR = "Exportar CSV";
export const NOME_ARQUIVO_CSV = "respostas-do-analista.csv";
export const RESPOSTAS_VAZIAS =
  'Ainda não há respostas. Abra uma transação na Fila de alertas e use "Confirmar fraude" ou "Marcar como legítima".';

// --- Issue #48 ---
// (textos de acessibilidade e correções serão adicionados aqui)

// --- Issue #63 — App do associado ---
export const NAV_ASSOCIADO = "App do associado";
export const TITULO_APP_ASSOCIADO = "App do associado";
export const LEGENDA_APP_ASSOCIADO =
  "Simulação do celular do associado. As notificações aparecem mais recentes primeiro.";
export const SEM_NOTIFICACOES =
  "Nenhuma notificação. Analise uma transação com decisão BLOQUEAR ou PEDIR_CONFIRMACAO para gerar uma.";
export const BOTAO_SIM_FUI_EU = "Sim, fui eu";
export const BOTAO_NAO_FUI_EU = "Não fui eu";
export const ROTULOS_STATUS_NOTIFICACAO: Record<string, string> = {
  aguardando: "Aguardando",
  confirmada: "Confirmou a compra",
  negada: "Não reconheceu",
};
export const ROTULOS_TIPO_NOTIFICACAO: Record<string, string> = {
  CONFIRMACAO: "Pedido de confirmação",
  AVISO_BLOQUEIO: "Aviso de bloqueio",
};
export const TITULO_BLOCO_ASSOCIADO = "Associado";
export const BOTAO_AVISAR_ASSOCIADO = "Avisar o associado";
export const AVISO_ASSOCIADO_ENVIADO = "Notificação enviada ao associado.";
export const ERRO_NOTIFICACAO_409 =
  "O associado já foi avisado sobre esta transação.";
export const ERRO_RESPOSTA_409 = "O associado já respondeu a esta notificação.";
export const ERRO_NOTIFICACAO_422 =
  "Não é possível notificar o associado em transações aprovadas.";
export const LINK_VER_NO_APP = "Ver no app do associado";
export const RESPONDIDA_EM = (quando: string) => `Respondida em ${quando}`;
export const CRIADA_EM = (quando: string) => `Enviada em ${quando}`;

// --- Issue #64 — Perfil do associado ---
export const TITULO_PERFIL_ASSOCIADO = "O normal deste associado";
export const PERFIL_SEM_HISTORICO =
  "Primeira compra registrada deste associado.";
export const PERFIL_COMPRAS_ANTERIORES = (n: number) =>
  `${n} ${n === 1 ? "compra anterior" : "compras anteriores"} na base`;
export const PERFIL_MEDIANA_VALOR = (valor: string) =>
  `Mediana de valor: ${valor}`;
export const PERFIL_RAZAO_MEDIANA = (razao: string) =>
  `Esta compra é ${razao}× a mediana`;
export const PERFIL_RAZAO_ALTA = "⚠ Esta compra é alta em relação à mediana";
export const PERFIL_HORA_MAIS_COMUM = (hora: number) =>
  `Hora mais comum: ${hora}h`;
export const PERFIL_PERCENTUAL_MADRUGADA = (pct: string) =>
  `Compras na madrugada: ${pct}%`;
export const PERFIL_CREDITO_NAO_PRESENTE = (pct: string) =>
  `Crédito não presente: ${pct}%`;

// --- Issue #67 — Privacidade e o associado (Como funciona) ---
export const TITULO_PRIVACIDADE_COMO = "Privacidade e o associado";
export const PRIVACIDADE_COMO = [
  "O modelo usa 11 variáveis comportamentais e operacionais: valor, hora, tipo de cartão, distâncias e contagens. Nenhum dado pessoal identificável entra no cálculo.",
  "Identificadores de cartão, cliente e estabelecimento nunca aparecem nas respostas da API, nos logs nem nas mensagens enviadas ao IBM watsonx.ai.",
  "Quando a decisão é pedir confirmação ou bloquear, o associado recebe uma mensagem validada contra 6 regras de segurança: começa com 'Sicredi:', até 160 caracteres, sem links, sem pedir senha ou código e sem número de cartão.",
  "Em março de 2025 (dados sintéticos): 0 compras legítimas bloqueadas e 159 pedidos de confirmação em 13.608 transações (1,2%).",
];

// --- Issue #91: identidade, molduras e entrada ---
export const ALT_LOGO = "Sicredi";
export const ENTRAR_TITULO = "Quem está entrando?";
export const ENTRAR_LEGENDA =
  "Acesso simulado, sem senha. Escolha uma pessoa para ver o Sentinela pelo lado dela.";
export const ENTRAR_BOTAO = "Entrar";
export const ENTRANDO = "Entrando…";
export const ROTULOS_PAPEL: Record<string, string> = {
  associado: "Associado",
  auditor: "Auditor",
  gerente: "Gerente",
  matriz: "Diretoria",
};
export const GRUPOS_PAPEL: Record<string, string> = {
  associado: "Associados",
  auditor: "Auditores da filial",
  gerente: "Gerentes da filial",
  matriz: "Matriz",
};
export const SAIR = "Sair";
export const NAV_INICIO = "Início";
export const NAV_EXTRATO = "Extrato";
export const NAV_COMPRAR = "Comprar";
export const NAV_CHAT = "Chat";
export const NAV_PAINEL_AGENCIA = "Painel da agência";
export const NAV_RESPOSTAS_ASSOCIADOS = "Respostas dos associados";
export const ROTULO_NAV_ASSOCIADO = "Navegação do app";
export const ROTULO_NAV_FILIAL = "Navegação da filial";
export const VERIFICANDO_SESSAO = "Abrindo…";

// --- Issue #93: início e extrato do associado ---
export const OLA = (nome: string) => `Olá, ${nome.split(" ")[0]}`;
export const SALDO_EM_CONTA = "Saldo em conta";
export const LIMITE_DISPONIVEL = "Limite disponível no crédito";
export const LIMITE_DE = (total: string) => `de ${total}`;
export const ROTULO_LIMITE = (usado: number) => `${usado}% do limite em uso`;
export const ATALHO_SIMULAR = "Simular compra";
export const ATALHO_EXTRATO = "Extrato";
export const ATALHO_CHAT = "Chat";
export const ATALHO_INVESTIR = "Investir";
export const ATALHO_EM_BREVE = "Em breve";
export const ROTULO_ATALHOS = "Atalhos";
export const PENDENTE_TITULO = "Uma compra espera a sua resposta.";
export const PENDENTE_DETALHE = (valor: string, quando: string) =>
  `${valor} em ${quando}.`;
export const PENDENTE_BOTAO = "Responder";
export const ULTIMAS_COMPRAS = "Últimas compras";
export const VER_EXTRATO = "Ver extrato completo";
export const MEUS_CARTOES = "Meus cartões";
export const CARTAO_DESCRICAO = (tipo: string, final: string) =>
  `${tipo} · final ${final}`;
export const CARTAO_BLOQUEADO = "Bloqueado";
export const TITULO_EXTRATO = "Extrato";
export const FILTROS_EXTRATO = "Filtrar compras";
export const FILTRO_TODAS = "Todas";
export const ROTULOS_SITUACAO: Record<string, string> = {
  APROVADA: "Aprovada",
  AGUARDANDO: "Aguardando você",
  BLOQUEADA: "Bloqueada",
  CONTESTADA: "Contestada",
};
export const ROTULOS_FILTRO_SITUACAO: Record<string, string> = {
  APROVADA: "Aprovadas",
  AGUARDANDO: "Aguardando",
  BLOQUEADA: "Bloqueadas",
  CONTESTADA: "Contestadas",
};
export const EXTRATO_VAZIO = "Nenhuma compra com este filtro.";
export const COMPRA_SIMULADA = "Simulada";
export const DESCRICAO_COMPRA = (quando: string, tipo: string) =>
  `${quando} · ${tipo}`;
export const ABRIR_COMPRA = (estabelecimento: string, valor: string) =>
  `Abrir a compra em ${estabelecimento}, ${valor}`;
export const VOLTAR = "Voltar";
export const DETALHE_QUANDO = "Quando";
export const DETALHE_CARTAO = "Cartão";
export const DETALHE_SITUACAO = "Situação";
export const DETALHE_BLOQUEADA_POR = "Bloqueada por";
export const DETALHE_EM = "Em";
export const DETALHE_MOTIVO = "Motivo";
export const RESPOSTA_REGISTRADA = (resposta: string, quando: string) =>
  `Você respondeu "${resposta}" em ${quando}.`;
export const RESPOSTA_SIM = "Fui eu";
export const RESPOSTA_NAO = "Não fui eu";
export const VALOR_NAO_COBRADO = "O valor não foi cobrado.";

// --- Issue #95: simular compra, aviso e contestação ---
export const TITULO_COMPRAR = "Simular compra";
export const LEGENDA_COMPRAR =
  "Faça uma compra de mentira para ver o Sentinela agir. Ela entra no seu extrato e na fila da sua agência.";
export const CENARIO_PRONTO = "Cenário pronto";
export const CAMPOS_COMPRA = {
  cartao: "Cartão",
  valor: "Valor (R$)",
  hora: "Hora (0 a 23)",
  estabelecimento: "Estabelecimento",
  modalidade: "Como pagou",
  pais: "País do acesso",
  rajada: "Compras no último minuto",
  terminais: "Usos do cartão na última hora",
  token: "Usos da carteira digital em 3 meses",
  distancia: "Distância da compra anterior (km)",
};
export const MODALIDADES = {
  presente: "Cartão na mão",
  naoPresente: "Pela internet",
};
export const PAISES = {
  conhecido: "Brasil",
  desconhecido: "País desconhecido",
};
export const MAIS_DETALHES = "Mais detalhes da compra";
export const BOTAO_COMPRAR = "Fazer a compra";
export const COMPRANDO = "Enviando…";
export const RESULTADO_COMPRA: Record<
  string,
  { titulo: string; texto: string }
> = {
  APROVADA: {
    titulo: "Compra aprovada.",
    texto: "O valor já aparece no seu extrato.",
  },
  AGUARDANDO: {
    titulo: "Precisamos confirmar com você.",
    texto: "Enviamos um aviso. A compra fica em espera até a sua resposta.",
  },
  BLOQUEADA: {
    titulo: "Compra bloqueada por segurança.",
    texto:
      "A compra fugiu do seu padrão de uso. Enviamos um aviso para você confirmar se foi você.",
  },
  CONTESTADA: { titulo: "Compra contestada.", texto: "" },
};
export const VER_AVISO = "Responder ao aviso";
export const VER_COMPRA = "Ver a compra";
export const SALDO_AGORA = (saldo: string) => `Saldo agora: ${saldo}.`;
export const ERRO_CARTAO_BLOQUEADO =
  "Este cartão está bloqueado. Escolha outro cartão.";
export const TITULO_AVISO = "Confirme esta compra";
export const MENSAGEM_DO_SICREDI = "Mensagem do Sicredi";
export const RODAPE_SEGURANCA =
  "O Sicredi nunca pede senha, código ou link por mensagem.";
export const AVISO_JA_RESPONDIDO = "Você já respondeu a este aviso.";
export const DETALHE_VALOR = "Valor";
export const CONTESTAR = "Não reconheço esta compra";
export const CONTESTAR_EXPLICACAO =
  "O cartão será bloqueado e a sua agência será avisada.";
export const CONTESTAR_CONFIRMAR = "Sim, contestar e bloquear o cartão";
export const CANCELAR = "Cancelar";
export const CONTESTADA_OK =
  "Compra contestada. O cartão foi bloqueado e a sua agência foi avisada.";

// --- Issue #97: fila do auditor e painel da compra na filial ---
export const TITULO_FILA_FILIAL = "Fila de alertas";
export const LEGENDA_FILA_FILIAL = (total: string, agencia: string) =>
  `${total} compras sinalizadas na carteira da ${agencia}, da mais arriscada para a menos arriscada.`;
export const FILTROS_FILA = "Filtrar a fila";
export const ROTULOS_FILTRO_FILA: Record<string, string> = {
  BLOQUEADA: "Bloqueadas",
  AGUARDANDO: "Aguardando associado",
  CONTESTADA: "Contestadas",
};
export const ROTULOS_SITUACAO_FILIAL: Record<string, string> = {
  APROVADA: "Aprovada",
  AGUARDANDO: "Aguardando",
  BLOQUEADA: "Bloqueada",
  CONTESTADA: "Contestada",
};
export const COLUNAS_FILA_FILIAL = {
  nota: "Nota",
  associado: "Associado",
  quando: "Quando",
  valor: "Valor",
  situacao: "Situação",
  ia: "IA",
};
export const ROTULO_TABELA_FILA_FILIAL =
  "Compras da agência: escolha uma para ver o detalhe";
export const ASSOCIADO_E_CARTAO = (nome: string, final: string) =>
  `${nome} · final ${final}`;
export const ROTULOS_VEREDITO: Record<string, string> = {
  CONFIRMA: "Confirma",
  DIVERGE: "Diverge",
  INCONCLUSIVO: "Inconclusivo",
};
export const SEM_VEREDITO = "—";
export const FILA_FILIAL_VAZIA = "Nenhuma compra com este filtro.";
export const ESCOLHA_UMA_COMPRA =
  "Escolha uma compra na fila para ver o detalhe.";
export const COMPRA_EM_ANALISE = "Compra em análise";
export const ROTULO_NOTA = "Nota de risco";
export const NOTA_DE_100 = (nota: string) => `${nota} de 100`;
export const DECISAO_DO_MODELO = "Decisão do modelo";
export const TITULO_SINAIS_FILIAL = (n: number) => `Sinais de alerta (${n})`;
export const EXPLICACAO_DO_MODELO = "Explicação do modelo";
export const TITULO_ASSOCIADO_FILIAL = "Associado";
export const SEM_RESPOSTA_ASSOCIADO =
  "O associado ainda não respondeu ao aviso.";
export const RESPOSTA_DO_ASSOCIADO = (resposta: string, quando: string) =>
  `Respondeu "${resposta}" em ${quando}.`;
export const LEITURA_RESPOSTA = {
  nao: "Fraude provável.",
  sim: "O associado reconhece a compra.",
};
export const HISTORICO_AGREGADO = "Histórico (agregado)";
export const RESUMO_HISTORICO = (
  compras: string,
  mediana: string,
  contestacoes: string,
) =>
  `${compras} compras em 90 dias · mediana ${mediana} · ${contestacoes} contestações.`;
export const TITULO_BLOQUEIO = "Bloqueio";
export const BLOQUEIO_POR = (por: string, quando: string) =>
  `Bloqueada por ${por} em ${quando}.`;

// --- Issue #99: painel do gerente ---
export const TITULO_PAINEL_AGENCIA = "Painel da agência";
export const LEGENDA_PAINEL_AGENCIA = (
  periodo: string,
  compras: string,
  agencia: string,
) => `${periodo} · ${compras} compras na carteira da ${agencia}.`;
export const PERIODOS: Record<string, string> = { "2025-03": "Março de 2025" };
export const KPI_APROVADAS = "Aprovadas";
export const KPI_CONFIRMACOES = "Pedidos de confirmação";
export const KPI_BLOQUEADAS = "Bloqueadas";
export const KPI_TEMPO_RESPOSTA = "Tempo de resposta do associado";
export const DAS_COMPRAS = (pct: string) => `${pct} das compras`;
export const PROTEGIDOS = (valor: string) => `${valor} protegidos`;
export const MEDIANA = "mediana";
export const SEM_RESPOSTAS_AINDA = "Ainda não há respostas";
export const TITULO_DECISOES_TIPO = "Decisões por tipo de compra";
export const TIPO_E_MODALIDADE = (tipo: string, modalidade: string) =>
  `${tipo}, ${modalidade}`;
export const MODALIDADE_CURTA: Record<string, string> = {
  cartao_presente: "com cartão",
  cartao_nao_presente: "sem cartão",
};
export const DESCRICAO_BARRA_TIPO = (
  rotulo: string,
  aprovadas: string,
  confirmacoes: string,
  bloqueadas: string,
) =>
  `${rotulo}: ${aprovadas} aprovadas, ${confirmacoes} pedidos de confirmação e ${bloqueadas} bloqueadas.`;
export const LEGENDA_APROVADAS = "Aprovadas";
export const LEGENDA_CONFIRMACOES = "Pedidos de confirmação";
export const LEGENDA_BLOQUEADAS = "Bloqueadas";
export const TITULO_ACERTO_MODELO = "Acerto do modelo";
export const DOS_ALERTAS_RESPONDIDOS = "dos alertas respondidos";
export const DESCRICAO_ROSCA = (taxa: string) =>
  `O modelo acertou ${taxa} dos alertas que os associados responderam.`;
export const ALERTAS_CERTOS = (n: string) =>
  `${n} associados responderam "não fui eu": o alerta estava certo.`;
export const ALERTAS_DESNECESSARIOS = (n: string) =>
  `${n} responderam "fui eu": alerta desnecessário.`;
export const ALERTAS_SEM_RESPOSTA = (n: string) => `${n} ainda sem resposta.`;
export const EXPLICA_ACERTO =
  'O acerto vem da resposta do associado ao aviso: "não fui eu" confirma o alerta; "fui eu" mostra que o alerta não era necessário.';
export const TITULO_FRAUDES_APROVADAS = "Fraudes que o modelo aprovou";
export const EXPLICA_FRAUDES_APROVADAS =
  'Compras aprovadas que o associado contestou com "Não reconheço esta compra". Os cartões foram bloqueados.';
export const NENHUMA_FRAUDE_APROVADA = "Nenhuma contestação até agora.";
export const CARTAO_BLOQUEADO_ETIQUETA = "Cartão bloqueado";
export const DURACAO_MIN = (min: string) => `${min} min`;
export const DURACAO_S = (s: string) => `${s} s`;

// --- Issue #103: o auditor bloqueia ---
export const BLOQUEAR_COMPRA = "Bloquear compra";
export const BLOQUEAR_EXPLICACAO =
  "A compra ainda espera o associado. Ao bloquear, ela não é cobrada e o seu nome fica registrado no bloqueio.";
export const BLOQUEAR_AVISO_ASSOCIADO =
  "O associado verá que a compra foi bloqueada por um analista da agência, sem o seu nome.";
export const NOTA_DO_AUDITOR =
  "Nota para o registro (opcional, até 300 caracteres)";
export const CONFIRMAR_BLOQUEIO = "Confirmar bloqueio";
export const BLOQUEANDO = "Bloqueando…";
export const ERRO_BLOQUEIO_409 =
  "Esta compra já não espera o associado e não pode mais ser bloqueada.";
export const BLOQUEIO_FEITO =
  "Compra bloqueada. O associado já vê o bloqueio no app.";
export const LIBERACAO_AUTOMATICA =
  'Se o associado responder "fui eu", a compra é liberada sozinha.';

// --- Issue #104: bloqueios da equipe ---
export const TITULO_BLOQUEIOS_EQUIPE = "Bloqueios da equipe";
export const COLUNAS_BLOQUEIOS = {
  auditor: "Auditor",
  bloqueios: "Bloqueios",
  corretos: "Corretos",
  liberados: "Liberados depois",
};
export const EXPLICA_BLOQUEIOS =
  '"Correto" é quando o associado confirma que não fez a compra; "liberado depois" é quando ele responde "fui eu" e a compra é liberada sozinha.';
export const SEM_BLOQUEIOS_EQUIPE =
  "Nenhum bloqueio feito pela equipe até agora.";

// --- Issue #106: chat do associado ---
export const TITULO_CHAT = "Assistente Sicredi";
export const SUBTITULO_CHAT =
  "Tire dúvidas sobre os seus gastos e as suas compras.";
export const BOAS_VINDAS_CHAT =
  "Olá! Posso resumir os seus gastos, explicar uma compra bloqueada ou mostrar o que está esperando a sua confirmação. O que você quer saber?";
export const SUGESTOES_CHAT = [
  "Quanto gastei este mês?",
  "Por que minha compra foi bloqueada?",
  "Quais compras estão pendentes?",
];
export const ROTULO_SUGESTOES = "Sugestões de pergunta";
export const CAMPO_CHAT = "Escreva a sua pergunta";
export const ENVIAR = "Enviar";
export const DIGITANDO = "Digitando…";
export const FONTE_CHAT: Record<string, string> = {
  watsonx: "Resposta do IBM Granite (watsonx.ai)",
  local: "Resposta automática",
  gerente: "Gerente da agência",
};
export const CONVERSAR_COM_GERENTE = "Conversar com gerente";
export const CHAMANDO_GERENTE = "Chamando o gerente…";
export const GERENTE_DA_AGENCIA = (nome: string) =>
  `${nome} · gerente da agência`;
export const AVISO_GERENTE_SIMULADO =
  "Conversa simulada: neste protótipo, o gerente não responde depois do resumo.";
export const ROTULO_CONVERSA = "Conversa";
export const ERRO_CHAT =
  "Não consegui responder agora. Tente de novo em instantes.";
export const VOCE = "Você";
export const ASSISTENTE = "Assistente";

// --- Seção 17.8: painel da matriz ---
export const NAV_PAINEL_MATRIZ = "Painel da matriz";
export const TITULO_PAINEL_MATRIZ = "Painel da matriz";
export const LEGENDA_PAINEL_MATRIZ = (periodo: string, compras: string, agencias: number) =>
  `${periodo} · ${compras} compras em ${agencias} agências.`;
export const TITULO_MODELO_BASE = "O modelo em toda a base de teste";
export const LEGENDA_MODELO_BASE = (transacoes: string) =>
  `${transacoes} compras de março, que o modelo não viu no treino. Janeiro e fevereiro ficam de fora porque foram usados para treinar o modelo.`;
export const FRAUDES_BLOQUEADAS_SENTINELA = "Fraudes bloqueadas pelo Sentinela";
export const FRAUDES_BLOQUEADAS_ATUAL = "Fraudes bloqueadas pelo sistema atual";
export const LEGITIMAS_BLOQUEADAS = "Compras legítimas bloqueadas";
export const PEDIDOS_CONFIRMACAO = "Pedidos de confirmação";
export const DE_N = (parte: string, total: string) => `${parte} de ${total}`;
export const FRAUDES_QUE_PASSARAM = (n: string) => `${n} fraudes passaram`;
export const SEPARACAO_MODELO = (pr: string, roc: string) => `PR-AUC ${pr} · ROC-AUC ${roc}`;
export const TITULO_COMPARACAO_AGENCIAS = "Comparação entre agências";
export const ROTULO_TABELA_AGENCIAS = "Indicadores de cada agência e o total da cooperativa";
export const COLUNAS_AGENCIAS = {
  agencia: "Agência",
  compras: "Compras",
  aprovadas: "Aprovadas",
  confirmacoes: "Confirmações",
  bloqueadas: "Bloqueadas",
  protegido: "Valor protegido",
  acerto: "Acerto do modelo",
  fraudesAprovadas: "Fraudes aprovadas",
  tempo: "Resposta do associado",
};
export const TOTAL_COOPERATIVA = "Total da cooperativa";
export const TITULO_CONSOLIDADO = "Todas as agências";
export const COLUNA_AGENCIA = "Agência";
