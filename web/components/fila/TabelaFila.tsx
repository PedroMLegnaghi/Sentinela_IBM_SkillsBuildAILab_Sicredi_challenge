"use client";

/**
 * Tabela paginada da fila. Cada linha abre a transação no painel (clique ou teclado).
 */

import { useState } from "react";
import { Pagination } from "@carbon/react";
import {
  formatarDataHora,
  formatarInteiro,
  formatarMoeda,
  formatarNota,
  formatarTipo,
} from "@/lib/formatacao";
import {
  ABRIR_TRANSACAO,
  COLUNAS_FILA,
  ITENS_POR_PAGINA,
  MOSTRANDO,
  PAGINACAO,
  ROTULO_TABELA_FILA,
  ROTULOS_CURTOS_DECISAO,
} from "@/lib/textos";
import type { ItemFila } from "@/lib/tipos";

const TAMANHOS_PAGINA = [10, 25, 50];

interface PropsTabelaFila {
  itens: ItemFila[];
  total: number;
  idSelecionado: number | null;
  aoSelecionar: (id: number) => void;
}

export default function TabelaFila({
  itens,
  total,
  idSelecionado,
  aoSelecionar,
}: PropsTabelaFila) {
  const [pagina, setPagina] = useState(1);
  const [tamanho, setTamanho] = useState(TAMANHOS_PAGINA[1]);
  const ultimaPagina = Math.max(1, Math.ceil(itens.length / tamanho));
  const paginaAtual = Math.min(pagina, ultimaPagina);
  const visiveis = itens.slice(
    (paginaAtual - 1) * tamanho,
    paginaAtual * tamanho,
  );

  return (
    <div>
      <p className="sentinela-legenda">
        {MOSTRANDO(formatarInteiro(itens.length), formatarInteiro(total))}
      </p>
      <div className="sentinela-tabela-rolagem">
        <table
          className="cds--data-table cds--data-table--sm"
          aria-label={ROTULO_TABELA_FILA}
        >
          <thead>
            <tr>
              {Object.values(COLUNAS_FILA).map((coluna) => (
                <th key={coluna} scope="col">
                  {coluna}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {visiveis.map((item) => (
              <tr
                key={item.id_transacao}
                aria-selected={item.id_transacao === idSelecionado}
                className={
                  item.id_transacao === idSelecionado
                    ? "sentinela-linha-selecionada"
                    : undefined
                }
                onClick={() => aoSelecionar(item.id_transacao)}
              >
                <td>
                  <button
                    type="button"
                    className="sentinela-link-linha"
                    aria-label={ABRIR_TRANSACAO(item.id_transacao)}
                    onClick={() => aoSelecionar(item.id_transacao)}
                  >
                    {item.id_transacao}
                  </button>
                </td>
                <td>{formatarNota(item.nota)}</td>
                <td>{ROTULOS_CURTOS_DECISAO[item.decisao]}</td>
                <td>{formatarMoeda(item.valor)}</td>
                <td>{formatarDataHora(item.data_hora)}</td>
                <td>{formatarTipo(item.tipo_transacao)}</td>
                <td>{item.n_sinais}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <Pagination
        page={paginaAtual}
        pageSize={tamanho}
        pageSizes={TAMANHOS_PAGINA}
        totalItems={itens.length}
        itemsPerPageText={ITENS_POR_PAGINA}
        itemRangeText={PAGINACAO.intervaloItens}
        pageRangeText={PAGINACAO.intervaloPaginas}
        backwardText={PAGINACAO.anterior}
        forwardText={PAGINACAO.proxima}
        pageNumberText={PAGINACAO.pagina}
        onChange={({ page, pageSize }: { page: number; pageSize: number }) => {
          setPagina(page);
          setTamanho(pageSize);
        }}
      />
    </div>
  );
}
