/**
 * /filial leva cada papel para a sua página inicial (Issue #91).
 */

import RedirecionarFilial from "@/components/filial/RedirecionarFilial";

// A página depende da sessão no navegador (Issue #91): fora da validação de navegação instantânea.
export const instant = false;

export default function Pagina() {
  return <RedirecionarFilial />;
}
