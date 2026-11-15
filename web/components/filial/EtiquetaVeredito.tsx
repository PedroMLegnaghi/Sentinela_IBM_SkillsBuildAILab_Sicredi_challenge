/**
 * Etiqueta do parecer da IA na fila da filial (Issue #97).
 */

import type { ParecerIA } from "@/lib/tipos";
import { ROTULOS_VEREDITO, SEM_VEREDITO } from "@/lib/textos";

const CLASSES: Record<ParecerIA, string> = {
  CONFIRMA: "sc-etiqueta--ok",
  DIVERGE: "sc-etiqueta--espera",
  INCONCLUSIVO: "sc-etiqueta--neutra",
};

export default function EtiquetaVeredito({ veredito }: { veredito: ParecerIA | null }) {
  if (!veredito) return <span className="sc-apoio">{SEM_VEREDITO}</span>;
  return <span className={`sc-etiqueta ${CLASSES[veredito]}`}>{ROTULOS_VEREDITO[veredito]}</span>;
}
