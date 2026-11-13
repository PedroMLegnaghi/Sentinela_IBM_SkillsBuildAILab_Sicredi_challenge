/**
 * Lógica pura do simulador "e se" (Issue #45) e da exportação de respostas.
 */

import type {
  EntradaAnalisar,
  RespostaRespostas,
  Transacao,
} from "@/lib/tipos";

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
