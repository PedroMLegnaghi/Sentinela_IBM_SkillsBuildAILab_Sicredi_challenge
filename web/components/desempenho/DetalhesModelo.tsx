"use client";

/**
 * Detalhes do modelo: PR-AUC, ROC-AUC, tabela das notas de corte e a comparação com o
 * gradient boosting.
 */

import { Accordion, AccordionItem } from "@carbon/react";
import {
  formatarDecimal,
  formatarInteiro,
  formatarPercentual,
} from "@/lib/formatacao";
import {
  COLUNAS_LIMIARES,
  COMPARACAO_HGB,
  LEGENDA_DETALHES_MODELO,
  TITULO_DETALHES_MODELO,
} from "@/lib/textos";
import type { Metricas } from "@/lib/tipos";

interface PropsDetalhesModelo {
  metricas: Metricas;
}

export default function DetalhesModelo({ metricas }: PropsDetalhesModelo) {
  return (
    <Accordion>
      <AccordionItem title={TITULO_DETALHES_MODELO}>
        <p className="sentinela-legenda">
          {LEGENDA_DETALHES_MODELO(
            formatarInteiro(metricas.treino.linhas),
            formatarInteiro(metricas.treino.fraudes),
          )}
        </p>
        <dl className="sentinela-indicadores sentinela-indicadores-2">
          <div className="sentinela-indicador">
            <dt>PR-AUC</dt>
            <dd>{formatarDecimal(metricas.pr_auc, 3)}</dd>
          </div>
          <div className="sentinela-indicador">
            <dt>ROC-AUC</dt>
            <dd>{formatarDecimal(metricas.roc_auc, 3)}</dd>
          </div>
        </dl>
        <table className="cds--data-table cds--data-table--sm">
          <thead>
            <tr>
              {Object.values(COLUNAS_LIMIARES).map((coluna) => (
                <th key={coluna} scope="col">
                  {coluna}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {metricas.limiares.map((linha) => (
              <tr key={linha.limiar}>
                <td>{linha.limiar}</td>
                <td>{formatarInteiro(linha.alertas)}</td>
                <td>{formatarInteiro(linha.fraudes_detectadas)}</td>
                <td>{formatarPercentual(linha.precisao)}</td>
                <td>{formatarPercentual(linha.recall)}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {metricas.comparacao_hgb && (
          <p className="sentinela-legenda">
            {COMPARACAO_HGB(formatarDecimal(metricas.comparacao_hgb.pr_auc, 3))}
          </p>
        )}
      </AccordionItem>
    </Accordion>
  );
}
