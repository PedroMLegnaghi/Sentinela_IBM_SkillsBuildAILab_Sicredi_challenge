"use client";

/**
 * Página "Respostas do analista": resumo, concordância com o modelo, tabela e exportação CSV.
 */

import { useEffect, useState } from "react";
import { Button, Heading, Tile } from "@carbon/react";
import EstadoCarregando from "@/components/comuns/EstadoCarregando";
import EstadoErro from "@/components/comuns/EstadoErro";
import { obterRespostas } from "@/lib/api";
import {
  formatarDataHora,
  formatarDecimal,
  formatarInteiro,
  formatarNota,
  formatarResposta,
} from "@/lib/formatacao";
import { gerarCsvRespostas } from "@/lib/simulacao";
import {
  AJUDA_CONCORDANCIA,
  BOTAO_EXPORTAR,
  COLUNAS_RESPOSTAS,
  INDICADORES_RESPOSTAS,
  LEGENDA_RESPOSTAS,
  NOME_ARQUIVO_CSV,
  RESPOSTAS_VAZIAS,
  ROTULOS_CURTOS_DECISAO,
  TITULO_RESPOSTAS,
} from "@/lib/textos";
import type { RespostaRespostas } from "@/lib/tipos";

function exportar(itens: RespostaRespostas["itens"]) {
  const blob = new Blob([gerarCsvRespostas(itens)], {
    type: "text/csv;charset=utf-8",
  });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = NOME_ARQUIVO_CSV;
  link.click();
  URL.revokeObjectURL(url);
}

export default function PaginaRespostas() {
  const [dados, setDados] = useState<RespostaRespostas | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    let cancelado = false;
    obterRespostas()
      .then((r) => !cancelado && setDados(r))
      .catch((e: Error) => !cancelado && setErro(e.message));
    return () => {
      cancelado = true;
    };
  }, []);

  if (erro) return <EstadoErro mensagem={erro} />;
  if (!dados) return <EstadoCarregando />;

  const indicadores = [
    [INDICADORES_RESPOSTAS.total, formatarInteiro(dados.total)],
    [INDICADORES_RESPOSTAS.fraudes, formatarInteiro(dados.fraudes)],
    [INDICADORES_RESPOSTAS.legitimas, formatarInteiro(dados.legitimas)],
    [
      INDICADORES_RESPOSTAS.concordancia,
      dados.concordancia === null
        ? "—"
        : `${formatarDecimal(dados.concordancia, 1)}%`,
    ],
  ];

  return (
    <div className="sentinela-pagina">
      <Heading>{TITULO_RESPOSTAS}</Heading>
      <p className="sentinela-legenda">{LEGENDA_RESPOSTAS}</p>
      <dl className="sentinela-indicadores">
        {indicadores.map(([rotulo, valor]) => (
          <Tile key={rotulo} className="sentinela-indicador">
            <dt>{rotulo}</dt>
            <dd>{valor}</dd>
          </Tile>
        ))}
      </dl>
      <p className="sentinela-legenda">{AJUDA_CONCORDANCIA}</p>
      {dados.itens.length === 0 ? (
        <p role="status">{RESPOSTAS_VAZIAS}</p>
      ) : (
        <>
          <Button kind="tertiary" onClick={() => exportar(dados.itens)}>
            {BOTAO_EXPORTAR}
          </Button>
          <div className="sentinela-tabela-rolagem">
          <table className="cds--data-table cds--data-table--sm">
            <thead>
              <tr>
                {Object.values(COLUNAS_RESPOSTAS).map((coluna) => (
                  <th key={coluna} scope="col">
                    {coluna}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {dados.itens.map((item) => (
                <tr key={item.id_transacao}>
                  <td>{item.id_transacao}</td>
                  <td>{formatarResposta(item.resposta)}</td>
                  <td>{formatarDataHora(item.registrado_em)}</td>
                  <td>{ROTULOS_CURTOS_DECISAO[item.decisao]}</td>
                  <td>{formatarNota(item.nota)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          </div>
        </>
      )}
    </div>
  );
}
