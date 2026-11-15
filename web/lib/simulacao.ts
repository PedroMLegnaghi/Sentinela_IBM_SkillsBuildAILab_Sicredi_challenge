/**
 * Regras de horário compartilhadas pela compra simulada (Issues #45 e #95).
 */

/** Hora de corte da madrugada (src/config.py, HORA_FIM_MADRUGADA). */
export const HORA_FIM_MADRUGADA = 5;

/** A madrugada vem da hora; nunca é editada à mão. */
export function ehMadrugada(hora: number): boolean {
  return hora < HORA_FIM_MADRUGADA;
}
