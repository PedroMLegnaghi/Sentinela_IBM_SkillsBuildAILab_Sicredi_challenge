"use client";

/**
 * Os cinco indicadores de março: fraudes, bloqueios do Sentinela e do sistema atual,
 * compras legítimas bloqueadas e pedidos de confirmação.
 */

import { Tile } from "@carbon/react";
import { formatarInteiro, formatarPercentual } from "@/lib/formatacao";
import {
  AJUDA_CONFIRMACOES,
  DE_TOTAL,
  DELTA_SENTINELA,
  INDICADORES_DESEMPENHO,
} from "@/lib/textos";
import type { AvaliacaoAgente } from "@/lib/tipos";

interface PropsIndicadoresDesempenho {
  avaliacao: AvaliacaoAgente;
}

export default function IndicadoresDesempenho({
  avaliacao,
}: PropsIndicadoresDesempenho) {
  const { sentinela, sistema_atual: atual, fraudes_total: total } = avaliacao;
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
      nota: DELTA_SENTINELA(
        sentinela.fraudes_bloqueadas - atual.fraudes_bloqueadas,
      ),
    },
    {
      rotulo: INDICADORES_DESEMPENHO.sistemaAtual,
      valor: DE_TOTAL(
        formatarInteiro(atual.fraudes_bloqueadas),
        formatarInteiro(total),
      ),
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
    <dl className="sentinela-indicadores sentinela-indicadores-5">
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
