/**
 * Página /associado/comprar: simular compra (Issue #95).
 */

import PaginaComprar from "@/components/associado/PaginaComprar";

// A página depende da sessão no navegador (Issue #91): fora da validação de navegação instantânea.
export const instant = false;

export const metadata = { title: "Simular compra · Sicredi" };

export default function Pagina() {
  return <PaginaComprar />;
}
