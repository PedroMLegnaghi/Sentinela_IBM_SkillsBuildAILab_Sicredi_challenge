/**
 * Etiqueta da situação de uma compra (Issue #93): texto e cor, nunca só a cor.
 */

import type { SituacaoCompra } from "@/lib/tipos";
import { ROTULOS_SITUACAO } from "@/lib/textos";

const CLASSES: Record<SituacaoCompra, string> = {
  APROVADA: "sc-etiqueta--ok",
  AGUARDANDO: "sc-etiqueta--espera",
  BLOQUEADA: "sc-etiqueta--bloqueio",
  CONTESTADA: "sc-etiqueta--bloqueio",
};

export default function EtiquetaSituacao({ situacao }: { situacao: SituacaoCompra }) {
  return <span className={`sc-etiqueta ${CLASSES[situacao]}`}>{ROTULOS_SITUACAO[situacao]}</span>;
}
