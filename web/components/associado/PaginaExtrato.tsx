"use client";

/**
 * Extrato do associado (Issue #93): filtros por situação e compras agrupadas por mês.
 * Tela 3 do protótipo.
 */

import { useState } from "react";
import { useCarregar } from "@/lib/useCarregar";
import { obterExtrato } from "@/lib/api";
import type { CompraExtrato, SituacaoCompra } from "@/lib/tipos";
import ItemCompra from "@/components/associado/ItemCompra";
import EstadoErro from "@/components/comuns/EstadoErro";
import { formatarMesAno } from "@/lib/formatacao";
import {
  CARREGANDO,
  EXTRATO_VAZIO,
  FILTRO_TODAS,
  FILTROS_EXTRATO,
  ROTULOS_FILTRO_SITUACAO,
  TITULO_EXTRATO,
} from "@/lib/textos";

const FILTROS: (SituacaoCompra | null)[] = [null, "APROVADA", "AGUARDANDO", "BLOQUEADA", "CONTESTADA"];

/** Agrupa as compras por mês, na ordem em que vieram. */
export function agruparPorMes(itens: CompraExtrato[]): [string, CompraExtrato[]][] {
  const grupos = new Map<string, CompraExtrato[]>();
  for (const item of itens) {
    const mes = formatarMesAno(item.data_hora);
    grupos.set(mes, [...(grupos.get(mes) ?? []), item]);
  }
  return [...grupos.entries()];
}

export default function PaginaExtrato() {
  const [filtro, setFiltro] = useState<SituacaoCompra | null>(null);
  const { dados, erro, recarregar: carregar } = useCarregar(
    () => obterExtrato(filtro ? [filtro] : undefined),
    filtro ?? "todas",
  );
  const itens = dados?.itens ?? null;

  return (
    <>
      <div className="sc-cabecalho-tela">
        <h1>{TITULO_EXTRATO}</h1>
      </div>
      <div className="sc-chips" role="group" aria-label={FILTROS_EXTRATO} style={{ marginBottom: 14 }}>
        {FILTROS.map((f) => (
          <button
            key={f ?? "todas"}
            type="button"
            className="sc-chip"
            aria-pressed={filtro === f}
            onClick={() => setFiltro(f)}
          >
            {f ? ROTULOS_FILTRO_SITUACAO[f] : FILTRO_TODAS}
          </button>
        ))}
      </div>

      {erro && <EstadoErro mensagem={erro} aoTentarNovamente={carregar} />}
      {!itens && !erro && <p className="sc-carregando">{CARREGANDO}</p>}
      {itens && itens.length === 0 && <p className="sc-apoio">{EXTRATO_VAZIO}</p>}

      {itens &&
        agruparPorMes(itens).map(([mes, compras]) => (
          <section key={mes} aria-label={mes} style={{ marginBottom: 16 }}>
            <h2 className="sc-rotulo" style={{ fontStyle: "normal" }}>
              {mes}
            </h2>
            <ul className="sc-cartao sc-lista-compras" style={{ marginTop: 6 }}>
              {compras.map((c) => (
                <ItemCompra key={c.id_compra} compra={c} />
              ))}
            </ul>
          </section>
        ))}
    </>
  );
}
