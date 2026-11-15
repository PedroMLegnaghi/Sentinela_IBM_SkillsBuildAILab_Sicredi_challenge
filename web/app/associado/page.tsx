/**
 * Página /associado: início do app do associado (Issue #93).
 */

import PaginaInicio from "@/components/associado/PaginaInicio";

// A página depende da sessão no navegador (Issue #91): fora da validação de navegação instantânea.
export const instant = false;

export const metadata = { title: "Início · Sicredi" };

export default function Pagina() {
  return <PaginaInicio />;
}
