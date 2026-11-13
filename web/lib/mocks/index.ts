/**
 * Dados inventados para todas as rotas da API (ESPECIFICACAO, seção 12).
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
    fraudes_total: 54,
    transacoes: 13608,
    sentinela: {
      fraudes_bloqueadas: 54,
      bloqueadas: 54,
      confirmacoes: 159,
    },
    sistema_atual: {
      fraudes_bloqueadas: 26,
    },
    pr_auc: 0.981,
    roc_auc: 0.998,
  },
  avaliacao: {
    limiares: [
      {
        nota_corte: 50,
        alertas: 213,
        fraudes_detectadas: 54,
        precisao: 0.253,
        recall: 1.0,
      },
    ],
  },
  extras: {
    avaliacao_rigorosa: null,
    custos: null,
    eda: null,
    ia_contra_modelo: null,
  },
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
};
