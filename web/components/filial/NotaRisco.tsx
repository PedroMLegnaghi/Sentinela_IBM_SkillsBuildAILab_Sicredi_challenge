/**
 * Nota de risco em destaque, com cor pela faixa (Issue #97).
 */

import { formatarNota } from "@/lib/formatacao";

/** Faixa da nota: alta a partir de 70, média a partir de 30 (cortes do agente). */
export function faixaDaNota(nota: number): "alta" | "media" | "baixa" {
  if (nota >= 70) return "alta";
  if (nota >= 30) return "media";
  return "baixa";
}

export default function NotaRisco({ nota }: { nota: number }) {
  return <span className={`sc-nota sc-nota--${faixaDaNota(nota)} sc-num`}>{formatarNota(nota)}</span>;
}
