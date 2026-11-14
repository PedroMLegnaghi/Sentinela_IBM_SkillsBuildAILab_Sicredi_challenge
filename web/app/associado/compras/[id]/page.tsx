/**
 * Página /associado/compras/[id]: detalhe de uma compra (Issues #93 e #95).
 */

import DetalheCompra from "@/components/associado/DetalheCompra";

export const metadata = { title: "Compra · Sicredi" };

export default async function Pagina({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <DetalheCompra idCompra={id} />;
}
