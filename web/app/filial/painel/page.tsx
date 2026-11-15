/**
 * Página /filial/painel: painel do gerente (Issue #99).
 */

import PaginaPainelAgencia from "@/components/gerente/PaginaPainelAgencia";
import SoGerente from "@/components/gerente/SoGerente";

// A página depende da sessão no navegador (Issue #91): fora da validação de navegação instantânea.
export const instant = false;

export const metadata = { title: "Painel da agência · Sentinela" };

export default function Pagina() {
  return (
    <SoGerente>
      <PaginaPainelAgencia />
    </SoGerente>
  );
}
