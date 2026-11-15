/**
 * Página /filial/como-funciona: do associado à filial em quatro passos (Issue #100).
 */

import PaginaComoFunciona from "@/components/como-funciona/PaginaComoFunciona";

// A página depende da sessão no navegador (Issue #91): fora da validação de navegação instantânea.
export const instant = false;

export const metadata = { title: "Como funciona · Sentinela" };

export default function Pagina() {
  return <PaginaComoFunciona />;
}
