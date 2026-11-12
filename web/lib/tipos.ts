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

export interface RespostaTransacao {
  transacao: Transacao;
  analise: Analise;
  historico: ItemHistorico[];
  resposta_analista: Resposta | null;
}

export interface RespostaAnalisar {
  analise: Analise;
  id_auditoria: string | null;
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

export interface RespostaMetricas {
  metricas: Record<string, unknown>;
  avaliacao: Record<string, unknown>;
  extras: {
    avaliacao_rigorosa: Record<string, unknown> | null;
    custos: Record<string, unknown> | null;
    eda: Record<string, unknown> | null;
    ia_contra_modelo: Record<string, unknown> | null;
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

// --- Corpo de entrada do POST /api/respostas ---

export interface EntradaResposta {
  id_transacao: number;
  resposta: "fraude" | "legitima";
}
