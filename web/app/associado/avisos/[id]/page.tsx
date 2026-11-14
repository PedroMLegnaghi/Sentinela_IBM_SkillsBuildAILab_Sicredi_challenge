/**
 * Página /associado/avisos/[id]: aviso "Foi você?" (Issue #95). `?compra=` diz a compra.
 */

import ConfirmarCompra from "@/components/associado/ConfirmarCompra";

export const metadata = { title: "Confirme esta compra · Sicredi" };

export default async function Pagina({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ compra?: string }>;
}) {
  const { id } = await params;
  const { compra } = await searchParams;
  return <ConfirmarCompra idNotificacao={id} idCompra={compra} />;
}
