/**
 * Página "Como funciona": o caminho de uma compra, os 9 sinais, as regras de decisão, como a
 * IA audita, os dados e as limitações. Conteúdo estático (sem chamada à API).
 */

import { Heading } from "@carbon/react";
import {
  COLUNAS_SINAIS,
  IA_COMO,
  LEAD_COMO,
  LIMITACOES,
  PASSOS_CAMINHO,
  REGRAS_DECISAO,
  SINAIS_EXPLICADOS,
  SOBRE_DADOS,
  TITULO_CAMINHO,
  TITULO_COMO,
  TITULO_DADOS_COMO,
  TITULO_DECISAO_COMO,
  TITULO_IA_COMO,
  TITULO_LIMITACOES,
  TITULO_SINAIS_COMO,
} from "@/lib/textos";

function Lista({
  itens,
  ordenada = false,
}: {
  itens: string[];
  ordenada?: boolean;
}) {
  const Elemento = ordenada ? "ol" : "ul";
  return (
    <Elemento className="sentinela-lista">
      {itens.map((item) => (
        <li key={item}>{item}</li>
      ))}
    </Elemento>
  );
}

export default function PaginaComoFunciona() {
  return (
    <div className="sentinela-pagina sentinela-leitura">
      <Heading>{TITULO_COMO}</Heading>
      <p className="sentinela-lead">{LEAD_COMO}</p>

      <h2 className="sentinela-secao">{TITULO_CAMINHO}</h2>
      <Lista itens={PASSOS_CAMINHO} ordenada />

      <h2 className="sentinela-secao">{TITULO_SINAIS_COMO}</h2>
      <table className="cds--data-table cds--data-table--sm">
        <thead>
          <tr>
            <th scope="col">{COLUNAS_SINAIS.sinal}</th>
            <th scope="col">{COLUNAS_SINAIS.quando}</th>
          </tr>
        </thead>
        <tbody>
          {SINAIS_EXPLICADOS.map(([sinal, quando]) => (
            <tr key={sinal}>
              <th scope="row">{sinal}</th>
              <td>{quando}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2 className="sentinela-secao">{TITULO_DECISAO_COMO}</h2>
      <Lista itens={REGRAS_DECISAO} />

      <h2 className="sentinela-secao">{TITULO_IA_COMO}</h2>
      <Lista itens={IA_COMO} />

      <h2 className="sentinela-secao">{TITULO_DADOS_COMO}</h2>
      <p>{SOBRE_DADOS}</p>

      <h2 className="sentinela-secao">{TITULO_LIMITACOES}</h2>
      <Lista itens={LIMITACOES} />
    </div>
  );
}
