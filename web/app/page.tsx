/**
 * Página raiz: leva para a tela de entrada (Issue #91).
 */

import { redirect } from "next/navigation";

export default function Pagina() {
  redirect("/entrar");
}
