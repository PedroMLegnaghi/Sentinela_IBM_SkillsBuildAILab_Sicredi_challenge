/**
 * Página /filial/painel: painel do gerente (Issue #99).
 */

import PaginaPainelAgencia from "@/components/gerente/PaginaPainelAgencia";
import SoGerente from "@/components/gerente/SoGerente";

export const metadata = { title: "Painel da agência · Sentinela" };

export default function Pagina() {
  return (
    <SoGerente>
      <PaginaPainelAgencia />
    </SoGerente>
  );
}
