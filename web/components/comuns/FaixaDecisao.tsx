"use client";

/**
 * Exibe a decisão do agente com ícone, cor e texto legível.
 * Nunca depende só de cor: sempre mostra ícone e texto (WCAG 1.4.1).
 */

import { InlineNotification } from "@carbon/react";
import type { Decisao } from "@/lib/tipos";
import { ROTULOS_DECISAO } from "@/lib/textos";

interface PropsFaixaDecisao {
  decisao: Decisao;
  decisaoLegivel?: string;
}

const CONFIG_DECISAO: Record<
  Decisao,
  { kind: "error" | "warning" | "success"; icone: string }
> = {
  BLOQUEAR: { kind: "error", icone: "⛔" },
  PEDIR_CONFIRMACAO: { kind: "warning", icone: "⚠️" },
  APROVAR: { kind: "success", icone: "✅" },
};

export default function FaixaDecisao({
  decisao,
  decisaoLegivel,
}: PropsFaixaDecisao) {
  const { kind, icone } = CONFIG_DECISAO[decisao];
  const texto = decisaoLegivel ?? ROTULOS_DECISAO[decisao] ?? decisao;

  return (
    <InlineNotification
      kind={kind}
      title=""
      subtitle={`${icone} ${texto}`}
      hideCloseButton
      role="status"
      aria-label={`Decisão: ${texto}`}
    />
  );
}
