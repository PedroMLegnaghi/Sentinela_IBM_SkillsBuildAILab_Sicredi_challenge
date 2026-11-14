/**
 * Lógica pura da compra simulada pelo associado (ESPECIFICACAO, seção 17; Issue #95).
 * Os cenários foram conferidos com o modelo real: "Compra comum" aprova, "Madrugada online"
 * pede confirmação e "Várias seguidas" bloqueia.
 */

import type { EntradaCompra, TipoCartao } from "@/lib/tipos";
import { HORA_FIM_MADRUGADA } from "@/lib/simulacao";

/** Data das compras simuladas: o último dia da base (ESPECIFICACAO, seção 17.4). */
export const DATA_SIMULADA = "2025-03-31";

/** Estabelecimentos fictícios e o risco de cada um (0 a 100). */
export const ESTABELECIMENTOS: { nome: string; risco: number }[] = [
  { nome: "Mercado Bom Preço", risco: 5 },
  { nome: "Farmácia Vida", risco: 5 },
  { nome: "Posto Avenida", risco: 10 },
  { nome: "Restaurante Sabor", risco: 15 },
  { nome: "Loja online", risco: 45 },
  { nome: "Eletrônicos Web", risco: 70 },
];

export interface ValoresCompra {
  tipoCartao: TipoCartao;
  valor: number;
  hora: number;
  estabelecimento: string;
  nao_presente: boolean;
  ip_pais_desconhecido: boolean;
  qtd_transacoes_cartao_1min: number;
  vel_cartao_terminal_1h: number;
  qtd_token_carteira_3m: number;
  dist_terminal_anterior_km: number;
}

export interface Cenario {
  id: string;
  nome: string;
  descricao: string;
  valores: ValoresCompra;
}

export const CENARIOS: Cenario[] = [
  {
    id: "comum",
    nome: "Compra comum",
    descricao: "Mercado no fim da tarde, no débito, com o cartão na mão.",
    valores: {
      tipoCartao: "debito",
      valor: 86.4,
      hora: 18,
      estabelecimento: "Mercado Bom Preço",
      nao_presente: false,
      ip_pais_desconhecido: false,
      qtd_transacoes_cartao_1min: 0,
      vel_cartao_terminal_1h: 1,
      qtd_token_carteira_3m: 0,
      dist_terminal_anterior_km: 2,
    },
  },
  {
    id: "madrugada",
    nome: "Madrugada online",
    descricao: "Compra alta pela internet, às 3h, no crédito.",
    valores: {
      tipoCartao: "credito",
      valor: 980,
      hora: 3,
      estabelecimento: "Loja online",
      nao_presente: true,
      ip_pais_desconhecido: false,
      qtd_transacoes_cartao_1min: 0,
      vel_cartao_terminal_1h: 1,
      qtd_token_carteira_3m: 0,
      dist_terminal_anterior_km: 0,
    },
  },
  {
    id: "sequencia",
    nome: "Várias seguidas",
    descricao: "Rajada de compras de madrugada, de um país desconhecido.",
    valores: {
      tipoCartao: "credito",
      valor: 450,
      hora: 2,
      estabelecimento: "Eletrônicos Web",
      nao_presente: true,
      ip_pais_desconhecido: true,
      qtd_transacoes_cartao_1min: 6,
      vel_cartao_terminal_1h: 12,
      qtd_token_carteira_3m: 30,
      dist_terminal_anterior_km: 300,
    },
  },
];

/** Risco de um estabelecimento da lista (desconhecido vale 50). */
export function riscoDoEstabelecimento(nome: string): number {
  return ESTABELECIMENTOS.find((e) => e.nome === nome)?.risco ?? 50;
}

/** Monta o corpo de POST /api/associado/compras. */
export function montarEntradaCompra(valores: ValoresCompra, idCartao: string): EntradaCompra {
  const hora = Math.min(23, Math.max(0, Math.floor(valores.hora)));
  return {
    cartao: idCartao,
    estabelecimento: valores.estabelecimento,
    data_hora: `${DATA_SIMULADA}T${String(hora).padStart(2, "0")}:00:00`,
    valor: valores.valor,
    hora,
    madrugada: hora < HORA_FIM_MADRUGADA ? 1 : 0,
    nao_presente: valores.nao_presente ? 1 : 0,
    ip_pais_desconhecido: valores.ip_pais_desconhecido ? 1 : 0,
    qtd_transacoes_cartao_1min: valores.qtd_transacoes_cartao_1min,
    vel_cartao_terminal_1h: valores.vel_cartao_terminal_1h,
    qtd_token_carteira_3m: valores.qtd_token_carteira_3m,
    dist_terminal_anterior_km: valores.dist_terminal_anterior_km,
    risco_estabelecimento: riscoDoEstabelecimento(valores.estabelecimento),
    modalidade_transacao: valores.nao_presente ? "cartao_nao_presente" : "cartao_presente",
  };
}
