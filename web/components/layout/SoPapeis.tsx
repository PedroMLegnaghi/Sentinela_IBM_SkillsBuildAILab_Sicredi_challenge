"use client";

/**
 * Só mostra a página para os papéis indicados; os outros vão para o próprio início.
 */

import GuardaSessao from "@/components/layout/GuardaSessao";
import type { Papel } from "@/lib/tipos";

export default function SoPapeis({
  papeis,
  children,
}: {
  papeis: Papel[];
  children: React.ReactNode;
}) {
  return <GuardaSessao papeis={papeis}>{() => children}</GuardaSessao>;
}
