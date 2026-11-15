"use client";

/**
 * Barras de fraudes bloqueadas (Sentinela × sistema atual) e a tabela de comparação.
 */

import { formatarInteiro, formatarPercentual } from "@/lib/formatacao";
import {
  COLUNAS_COMPARACAO,
  DE_TOTAL,
  LINHAS_COMPARACAO,
  ROTULO_SENTINELA,
  ROTULO_SISTEMA_ATUAL,
  TITULO_COMPARACAO,
  TITULO_GRAFICO_FRAUDES,
} from "@/lib/textos";
import type { AvaliacaoAgente } from "@/lib/tipos";

interface PropsComparacaoSistemas {
  avaliacao: AvaliacaoAgente;
}

export default function ComparacaoSistemas({
  avaliacao,
}: PropsComparacaoSistemas) {
  const { sentinela, sistema_atual: atual, fraudes_total: total } = avaliacao;
  const barras = [
    {
      rotulo: ROTULO_SENTINELA,
      valor: sentinela.fraudes_bloqueadas,
      classe: "sentinela-barra-modelo",
    },
    {
      rotulo: ROTULO_SISTEMA_ATUAL,
      valor: atual.fraudes_bloqueadas,
      classe: "sentinela-barra-atual",
    },
  ];
  const linhas = [
    [
      LINHAS_COMPARACAO.bloqueadas,
      DE_TOTAL(
        formatarInteiro(atual.fraudes_bloqueadas),
        formatarInteiro(total),
      ),
      DE_TOTAL(
        formatarInteiro(sentinela.fraudes_bloqueadas),
        formatarInteiro(total),
      ),
    ],
    [
      LINHAS_COMPARACAO.naoBloqueadas,
      formatarInteiro(atual.fraudes_nao_bloqueadas),
      formatarInteiro(total - sentinela.fraudes_bloqueadas),
    ],
    [
      LINHAS_COMPARACAO.percentual,
      formatarPercentual(atual.fraudes_bloqueadas / total),
      formatarPercentual(sentinela.fraudes_bloqueadas / total),
    ],
    [
      LINHAS_COMPARACAO.legitimas,
      "—",
      formatarInteiro(sentinela.bloqueadas - sentinela.fraudes_bloqueadas),
    ],
  ];

  return (
    <section aria-labelledby="titulo-grafico-fraudes">
      <h2 id="titulo-grafico-fraudes" className="sentinela-secao">
        {TITULO_GRAFICO_FRAUDES}
      </h2>
      <ul className="sentinela-barras">
        {barras.map((barra) => (
          <li
            key={barra.rotulo}
            aria-label={`${barra.rotulo}: ${DE_TOTAL(formatarInteiro(barra.valor), formatarInteiro(total))}`}
          >
            <span aria-hidden="true">{barra.rotulo}</span>
            <span className="sentinela-barras-trilho" aria-hidden="true">
              <span
                className={barra.classe}
                style={{ width: `${(barra.valor / total) * 100}%` }}
              />
            </span>
            <strong aria-hidden="true">
              {DE_TOTAL(formatarInteiro(barra.valor), formatarInteiro(total))}
            </strong>
          </li>
        ))}
      </ul>
      <h2 className="sentinela-secao">{TITULO_COMPARACAO}</h2>
      <table className="cds--data-table cds--data-table--sm">
        <thead>
          <tr>
            {Object.values(COLUNAS_COMPARACAO).map((coluna) => (
              <th key={coluna} scope="col">
                {coluna}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {linhas.map(([indicador, valorAtual, valorSentinela]) => (
            <tr key={indicador}>
              <th scope="row">{indicador}</th>
              <td>{valorAtual}</td>
              <td>{valorSentinela}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
