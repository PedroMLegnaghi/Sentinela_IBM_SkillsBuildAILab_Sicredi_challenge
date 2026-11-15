/**
 * Página /filial/fila: fila de alertas da agência (Issue #97).
 */

import PaginaFilaFilial from "@/components/filial/PaginaFilaFilial";
import SoPapeis from "@/components/layout/SoPapeis";

// A página depende da sessão no navegador (Issue #91): fora da validação de navegação instantânea.
export const instant = false;

export const metadata = { title: "Fila de alertas · Sentinela" };

export default function Pagina() {
  return (
    <SoPapeis papeis={["auditor", "gerente"]}>
      <PaginaFilaFilial />
    </SoPapeis>
  );
}
