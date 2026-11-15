"use client";

/**
 * Os quatro indicadores de março: fraudes, fraudes bloqueadas pelo Sentinela, compras legítimas
 * bloqueadas e pedidos de confirmação.
 */

import { Tile } from "@carbon/react";
import { formatarInteiro, formatarPercentual } from "@/lib/formatacao";
import {
  AJUDA_CONFIRMACOES,
  AJUDA_SENTINELA,
  DE_TOTAL,
  INDICADORES_DESEMPENHO,
} from "@/lib/textos";
import type { AvaliacaoAgente } from "@/lib/tipos";

interface PropsIndicadoresDesempenho {
  avaliacao: AvaliacaoAgente;
}

export default function IndicadoresDesempenho({
  avaliacao,
}: PropsIndicadoresDesempenho) {
  const { sentinela, fraudes_total: total } = avaliacao;
  const legitimasBloqueadas =
    sentinela.bloqueadas - sentinela.fraudes_bloqueadas;
  const itens = [
    { rotulo: INDICADORES_DESEMPENHO.fraudes, valor: formatarInteiro(total) },
    {
      rotulo: INDICADORES_DESEMPENHO.sentinela,
      valor: DE_TOTAL(
        formatarInteiro(sentinela.fraudes_bloqueadas),
        formatarInteiro(total),
      ),
      nota: AJUDA_SENTINELA,
    },
    {
      rotulo: INDICADORES_DESEMPENHO.legitimas,
      valor: formatarInteiro(legitimasBloqueadas),
    },
    {
      rotulo: INDICADORES_DESEMPENHO.confirmacoes,
      valor: formatarInteiro(sentinela.confirmacoes),
      nota: AJUDA_CONFIRMACOES(
        formatarPercentual(sentinela.confirmacoes / avaliacao.transacoes),
      ),
    },
  ];

  return (
    <dl className="sentinela-indicadores sentinela-indicadores-4">
      {itens.map((item) => (
        <Tile key={item.rotulo} className="sentinela-indicador">
          <dt>{item.rotulo}</dt>
          <dd>{item.valor}</dd>
          {item.nota && (
            <dd className="sentinela-indicador-nota">{item.nota}</dd>
          )}
        </Tile>
      ))}
    </dl>
  );
}
