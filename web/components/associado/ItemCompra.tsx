/**
 * Uma compra na lista do associado (Issue #93). Abre o detalhe da compra.
 */

import Link from "next/link";
import type { CompraExtrato } from "@/lib/tipos";
import EtiquetaSituacao from "@/components/associado/EtiquetaSituacao";
import { formatarDiaHora, formatarMoeda, formatarTipo } from "@/lib/formatacao";
import { ABRIR_COMPRA, COMPRA_SIMULADA, DESCRICAO_COMPRA } from "@/lib/textos";

interface PropsItemCompra {
  compra: CompraExtrato;
  mostrarSituacao?: boolean;
}

export default function ItemCompra({ compra, mostrarSituacao = true }: PropsItemCompra) {
  const valor = formatarMoeda(compra.valor);
  const riscado = compra.situacao === "BLOQUEADA" || compra.situacao === "CONTESTADA";
  return (
    <li>
      <Link
        href={`/associado/compras/${compra.id_compra}`}
        className="sc-item-compra"
        aria-label={ABRIR_COMPRA(compra.estabelecimento, valor)}
      >
        <span className="sc-item-compra__icone" aria-hidden="true">
          {compra.estabelecimento.charAt(0).toUpperCase()}
        </span>
        <span className="sc-item-compra__meio">
          <b>{compra.estabelecimento}</b>
          <small>
            {DESCRICAO_COMPRA(formatarDiaHora(compra.data_hora), formatarTipo(compra.tipo_transacao).toLowerCase())}
          </small>
          {(mostrarSituacao || compra.situacao !== "APROVADA") && (
            <span className="sc-item-compra__etiquetas">
              <EtiquetaSituacao situacao={compra.situacao} />
              {compra.simulada && (
                <span className="sc-etiqueta sc-etiqueta--neutra">{COMPRA_SIMULADA}</span>
              )}
            </span>
          )}
        </span>
        <span className={`sc-item-compra__valor sc-num${riscado ? " sc-riscado" : ""}`}>{valor}</span>
      </Link>
    </li>
  );
}
