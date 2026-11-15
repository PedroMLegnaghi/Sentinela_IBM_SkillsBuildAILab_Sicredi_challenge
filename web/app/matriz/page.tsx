/**
 * Página /matriz: painel da matriz (seção 17.8).
 */

import PaginaPainelMatriz from "@/components/matriz/PaginaPainelMatriz";
import SoPapeis from "@/components/layout/SoPapeis";

// A página depende da sessão no navegador (Issue #91): fora da validação de navegação instantânea.
export const instant = false;

export const metadata = { title: "Painel da matriz · Sentinela" };

export default function Pagina() {
  return (
    <SoPapeis papeis={["matriz"]}>
      <PaginaPainelMatriz />
    </SoPapeis>
  );
}
