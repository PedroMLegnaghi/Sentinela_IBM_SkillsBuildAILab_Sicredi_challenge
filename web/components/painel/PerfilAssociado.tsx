"use client";

/**
 * Cartão "O normal deste associado" — Issue #64.
 * Exibe o perfil calculado com as compras anteriores do mesmo cliente.
 */

import { Accordion, AccordionItem, Tag } from "@carbon/react";
import { formatarDecimal, formatarMoeda } from "@/lib/formatacao";
import {
  TITULO_PERFIL_ASSOCIADO,
  PERFIL_SEM_HISTORICO,
  PERFIL_COMPRAS_ANTERIORES,
  PERFIL_MEDIANA_VALOR,
  PERFIL_RAZAO_MEDIANA,
  PERFIL_RAZAO_ALTA,
  PERFIL_HORA_MAIS_COMUM,
  PERFIL_PERCENTUAL_MADRUGADA,
  PERFIL_CREDITO_NAO_PRESENTE,
} from "@/lib/textos";
import type { PerfilAssociado as TPerfilAssociado } from "@/lib/tipos";

interface PropsPerfilAssociado {
  perfil: TPerfilAssociado | null;
}

export default function PerfilAssociado({ perfil }: PropsPerfilAssociado) {
  return (
    <Accordion>
      <AccordionItem title={TITULO_PERFIL_ASSOCIADO}>
        {!perfil ? (
          <p>{PERFIL_SEM_HISTORICO}</p>
        ) : (
          <ul className="sentinela-lista">
            <li>{PERFIL_COMPRAS_ANTERIORES(perfil.compras_anteriores)}</li>
            {perfil.mediana_valor !== null && (
              <li>{PERFIL_MEDIANA_VALOR(formatarMoeda(perfil.mediana_valor))}</li>
            )}
            {perfil.valor_atual_sobre_mediana !== null && (
              <li>
                {perfil.valor_atual_sobre_mediana >= 3 ? (
                  <Tag type="red">{PERFIL_RAZAO_ALTA}</Tag>
                ) : (
                  PERFIL_RAZAO_MEDIANA(
                    formatarDecimal(perfil.valor_atual_sobre_mediana, 1),
                  )
                )}
              </li>
            )}
            {perfil.hora_mais_comum !== null && (
              <li>{PERFIL_HORA_MAIS_COMUM(perfil.hora_mais_comum)}</li>
            )}
            {perfil.percentual_madrugada !== null && (
              <li>
                {PERFIL_PERCENTUAL_MADRUGADA(
                  formatarDecimal(perfil.percentual_madrugada, 1),
                )}
              </li>
            )}
            {perfil.percentual_credito_nao_presente !== null && (
              <li>
                {PERFIL_CREDITO_NAO_PRESENTE(
                  formatarDecimal(perfil.percentual_credito_nao_presente, 1),
                )}
              </li>
            )}
          </ul>
        )}
      </AccordionItem>
    </Accordion>
  );
}
