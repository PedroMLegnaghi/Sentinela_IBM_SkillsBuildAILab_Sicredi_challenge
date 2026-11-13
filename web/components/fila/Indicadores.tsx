"use client";

/**
 * Quatro indicadores da fila inteira (não mudam com o filtro).
 */

import { Tile } from "@carbon/react";
import { formatarInteiro } from "@/lib/formatacao";
import { INDICADOR_NA_FILA, ROTULOS_CURTOS_DECISAO } from "@/lib/textos";
import type { RespostaFila } from "@/lib/tipos";

interface PropsIndicadores {
  fila: RespostaFila;
}

export default function Indicadores({ fila }: PropsIndicadores) {
  const itens = [
    { rotulo: INDICADOR_NA_FILA, valor: fila.total_fila },
    { rotulo: ROTULOS_CURTOS_DECISAO.BLOQUEAR, valor: fila.contagens.BLOQUEAR },
    {
      rotulo: ROTULOS_CURTOS_DECISAO.PEDIR_CONFIRMACAO,
      valor: fila.contagens.PEDIR_CONFIRMACAO,
    },
    { rotulo: ROTULOS_CURTOS_DECISAO.APROVAR, valor: fila.contagens.APROVAR },
  ];

  return (
    <dl className="sentinela-indicadores">
      {itens.map((item) => (
        <Tile key={item.rotulo} className="sentinela-indicador">
          <dt>{item.rotulo}</dt>
          <dd>{formatarInteiro(item.valor)}</dd>
        </Tile>
      ))}
    </dl>
  );
}
