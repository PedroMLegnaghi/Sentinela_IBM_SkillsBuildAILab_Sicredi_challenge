/**
 * Layout da área do associado (Issue #91).
 * A moldura depende da sessão no navegador: a área não tem tela pronta no servidor.
 */

import { Suspense } from "react";
import MolduraAssociado from "@/components/layout/MolduraAssociado";

export const instant = false;

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <Suspense fallback={null}>
      <MolduraAssociado>{children}</MolduraAssociado>
    </Suspense>
  );
}
