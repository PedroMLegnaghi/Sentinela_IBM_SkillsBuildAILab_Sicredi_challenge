/**
 * Página /filial/desempenho: o Sentinela contra o sistema atual em março (Issue #100).
 */

import PaginaDesempenho from "@/components/desempenho/PaginaDesempenho";

// A página depende da sessão no navegador (Issue #91): fora da validação de navegação instantânea.
export const instant = false;

export const metadata = { title: "Desempenho · Sentinela" };

export default function Pagina() {
  return <PaginaDesempenho />;
}
