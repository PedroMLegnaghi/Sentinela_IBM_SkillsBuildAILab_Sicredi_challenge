"use client";

/**
 * Histórico do cartão: até 10 compras anteriores, já formatadas em pt-BR.
 */

import { Accordion, AccordionItem } from "@carbon/react";
import {
  formatarDecimal,
  formatarDataHora,
  formatarModalidade,
  formatarMoeda,
  formatarTipo,
} from "@/lib/formatacao";
import {
  COLUNAS_HISTORICO,
  HISTORICO_VAZIO,
  TITULO_HISTORICO,
} from "@/lib/textos";
import type { ItemHistorico } from "@/lib/tipos";

interface PropsHistoricoCartao {
  historico: ItemHistorico[];
}

export default function HistoricoCartao({ historico }: PropsHistoricoCartao) {
  return (
    <Accordion>
      <AccordionItem title={TITULO_HISTORICO(historico.length)}>
        {historico.length === 0 ? (
          <p>{HISTORICO_VAZIO}</p>
        ) : (
          <div className="sentinela-tabela-rolagem">
            <table className="cds--data-table cds--data-table--xs">
              <thead>
                <tr>
                  {Object.values(COLUNAS_HISTORICO).map((coluna) => (
                    <th key={coluna} scope="col">
                      {coluna}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {historico.map((item, indice) => (
                  <tr key={`${item.data_hora}-${indice}`}>
                    <td>{formatarDataHora(item.data_hora)}</td>
                    <td>{formatarMoeda(item.valor)}</td>
                    <td>{formatarTipo(item.tipo_transacao)}</td>
                    <td>{formatarModalidade(item.modalidade_transacao)}</td>
                    <td>
                      {item.dist_terminal_anterior_km === null
                        ? "—"
                        : formatarDecimal(item.dist_terminal_anterior_km, 0)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </AccordionItem>
    </Accordion>
  );
}
