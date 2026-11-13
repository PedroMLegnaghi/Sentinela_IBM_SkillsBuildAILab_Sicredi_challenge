"use client";

/**
 * Filtro das decisões exibidas na tabela (padrão: Bloquear e Pedir confirmação).
 */

import { Checkbox, FormGroup } from "@carbon/react";
import { FILTRO_DECISOES, ROTULOS_CURTOS_DECISAO } from "@/lib/textos";
import type { Decisao } from "@/lib/tipos";

export const ORDEM_DECISOES: Decisao[] = [
  "BLOQUEAR",
  "PEDIR_CONFIRMACAO",
  "APROVAR",
];

interface PropsFiltroDecisoes {
  selecionadas: Decisao[];
  aoMudar: (selecionadas: Decisao[]) => void;
}

export default function FiltroDecisoes({
  selecionadas,
  aoMudar,
}: PropsFiltroDecisoes) {
  function alternar(decisao: Decisao, marcada: boolean) {
    const novas = marcada
      ? [...selecionadas, decisao]
      : selecionadas.filter((d) => d !== decisao);
    aoMudar(ORDEM_DECISOES.filter((d) => novas.includes(d)));
  }

  return (
    <FormGroup legendText={FILTRO_DECISOES} className="sentinela-filtro">
      {ORDEM_DECISOES.map((decisao) => (
        <Checkbox
          key={decisao}
          id={`filtro-${decisao}`}
          labelText={ROTULOS_CURTOS_DECISAO[decisao]}
          checked={selecionadas.includes(decisao)}
          onChange={(_evento, { checked }) => alternar(decisao, checked)}
        />
      ))}
    </FormGroup>
  );
}
