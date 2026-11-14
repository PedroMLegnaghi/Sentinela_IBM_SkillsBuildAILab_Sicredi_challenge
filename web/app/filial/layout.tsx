/**
 * Layout da área da filial (Issue #91).
 * A moldura depende da sessão no navegador: a área não tem tela pronta no servidor.
 */

import { Suspense } from "react";
import MolduraFilial from "@/components/layout/MolduraFilial";

export const instant = false;

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <Suspense fallback={null}>
      <MolduraFilial>{children}</MolduraFilial>
    </Suspense>
  );
}
