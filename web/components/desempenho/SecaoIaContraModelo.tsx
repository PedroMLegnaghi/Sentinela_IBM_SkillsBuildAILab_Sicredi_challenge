"use client";

/**
 * "Modelo e IA lado a lado" (Issue #46): latência e acerto de cada caminho e a concordância.
 * Só aparece quando modelos/ia_contra_modelo.json existe.
 */

import { formatarDecimal, formatarInteiro } from "@/lib/formatacao";
import {
  COLUNAS_IA_CONTRA_MODELO,
  CONCORDANCIA_IA,
  FONTES_IA,
  LEGENDA_IA_CONTRA_MODELO,
  LINHAS_IA_CONTRA_MODELO,
  TITULO_IA_CONTRA_MODELO,
} from "@/lib/textos";
import type { AcertoAlertas, IaContraModelo } from "@/lib/tipos";

const ms = (valor: number) => `${formatarDecimal(valor, 1)} ms`;
const pct = (valor: number | null) =>
  valor === null ? "—" : `${formatarDecimal(valor, 1)}%`;

function linhasAcerto(
  modelo: AcertoAlertas,
  ia: AcertoAlertas,
): Array<[string, string, string]> {
  return [
    [
      LINHAS_IA_CONTRA_MODELO.alertas,
      formatarInteiro(modelo.alertas),
      formatarInteiro(ia.alertas),
    ],
    [
      LINHAS_IA_CONTRA_MODELO.fraudes,
      formatarInteiro(modelo.fraudes_pegas),
      formatarInteiro(ia.fraudes_pegas),
    ],
    [LINHAS_IA_CONTRA_MODELO.precisao, pct(modelo.precisao), pct(ia.precisao)],
    [LINHAS_IA_CONTRA_MODELO.recall, pct(modelo.recall), pct(ia.recall)],
  ];
}

interface PropsSecaoIaContraModelo {
  dados: IaContraModelo;
}

export default function SecaoIaContraModelo({
  dados,
}: PropsSecaoIaContraModelo) {
  const linhas: Array<[string, string, string]> = [
    [
      LINHAS_IA_CONTRA_MODELO.latenciaP50,
      ms(dados.latencia_modelo.p50_ms),
      ms(dados.latencia_ia.p50_ms),
    ],
    [
      LINHAS_IA_CONTRA_MODELO.latenciaP95,
      ms(dados.latencia_modelo.p95_ms),
      ms(dados.latencia_ia.p95_ms),
    ],
    ...linhasAcerto(dados.modelo, dados.ia_sozinha),
  ];
  const confirmados = dados.pareceres.CONFIRMA ?? 0;
  const fontes = Object.entries(dados.fontes)
    .map(
      ([fonte, n]) =>
        `${fonte === "watsonx" ? "IBM watsonx.ai" : "modo local"} (${n})`,
    )
    .join(", ");

  return (
    <section aria-labelledby="titulo-ia-contra-modelo">
      <h2 id="titulo-ia-contra-modelo" className="sentinela-secao">
        {TITULO_IA_CONTRA_MODELO}
      </h2>
      <p className="sentinela-legenda">
        {LEGENDA_IA_CONTRA_MODELO(
          formatarInteiro(dados.transacoes),
          formatarInteiro(dados.fraudes),
        )}
      </p>
      <table className="cds--data-table cds--data-table--sm">
        <thead>
          <tr>
            {Object.values(COLUNAS_IA_CONTRA_MODELO).map((coluna) => (
              <th key={coluna} scope="col">
                {coluna}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {linhas.map(([medida, modelo, ia]) => (
            <tr key={medida}>
              <th scope="row">{medida}</th>
              <td>{modelo}</td>
              <td>{ia}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p>
        {CONCORDANCIA_IA(
          `${formatarInteiro(confirmados)} de ${formatarInteiro(dados.transacoes)}`,
        )}
      </p>
      <p className="sentinela-legenda">{FONTES_IA(fontes)}</p>
    </section>
  );
}
