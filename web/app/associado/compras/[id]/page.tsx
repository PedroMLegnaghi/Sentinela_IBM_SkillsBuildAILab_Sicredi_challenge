/**
 * Página /associado/compras/[id]: detalhe de uma compra (Issues #93 e #95).
 */

import DetalheCompra from "@/components/associado/DetalheCompra";

// A página depende da sessão no navegador (Issue #91): fora da validação de navegação instantânea.
export const instant = false;

export const metadata = { title: "Compra · Sicredi" };

export default async function Pagina({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <DetalheCompra idCompra={id} />;
}
