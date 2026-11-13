"use client";

/**
 * Uma coluna de resultado do simulador: decisão, nota e sinais de uma análise.
 */

import { Tile } from "@carbon/react";
import BarraNota from "@/components/comuns/BarraNota";
import FaixaDecisao from "@/components/comuns/FaixaDecisao";
import { formatarDecimal } from "@/lib/formatacao";
import { LEGENDA_LATENCIA, SEM_SINAIS, TITULO_SINAIS } from "@/lib/textos";
import type { Analise } from "@/lib/tipos";

interface PropsResultadoAnalise {
  titulo: string;
  analise: Analise;
}

export default function ResultadoAnalise({
  titulo,
  analise,
}: PropsResultadoAnalise) {
  return (
    <Tile className="sentinela-resultado" aria-label={titulo}>
      <h2 className="sentinela-subtitulo">{titulo}</h2>
      <FaixaDecisao
        decisao={analise.decisao}
        decisaoLegivel={analise.decisao_legivel}
      />
      <BarraNota nota={analise.nota} />
      <p className="sentinela-legenda">
        {LEGENDA_LATENCIA(formatarDecimal(analise.latencia_ms, 1))}
      </p>
      <h3 className="sentinela-rotulo">
        {TITULO_SINAIS(analise.sinais.length)}
      </h3>
      {analise.sinais.length === 0 ? (
        <p>{SEM_SINAIS}</p>
      ) : (
        <ul className="sentinela-lista">
          {analise.sinais.map((sinal) => (
            <li key={sinal.id}>{sinal.descricao}</li>
          ))}
        </ul>
      )}
    </Tile>
  );
}
