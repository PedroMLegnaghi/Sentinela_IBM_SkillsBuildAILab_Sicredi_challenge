/**
 * Página /associado/extrato (Issue #93).
 */

import PaginaExtrato from "@/components/associado/PaginaExtrato";

// A página depende da sessão no navegador (Issue #91): fora da validação de navegação instantânea.
export const instant = false;

export const metadata = { title: "Extrato · Sicredi" };

export default function Pagina() {
  return <PaginaExtrato />;
}
