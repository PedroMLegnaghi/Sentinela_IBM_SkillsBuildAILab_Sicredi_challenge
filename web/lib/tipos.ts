/**
 * Tipos TypeScript que espelham exatamente os objetos da API (ESPECIFICACAO, seções 12 e 13).
 * Nenhum campo inventado: qualquer mudança exige uma Issue que mude a ESPECIFICACAO primeiro.
 */

// --- Seção 12.1: Objetos da API ---

export interface Sinal {
  id: string;
  descricao: string;
}

export interface Contribuicao {
  variavel: string;
  nome: string;
  contribuicao: number;
}

export type Decisao = "APROVAR" | "PEDIR_CONFIRMACAO" | "BLOQUEAR";

export interface Analise {
  nota: number;
  decisao: Decisao;
  decisao_legivel: string;
  sinais: Sinal[];
  explicacao: string;
  contribuicoes: Contribuicao[];
  latencia_ms: number;
}

export interface ItemFila {
  id_transacao: number;
  nota: number;
  decisao: Decisao;
  valor: number | null;
  data_hora: string | null;
  tipo_transacao: string;
  modalidade_transacao: string;
  n_sinais: number;
}

export interface Transacao {
  id_transacao: number;
  data_hora: string | null;
  valor: number | null;
  tipo_transacao: string;
  modalidade_transacao: string;
  hora: number | null;
  madrugada: number | null;
  credito: number | null;
  nao_presente: number | null;
  ip_pais_desconhecido: number | null;
  vel_cartao_terminal_1h: number | null;
  qtd_transacoes_cartao_1min: number | null;
  qtd_token_carteira_3m: number | null;
  dist_terminal_anterior_km: number | null;
  risco_estabelecimento: number | null;
}

export interface ItemHistorico {
  data_hora: string | null;
  valor: number | null;
  tipo_transacao: string;
  modalidade_transacao: string;
  dist_terminal_anterior_km: number | null;
}

export interface Resposta {
  id_transacao: number;
  resposta: "fraude" | "legitima";
  registrado_em: string;
}

// --- Seção 12.2: Corpos de resposta dos endpoints ---

export interface RespostaFila {
  total_fila: number;
  contagens: {
    BLOQUEAR: number;
    PEDIR_CONFIRMACAO: number;
    APROVAR: number;
  };
  itens: ItemFila[];
}

// --- Seção 12.1: PerfilAssociado (Issue #64) ---

export interface PerfilAssociado {
  compras_anteriores: number;
  mediana_valor: number | null;
  valor_atual_sobre_mediana: number | null;
  hora_mais_comum: number | null;
  percentual_madrugada: number | null;
  percentual_credito_nao_presente: number | null;
}

export interface RespostaTransacao {
  transacao: Transacao;
  analise: Analise;
  historico: ItemHistorico[];
  resposta_analista: Resposta | null;
  perfil_associado: PerfilAssociado | null;
  notificacao: Notificacao | null;
}

export interface RespostaAnalisar {
  analise: Analise;
  id_auditoria: string | null;
  id_notificacao: string | null;
}

export interface RespostaAuditoriaIniciada {
  id_auditoria: string;
  status: string;
}

export interface RespostaRespostas {
  total: number;
  fraudes: number;
  legitimas: number;
  concordancia: number | null;
  itens: Array<{
    id_transacao: number;
    resposta: "fraude" | "legitima";
    registrado_em: string;
    decisao: Decisao;
    nota: number;
  }>;
}

/** modelos/metricas.json (ESPECIFICACAO, seção 7). */
export interface Metricas {
  modelo: string;
  treino: { linhas: number; fraudes: number };
  teste: { linhas: number; fraudes: number };
  pr_auc: number;
  roc_auc: number;
  limiares: Array<{
    limiar: number;
    alertas: number;
    fraudes_detectadas: number;
    precisao: number;
    recall: number;
  }>;
  comparacao_hgb?: { pr_auc: number; roc_auc: number };
}

/** modelos/avaliacao_agente.json (ESPECIFICACAO, seção 8.6). */
export interface AvaliacaoAgente {
  periodo: string;
  transacoes: number;
  fraudes_total: number;
  sentinela: {
    bloqueadas: number;
    fraudes_bloqueadas: number;
    confirmacoes: number;
    fraudes_em_confirmacao: number;
    aprovadas: number;
    fraudes_aprovadas: number;
  };
  sistema_atual: {
    bloqueadas: number;
    fraudes_bloqueadas: number;
    fraudes_nao_bloqueadas: number;
  };
}

/** Acerto de um conjunto de alertas (Issue #46). */
export interface AcertoAlertas {
  alertas: number;
  fraudes_pegas: number;
  recall: number | null;
  precisao: number | null;
}

/** modelos/ia_contra_modelo.json (Issue #46, src/avaliar_ia.py). */
export interface IaContraModelo {
  transacoes: number;
  fraudes: number;
  fontes: Record<string, number>;
  latencia_modelo: { p50_ms: number; p95_ms: number };
  latencia_ia: { p50_ms: number; p95_ms: number };
  pareceres: Record<string, number>;
  concordancia_por_decisao: Record<string, number | null>;
  modelo: AcertoAlertas;
  ia_sozinha: AcertoAlertas;
}

export interface RespostaMetricas {
  metricas: Metricas;
  avaliacao: AvaliacaoAgente;
  extras: {
    avaliacao_rigorosa: Record<string, unknown> | null;
    custos: Record<string, unknown> | null;
    eda: Record<string, unknown> | null;
    ia_contra_modelo: IaContraModelo | null;
  };
}

export interface RespostaSaude {
  status: string;
  modelo_carregado: boolean;
  dados_carregados: boolean;
  auditoria: "watsonx" | "local";
}

// --- Seção 13: Auditoria por IA ---

export type ParecerIA = "CONFIRMA" | "DIVERGE" | "INCONCLUSIVO";
export type RiscoIA = "BAIXO" | "SUSPEITO" | "ALTO";
export type Confianca = "BAIXA" | "MEDIA" | "ALTA";
export type FonteIA = "watsonx" | "local";

export interface Ferramenta {
  nome: string;
  resumo: string;
}

export interface Relatorio {
  parecer: ParecerIA;
  risco_ia: RiscoIA | null;
  confianca: Confianca;
  explicacao: string;
  evidencias_a_favor: string[];
  evidencias_contra: string[];
  dados_ausentes: string[];
  ferramentas_usadas: Ferramenta[];
  fonte: FonteIA;
  modelo: string;
}

export interface Auditoria {
  id_auditoria: string;
  status: "pendente" | "concluida" | "erro";
  relatorio: Relatorio | null;
  latencia_ms: number | null;
  mensagem: string | null;
}

// --- Corpo de entrada do POST /api/analisar ---

export interface EntradaAnalisar {
  valor?: number | null;
  hora?: number | null;
  madrugada?: number | null;
  credito?: number | null;
  nao_presente?: number | null;
  ip_pais_desconhecido?: number | null;
  vel_cartao_terminal_1h?: number | null;
  qtd_transacoes_cartao_1min?: number | null;
  qtd_token_carteira_3m?: number | null;
  dist_terminal_anterior_km?: number | null;
  risco_estabelecimento?: number | null;
  data_hora?: string | null;
  tipo_transacao?: string | null;
  modalidade_transacao?: string | null;
  auditar?: boolean;
}

// --- Seção 15: Canal do associado ---

export type StatusNotificacao = "aguardando" | "confirmada" | "negada";
export type TipoNotificacao = "CONFIRMACAO" | "AVISO_BLOQUEIO";
export type FonteMensagem = "watsonx" | "modelo";

export interface Notificacao {
  id_notificacao: string;
  id_transacao: number | null;
  tipo: TipoNotificacao;
  mensagem: string;
  fonte_mensagem: FonteMensagem;
  criada_em: string;
  status: StatusNotificacao;
  respondida_em: string | null;
  resultado: string | null;
}

export interface RespostaNotificacoes {
  itens: Notificacao[];
}

export interface EntradaRespostaNotificacao {
  resposta: "sim" | "nao";
}

// --- Corpo de entrada do POST /api/respostas ---

export interface EntradaResposta {
  id_transacao: number;
  resposta: "fraude" | "legitima";
}
