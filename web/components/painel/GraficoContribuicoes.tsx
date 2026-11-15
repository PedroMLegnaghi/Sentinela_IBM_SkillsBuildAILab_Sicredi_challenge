"use client";

/**
 * Barras horizontais com as 6 variáveis que mais pesaram na nota (positivas aumentam o risco).
 */

import { formatarDecimal } from "@/lib/formatacao";
import {
  LEGENDA_CONTRIBUICOES,
  SEM_CONTRIBUICOES,
  TITULO_CONTRIBUICOES,
} from "@/lib/textos";
import type { Contribuicao } from "@/lib/tipos";

const MAXIMO_BARRAS = 6;

interface PropsGraficoContribuicoes {
  contribuicoes: Contribuicao[];
}

/** Gera texto alternativo completo para leitores de tela. */
function textoAlternativo(principais: Contribuicao[]): string {
  if (principais.length === 0) return "";
  return principais
    .map((c) => {
      const sinal = c.contribuicao >= 0 ? "aumentou o risco" : "reduziu o risco";
      return `${c.nome}: ${sinal} em ${formatarDecimal(Math.abs(c.contribuicao), 2)}`;
    })
    .join("; ");
}

export default function GraficoContribuicoes({
  contribuicoes,
}: PropsGraficoContribuicoes) {
  const principais = contribuicoes.slice(0, MAXIMO_BARRAS);
  const maior = Math.max(
    ...principais.map((c) => Math.abs(c.contribuicao)),
    1e-9,
  );

  return (
    <section aria-labelledby="titulo-contribuicoes">
      <h3 id="titulo-contribuicoes" className="sentinela-subtitulo">
        {TITULO_CONTRIBUICOES}
      </h3>
      {principais.length === 0 ? (
        <p className="sentinela-legenda">{SEM_CONTRIBUICOES}</p>
      ) : (
        <>
          {/* Resumo para leitores de tela; barras visuais são aria-hidden */}
          <p className="sentinela-sr-only">{textoAlternativo(principais)}</p>
          <ul className="sentinela-contribuicoes" aria-hidden="true">
            {principais.map((c) => {
              const largura = `${(Math.abs(c.contribuicao) / maior) * 50}%`;
              const positivo = c.contribuicao >= 0;
              return (
                <li key={c.variavel}>
                  <span className="sentinela-contribuicao-nome">{c.nome}</span>
                  <span className="sentinela-contribuicao-trilho">
                    <span
                      className={
                        positivo
                          ? "sentinela-barra-risco"
                          : "sentinela-barra-alivio"
                      }
                      style={
                        positivo
                          ? { left: "50%", width: largura }
                          : { right: "50%", width: largura }
                      }
                    />
                  </span>
                  <span className="sentinela-contribuicao-valor">
                    {positivo ? "+" : "−"}
                    {formatarDecimal(Math.abs(c.contribuicao), 2)}
                  </span>
                </li>
              );
            })}
          </ul>
          <p className="sentinela-legenda">{LEGENDA_CONTRIBUICOES}</p>
        </>
      )}
    </section>
  );
}
