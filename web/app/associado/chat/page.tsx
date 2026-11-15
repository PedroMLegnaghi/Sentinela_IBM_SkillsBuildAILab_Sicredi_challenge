/**
 * Página /associado/chat: chat do associado (Issue #106).
 */

import PaginaChat from "@/components/associado/PaginaChat";

// A página depende da sessão no navegador (Issue #91): fora da validação de navegação instantânea.
export const instant = false;

export const metadata = { title: "Chat · Sicredi" };

export default function Pagina() {
  return <PaginaChat />;
}
