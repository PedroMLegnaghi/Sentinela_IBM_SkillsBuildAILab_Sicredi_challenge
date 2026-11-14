/**
 * Página /associado: início do app do associado (Issues #91 e #93).
 */

import ListaNotificacoes from "@/components/associado/ListaNotificacoes";
import { TITULO_APP_ASSOCIADO } from "@/lib/textos";

export const metadata = { title: "Início · Sicredi" };

export default function PaginaAssociado() {
  return (
    <>
      <div className="sc-cabecalho-tela">
        <h1>{TITULO_APP_ASSOCIADO}</h1>
      </div>
      <ListaNotificacoes />
    </>
  );
}
