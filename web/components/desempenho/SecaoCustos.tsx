"use client";

/**
 * "Valor protegido em março" (Issue #42): quanto as fraudes bloqueadas somam, quanto custam os
 * pedidos de confirmação e o valor líquido, lidos de modelos/custos.json. Se algum campo faltar,
 * a seção não aparece.
 */

import { Tile } from "@carbon/react";
import { formatarMoeda } from "@/lib/formatacao";
import { ROTULOS_CUSTOS, TITULO_CUSTOS } from "@/lib/textos";

function numero(valor: unknown): number | null {
  return typeof valor === "number" && Number.isFinite(valor) ? valor : null;
}

function campo(bloco: unknown, nome: string): number | null {
  if (typeof bloco !== "object" || bloco === null) return null;
  return numero((bloco as Record<string, unknown>)[nome]);
}

interface PropsSecaoCustos {
  custos: Record<string, unknown>;
}

export default function SecaoCustos({ custos }: PropsSecaoCustos) {
  const barrado = campo(custos.sentinela, "valor_fraudes_bloqueadas");
  const confirmacoes = campo(custos.sentinela, "custo_confirmacoes");
  const liquido = numero(custos.valor_liquido_protegido);
  if (barrado === null || confirmacoes === null || liquido === null)
    return null;

  const itens = [
    { rotulo: ROTULOS_CUSTOS.barrado, valor: barrado },
    { rotulo: ROTULOS_CUSTOS.confirmacoes, valor: confirmacoes },
    { rotulo: ROTULOS_CUSTOS.liquido, valor: liquido },
  ];
  return (
    <section aria-labelledby="titulo-custos">
      <h2 id="titulo-custos" className="sentinela-secao">
        {TITULO_CUSTOS}
      </h2>
      <dl className="sentinela-indicadores sentinela-indicadores-3">
        {itens.map((item) => (
          <Tile key={item.rotulo} className="sentinela-indicador">
            <dt>{item.rotulo}</dt>
            <dd>{formatarMoeda(item.valor)}</dd>
          </Tile>
        ))}
      </dl>
    </section>
  );
}
