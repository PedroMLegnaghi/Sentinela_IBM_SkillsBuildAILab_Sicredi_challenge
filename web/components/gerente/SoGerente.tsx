"use client";

/**
 * Só o gerente vê o painel da agência; o auditor vai para a fila (Issue #99).
 */

import GuardaSessao from "@/components/layout/GuardaSessao";

export default function SoGerente({ children }: { children: React.ReactNode }) {
  return <GuardaSessao papeis={["gerente"]}>{() => children}</GuardaSessao>;
}
