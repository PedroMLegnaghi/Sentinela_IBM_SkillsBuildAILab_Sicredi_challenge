/**
 * Situação da compra na visão da filial (Issue #97).
 */

import type { SituacaoCompra } from "@/lib/tipos";
import { ROTULOS_SITUACAO_FILIAL } from "@/lib/textos";

const CLASSES: Record<SituacaoCompra, string> = {
  APROVADA: "sc-etiqueta--ok",
  AGUARDANDO: "sc-etiqueta--espera",
  BLOQUEADA: "sc-etiqueta--bloqueio",
  CONTESTADA: "sc-etiqueta--bloqueio",
};

export default function EtiquetaSituacaoFilial({ situacao }: { situacao: SituacaoCompra }) {
  return <span className={`sc-etiqueta ${CLASSES[situacao]}`}>{ROTULOS_SITUACAO_FILIAL[situacao]}</span>;
}
