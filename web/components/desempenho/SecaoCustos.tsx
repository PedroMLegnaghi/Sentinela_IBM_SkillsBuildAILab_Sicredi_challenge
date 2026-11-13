"use client";

/**
 * "Custo da fraude em março" (Issue #42): prejuízo evitado e custo de cada sistema, em reais.
 * Lê os campos da backlog (#20): prejuizo_evitado, sentinela.custo_total e
 * sistema_atual.custo_total. Se algum faltar, a seção não aparece.
 */

import { Tile } from "@carbon/react";
import { formatarMoeda } from "@/lib/formatacao";
import { ROTULOS_CUSTOS, TITULO_CUSTOS } from "@/lib/textos";

function numero(valor: unknown): number | null {
  return typeof valor === "number" && Number.isFinite(valor) ? valor : null;
}

function custoTotal(bloco: unknown): number | null {
  if (typeof bloco !== "object" || bloco === null) return null;
  return numero((bloco as Record<string, unknown>).custo_total);
}

interface PropsSecaoCustos {
  custos: Record<string, unknown>;
}

export default function SecaoCustos({ custos }: PropsSecaoCustos) {
  const evitado = numero(custos.prejuizo_evitado);
  const sentinela = custoTotal(custos.sentinela);
  const atual = custoTotal(custos.sistema_atual);
  if (evitado === null || sentinela === null || atual === null) return null;

  const itens = [
    { rotulo: ROTULOS_CUSTOS.evitado, valor: evitado },
    { rotulo: ROTULOS_CUSTOS.sentinela, valor: sentinela },
    { rotulo: ROTULOS_CUSTOS.sistemaAtual, valor: atual },
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
