/**
 * Lógica pura do simulador "e se" (Issue #45), dos cenários prontos (Issue #110) e da
 * exportação de respostas.
 */

import type {
  EntradaAnalisar,
  RespostaRespostas,
  Transacao,
} from "@/lib/tipos";
import { TEXTOS_CENARIOS } from "@/lib/textos";

/** Hora de corte da madrugada (src/config.py, HORA_FIM_MADRUGADA). */
export const HORA_FIM_MADRUGADA = 5;

/** Campos que o analista pode mudar no simulador. */
export interface ValoresSimulador {
  valor: number;
  hora: number;
  credito: boolean;
  nao_presente: boolean;
  ip_pais_desconhecido: boolean;
  qtd_transacoes_cartao_1min: number;
  vel_cartao_terminal_1h: number;
  qtd_token_carteira_3m: number;
  dist_terminal_anterior_km: number;
  risco_estabelecimento: number;
}

/** Cenário pronto: preenche todos os campos do simulador de uma vez. */
export interface Cenario {
  id: string;
  nome: string;
  frase: string;
  valores: ValoresSimulador;
}

/** Cenários da demonstração. Ajuste os números com a API real (decisão esperada ao lado). */
export const CENARIOS: Cenario[] = [
  {
    // Esperado: APROVAR
    id: "comum",
    ...TEXTOS_CENARIOS.comum,
    valores: {
      valor: 85.9,
      hora: 15,
      credito: false,
      nao_presente: false,
      ip_pais_desconhecido: false,
      qtd_transacoes_cartao_1min: 0,
      vel_cartao_terminal_1h: 0,
      qtd_token_carteira_3m: 0,
      dist_terminal_anterior_km: 0,
      risco_estabelecimento: 10,
    },
  },
  {
    // Esperado: PEDIR_CONFIRMACAO ou BLOQUEAR
    id: "exterior",
    ...TEXTOS_CENARIOS.exterior,
    valores: {
      valor: 450,
      hora: 3,
      credito: true,
      nao_presente: true,
      ip_pais_desconhecido: true,
      qtd_transacoes_cartao_1min: 0,
      vel_cartao_terminal_1h: 0,
      qtd_token_carteira_3m: 0,
      dist_terminal_anterior_km: 0,
      risco_estabelecimento: 50,
    },
  },
  {
    // Esperado: BLOQUEAR
    id: "rajada",
    ...TEXTOS_CENARIOS.rajada,
    valores: {
      valor: 900,
      hora: 2,
      credito: true,
      nao_presente: true,
      ip_pais_desconhecido: true,
      qtd_transacoes_cartao_1min: 6,
      vel_cartao_terminal_1h: 8,
      qtd_token_carteira_3m: 3,
      dist_terminal_anterior_km: 300,
      risco_estabelecimento: 70,
    },
  },
];

const numero = (valor: number | null | undefined) => valor ?? 0;
const ligado = (valor: number | null | undefined) => valor === 1;

/** Valores iniciais do simulador a partir da transação original (vazio vira 0). */
export function valoresIniciais(transacao: Transacao): ValoresSimulador {
  return {
    valor: numero(transacao.valor),
    hora: Math.floor(numero(transacao.hora)),
    credito: ligado(transacao.credito),
    nao_presente: ligado(transacao.nao_presente),
    ip_pais_desconhecido: ligado(transacao.ip_pais_desconhecido),
    qtd_transacoes_cartao_1min: numero(transacao.qtd_transacoes_cartao_1min),
    vel_cartao_terminal_1h: numero(transacao.vel_cartao_terminal_1h),
    qtd_token_carteira_3m: numero(transacao.qtd_token_carteira_3m),
    dist_terminal_anterior_km: numero(transacao.dist_terminal_anterior_km),
    risco_estabelecimento: numero(transacao.risco_estabelecimento),
  };
}

/** A madrugada vem da hora; nunca é editada à mão. */
export function ehMadrugada(hora: number): boolean {
  return hora < HORA_FIM_MADRUGADA;
}

/** Monta o corpo do POST /api/analisar para a compra simulada. */
export function montarEntradaSimulada(
  original: Transacao,
  valores: ValoresSimulador,
): EntradaAnalisar {
  return {
    ...valores,
    credito: valores.credito ? 1 : 0,
    nao_presente: valores.nao_presente ? 1 : 0,
    ip_pais_desconhecido: valores.ip_pais_desconhecido ? 1 : 0,
    madrugada: ehMadrugada(valores.hora) ? 1 : 0,
    data_hora: original.data_hora,
    tipo_transacao: valores.credito ? "credito" : "debito",
    modalidade_transacao: valores.nao_presente
      ? "cartao_nao_presente"
      : "cartao_presente",
    auditar: true,
  };
}

const escapar = (campo: string | number) => {
  const texto = String(campo);
  return /[",\n]/.test(texto) ? `"${texto.replace(/"/g, '""')}"` : texto;
};

/** CSV das respostas do analista (separador vírgula, cabeçalho em português). */
export function gerarCsvRespostas(itens: RespostaRespostas["itens"]): string {
  const cabecalho = [
    "id_transacao",
    "resposta",
    "registrado_em",
    "decisao",
    "nota",
  ];
  const linhas = itens.map((i) =>
    [i.id_transacao, i.resposta, i.registrado_em, i.decisao, i.nota]
      .map(escapar)
      .join(","),
  );
  return [cabecalho.join(","), ...linhas].join("\n") + "\n";
}