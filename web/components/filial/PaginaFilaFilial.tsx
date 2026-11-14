"use client";

/**
 * Fila de alertas da agência (Issue #97): só a carteira da filial, com filtros por situação,
 * a tabela e o painel da compra escolhida. Tela "Filial: auditor" do protótipo.
 */

import { useState } from "react";
import { obterFilaFilial } from "@/lib/api";
import { useCarregar } from "@/lib/useCarregar";
import type { ItemFilaFilial, SituacaoCompra } from "@/lib/tipos";
import EstadoErro from "@/components/comuns/EstadoErro";
import EtiquetaSituacaoFilial from "@/components/filial/EtiquetaSituacaoFilial";
import EtiquetaVeredito from "@/components/filial/EtiquetaVeredito";
import NotaRisco from "@/components/filial/NotaRisco";
import PainelCompraFilial from "@/components/filial/PainelCompraFilial";
import { formatarDiaHora, formatarInteiro, formatarMoeda } from "@/lib/formatacao";
import {
  ASSOCIADO_E_CARTAO,
  CARREGANDO,
  COLUNAS_FILA_FILIAL,
  ESCOLHA_UMA_COMPRA,
  FILA_FILIAL_VAZIA,
  FILTRO_TODAS,
  FILTROS_FILA,
  LEGENDA_FILA_FILIAL,
  ROTULO_TABELA_FILA_FILIAL,
  ROTULOS_FILTRO_FILA,
  TITULO_FILA_FILIAL,
} from "@/lib/textos";

const FILTROS: (SituacaoCompra | null)[] = [null, "BLOQUEADA", "AGUARDANDO", "CONTESTADA"];

/** Itens da fila que passam no filtro (null mostra todos). */
export function filtrarFila(itens: ItemFilaFilial[], filtro: SituacaoCompra | null) {
  return filtro ? itens.filter((i) => i.situacao === filtro) : itens;
}

export default function PaginaFilaFilial() {
  const { dados, erro, recarregar } = useCarregar(() => obterFilaFilial());
  const [filtro, setFiltro] = useState<SituacaoCompra | null>(null);
  const [escolhida, setEscolhida] = useState<string | null>(null);

  const itens = dados ? filtrarFila(dados.itens, filtro) : [];
  const selecionada = escolhida ?? itens[0]?.id_compra ?? null;

  return (
    <>
      <h1>{TITULO_FILA_FILIAL}</h1>
      {dados && (
        <p className="sc-filial__descricao">
          {LEGENDA_FILA_FILIAL(formatarInteiro(dados.total), dados.filial.nome)}
        </p>
      )}

      {erro && <EstadoErro mensagem={erro} aoTentarNovamente={recarregar} />}
      {!dados && !erro && <p className="sc-carregando">{CARREGANDO}</p>}

      {dados && (
        <div className="sc-grade-fila">
          <section className="sc-cartao" style={{ minWidth: 0 }}>
            <div className="sc-chips" role="group" aria-label={FILTROS_FILA} style={{ marginBottom: 12 }}>
              {FILTROS.map((f) => (
                <button
                  key={f ?? "todas"}
                  type="button"
                  className="sc-chip"
                  aria-pressed={filtro === f}
                  onClick={() => setFiltro(f)}
                >
                  {f ? ROTULOS_FILTRO_FILA[f] : FILTRO_TODAS}
                  {" "}
                  <span className="sc-num">({filtrarFila(dados.itens, f).length})</span>
                </button>
              ))}
            </div>
            {itens.length === 0 ? (
              <p className="sc-apoio">{FILA_FILIAL_VAZIA}</p>
            ) : (
              <div className="sc-tabela-rolagem">
                <table className="sc-tabela" aria-label={ROTULO_TABELA_FILA_FILIAL}>
                  <thead>
                    <tr>
                      <th scope="col">{COLUNAS_FILA_FILIAL.nota}</th>
                      <th scope="col">{COLUNAS_FILA_FILIAL.associado}</th>
                      <th scope="col">{COLUNAS_FILA_FILIAL.quando}</th>
                      <th scope="col" className="sc-direita">{COLUNAS_FILA_FILIAL.valor}</th>
                      <th scope="col">{COLUNAS_FILA_FILIAL.situacao}</th>
                      <th scope="col">{COLUNAS_FILA_FILIAL.ia}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {itens.map((item) => (
                      <tr
                        key={item.id_compra}
                        aria-selected={item.id_compra === selecionada}
                        tabIndex={0}
                        onClick={() => setEscolhida(item.id_compra)}
                        onKeyDown={(e) => {
                          if (e.key === "Enter" || e.key === " ") {
                            e.preventDefault();
                            setEscolhida(item.id_compra);
                          }
                        }}
                      >
                        <td>
                          <NotaRisco nota={item.nota} />
                        </td>
                        <td>{ASSOCIADO_E_CARTAO(item.associado, item.final_cartao)}</td>
                        <td className="sc-num">{formatarDiaHora(item.data_hora)}</td>
                        <td className="sc-direita sc-num">{formatarMoeda(item.valor)}</td>
                        <td>
                          <EtiquetaSituacaoFilial situacao={item.situacao} />
                        </td>
                        <td>
                          <EtiquetaVeredito veredito={item.veredito_ia} />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
          <section className="sc-cartao">
            {selecionada ? (
              <PainelCompraFilial key={selecionada} idCompra={selecionada} />
            ) : (
              <p className="sc-apoio">{ESCOLHA_UMA_COMPRA}</p>
            )}
          </section>
        </div>
      )}
    </>
  );
}
