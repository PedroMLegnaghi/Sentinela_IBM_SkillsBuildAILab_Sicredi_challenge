/**
 * Dados inventados para todas as rotas da API (ESPECIFICACAO, seções 12 e 15).
 * Usados quando NEXT_PUBLIC_USAR_MOCK=1. Nunca contêm linhas de data/.
 */

import type {
  RespostaSaude,
  RespostaFila,
  RespostaTransacao,
  RespostaAnalisar,
  RespostaAuditoriaIniciada,
  Auditoria,
  RespostaRespostas,
  RespostaMetricas,
  Notificacao,
  RespostaNotificacoes,
  PerfilAssociado,
  RespostaPergunta,
} from "@/lib/tipos";

const saude: RespostaSaude = {
  status: "ok",
  modelo_carregado: true,
  dados_carregados: true,
  auditoria: "local",
};

const fila: RespostaFila = {
  total_fila: 2054,
  contagens: {
    BLOQUEAR: 54,
    PEDIR_CONFIRMACAO: 25,
    APROVAR: 1975,
  },
  itens: [
    {
      id_transacao: 100001,
      nota: 97.3,
      decisao: "BLOQUEAR",
      valor: 4520.0,
      data_hora: "2025-03-15T03:12:00",
      tipo_transacao: "credito",
      modalidade_transacao: "cartao_nao_presente",
      n_sinais: 5,
    },
    {
      id_transacao: 100002,
      nota: 72.1,
      decisao: "PEDIR_CONFIRMACAO",
      valor: 890.5,
      data_hora: "2025-03-15T14:33:00",
      tipo_transacao: "credito",
      modalidade_transacao: "cartao_presente",
      n_sinais: 2,
    },
    {
      id_transacao: 100003,
      nota: 12.4,
      decisao: "APROVAR",
      valor: 150.0,
      data_hora: "2025-03-16T09:05:00",
      tipo_transacao: "debito",
      modalidade_transacao: "cartao_presente",
      n_sinais: 0,
    },
  ],
};

const transacao: RespostaTransacao = {
  transacao: {
    id_transacao: 100001,
    data_hora: "2025-03-15T03:12:00",
    valor: 4520.0,
    tipo_transacao: "credito",
    modalidade_transacao: "cartao_nao_presente",
    hora: 3.2,
    madrugada: 1.0,
    credito: 1.0,
    nao_presente: 1.0,
    ip_pais_desconhecido: 1.0,
    vel_cartao_terminal_1h: 8.0,
    qtd_transacoes_cartao_1min: 4.0,
    qtd_token_carteira_3m: 12.0,
    dist_terminal_anterior_km: 520.0,
    risco_estabelecimento: 0.85,
  },
  analise: {
    nota: 97.3,
    decisao: "BLOQUEAR",
    decisao_legivel: "Bloquear e enviar ao analista",
    sinais: [
      { id: "madrugada", descricao: "Compra feita na madrugada (03h)." },
      { id: "ip_pais_desconhecido", descricao: "IP de país desconhecido." },
      { id: "vel_cartao_terminal_1h", descricao: "Cartão usado 8 vezes em terminais na última hora." },
      { id: "salto_geografico", descricao: "Terminal a 520 km do anterior em menos de 1 hora." },
      { id: "credito_nao_presente", descricao: "Compra online no crédito." },
    ],
    explicacao:
      "A transação apresenta múltiplos sinais de alerta: compra na madrugada com IP de país desconhecido, uso acelerado do cartão e salto geográfico expressivo. O risco é muito alto.",
    contribuicoes: [],
    latencia_ms: 12.5,
  },
  historico: [
    {
      data_hora: "2025-03-14T22:45:00",
      valor: 200.0,
      tipo_transacao: "credito",
      modalidade_transacao: "cartao_presente",
      dist_terminal_anterior_km: 0.5,
    },
    {
      data_hora: "2025-03-14T18:30:00",
      valor: 80.0,
      tipo_transacao: "debito",
      modalidade_transacao: "cartao_presente",
      dist_terminal_anterior_km: 1.2,
    },
  ],
  resposta_analista: null,
  perfil_associado: {
    compras_anteriores: 8,
    mediana_valor: 150.0,
    valor_atual_sobre_mediana: 30.1,
    hora_mais_comum: 14,
    percentual_madrugada: 12.5,
    percentual_credito_nao_presente: 25.0,
  } satisfies PerfilAssociado,
  notificacao: null,
};

const analisar: RespostaAnalisar = {
  analise: {
    nota: 85.0,
    decisao: "BLOQUEAR",
    decisao_legivel: "Bloquear e enviar ao analista",
    sinais: [
      { id: "madrugada", descricao: "Compra feita na madrugada." },
      { id: "ip_pais_desconhecido", descricao: "IP de país desconhecido." },
    ],
    explicacao:
      "Transação simulada com dois sinais críticos disparados.",
    contribuicoes: [],
    latencia_ms: 8.1,
  },
  id_auditoria: "aud-mock-001",
  id_notificacao: "not-mock-001",
};

const notificacaoAguardando: Notificacao = {
  id_notificacao: "not-mock-001",
  id_transacao: null,
  tipo: "AVISO_BLOQUEIO",
  mensagem:
    "Sicredi: bloqueamos uma compra de R$ 4.520,00 em 15/03 às 03:12 por segurança. Seu cartão está protegido. Foi você? Responda no app.",
  fonte_mensagem: "modelo",
  criada_em: "2025-03-15T03:12:05",
  status: "aguardando",
  respondida_em: null,
  resultado: null,
};

const notificacaoNegada: Notificacao = {
  ...notificacaoAguardando,
  id_notificacao: "not-mock-002",
  id_transacao: 100002,
  tipo: "CONFIRMACAO",
  mensagem:
    "Sicredi: compra de R$ 890,50 em 15/03 às 14:33 no seu cartão de crédito. Foi você? Responda no app.",
  status: "negada",
  respondida_em: "2025-03-15T14:40:00",
  resultado:
    "Compra bloqueada e cartão protegido. O caso foi para o analista.",
};

// Notificação com mensagem redigida pelo IBM Granite (fonte "watsonx") — Issue #109.
const notificacaoGranite: Notificacao = {
  ...notificacaoAguardando,
  id_notificacao: "not-mock-003",
  id_transacao: 100001,
  mensagem:
    "Sicredi: identificamos uma compra suspeita de R$ 4.520,00 em 15/03 às 03:12 e a bloqueamos por segurança. Seu cartão segue protegido. Foi você? Responda no app.",
  fonte_mensagem: "watsonx",
};

const notificacoes: RespostaNotificacoes = {
  itens: [notificacaoAguardando, notificacaoNegada],
};

const auditoriaIniciada: RespostaAuditoriaIniciada = {
  id_auditoria: "aud-mock-001",
  status: "pendente",
};

const auditoriaPendente: Auditoria = {
  id_auditoria: "aud-mock-001",
  status: "pendente",
  relatorio: null,
  latencia_ms: null,
  mensagem: null,
};

const auditoriaConcluida: Auditoria = {
  id_auditoria: "aud-mock-001",
  status: "concluida",
  relatorio: {
    parecer: "CONFIRMA",
    risco_ia: "ALTO",
    confianca: "ALTA",
    explicacao:
      "A auditoria confirma a decisão de bloqueio. Os sinais são consistentes com fraude: IP desconhecido e uso acelerado do cartão em horário atípico.",
    evidencias_a_favor: [
      "IP de país desconhecido detectado.",
      "Cartão usado 8 vezes em terminais em 1 hora.",
      "Compra na madrugada fora do padrão do cliente.",
    ],
    evidencias_contra: [],
    dados_ausentes: [],
    ferramentas_usadas: [
      { nome: "sinais_da_transacao", resumo: "5 sinais disparados." },
      { nome: "historico_do_cartao", resumo: "Padrão normal até 22h do dia anterior." },
      { nome: "perfil_do_cliente", resumo: "Mediana de R$ 150, raramente compra na madrugada." },
    ],
    fonte: "local",
    modelo: "modo-local",
  },
  latencia_ms: 320.0,
  mensagem: null,
};

const respostas: RespostaRespostas = {
  total: 3,
  fraudes: 2,
  legitimas: 1,
  concordancia: 66.7,
  itens: [
    {
      id_transacao: 100001,
      resposta: "fraude",
      registrado_em: "2025-03-15T10:00:00",
      decisao: "BLOQUEAR",
      nota: 97.3,
    },
    {
      id_transacao: 100002,
      resposta: "legitima",
      registrado_em: "2025-03-15T10:05:00",
      decisao: "PEDIR_CONFIRMACAO",
      nota: 72.1,
    },
    {
      id_transacao: 100003,
      resposta: "fraude",
      registrado_em: "2025-03-15T10:10:00",
      decisao: "APROVAR",
      nota: 12.4,
    },
  ],
};

const metricas: RespostaMetricas = {
  metricas: {
    modelo: "regressao_logistica",
    treino: { linhas: 25923, fraudes: 92 },
    teste: { linhas: 13608, fraudes: 54 },
    pr_auc: 1.0,
    roc_auc: 1.0,
    limiares: [
      { limiar: 30, alertas: 54, fraudes_detectadas: 54, precisao: 1.0, recall: 1.0 },
      { limiar: 50, alertas: 54, fraudes_detectadas: 54, precisao: 1.0, recall: 1.0 },
      { limiar: 70, alertas: 54, fraudes_detectadas: 54, precisao: 1.0, recall: 1.0 },
      { limiar: 90, alertas: 52, fraudes_detectadas: 52, precisao: 1.0, recall: 0.963 },
    ],
    comparacao_hgb: { pr_auc: 1.0, roc_auc: 1.0 },
  },
  avaliacao: {
    periodo: "2025-03",
    transacoes: 13608,
    fraudes_total: 54,
    sentinela: {
      bloqueadas: 54,
      fraudes_bloqueadas: 54,
      confirmacoes: 159,
      fraudes_em_confirmacao: 0,
      aprovadas: 13395,
      fraudes_aprovadas: 0,
    },
    sistema_atual: { bloqueadas: 26, fraudes_bloqueadas: 26, fraudes_nao_bloqueadas: 28 },
  },
  extras: {
    avaliacao_rigorosa: null,
    custos: null,
    eda: null,
    ia_contra_modelo: {
      transacoes: 254,
      fraudes: 54,
      fontes: { watsonx: 254 },
      latencia_modelo: { p50_ms: 1.5, p95_ms: 2.1 },
      latencia_ia: { p50_ms: 3200.0, p95_ms: 5400.0 },
      pareceres: { CONFIRMA: 232, DIVERGE: 18, INCONCLUSIVO: 4 },
      concordancia_por_decisao: { APROVAR: 89.0, PEDIR_CONFIRMACAO: 100.0, BLOQUEAR: 100.0 },
      modelo: { alertas: 56, fraudes_pegas: 54, recall: 100.0, precisao: 96.4 },
      ia_sozinha: { alertas: 78, fraudes_pegas: 54, recall: 100.0, precisao: 69.2 },
    },
  },
};

const pergunta: RespostaPergunta = {
  resposta:
    "A compra foi feita na madrugada, com IP de país desconhecido, e o valor é bem acima da mediana do associado. Esses pontos explicam a decisão do modelo.",
  ferramentas_usadas: [
    { nome: "sinais_da_transacao", resumo: "5 sinal(is) de alerta" },
    { nome: "perfil_do_cliente", resumo: "8 compras anteriores do cliente" },
  ],
  fonte: "local",
  latencia_ms: 1800.0,
};

export const mocks = {
  saude,
  fila,
  transacao,
  analisar,
  auditoriaIniciada,
  auditoriaPendente,
  auditoriaConcluida,
  respostas,
  metricas,
  notificacaoAguardando,
  notificacaoNegada,
  notificacaoGranite,
  notificacoes,
  pergunta,
};