"use client";

/**
 * Moldura da área do associado (Issue #91): coluna de celular com a navegação embaixo.
 */

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Chat, Home, Receipt, ShoppingCart } from "@carbon/react/icons";
import GuardaSessao from "@/components/layout/GuardaSessao";
import {
  NAV_CHAT,
  NAV_COMPRAR,
  NAV_EXTRATO,
  NAV_INICIO,
  ROTULO_NAV_ASSOCIADO,
} from "@/lib/textos";

const ITENS = [
  { href: "/associado", rotulo: NAV_INICIO, Icone: Home },
  { href: "/associado/extrato", rotulo: NAV_EXTRATO, Icone: Receipt },
  { href: "/associado/comprar", rotulo: NAV_COMPRAR, Icone: ShoppingCart },
  { href: "/associado/chat", rotulo: NAV_CHAT, Icone: Chat },
];

/** Item ativo: o início só na raiz; os outros também nas subpáginas. */
export function itemAtivo(caminho: string, href: string): boolean {
  if (href === "/associado") return caminho === "/associado";
  return caminho === href || caminho.startsWith(`${href}/`);
}

export default function MolduraAssociado({ children }: { children: React.ReactNode }) {
  const caminho = usePathname() ?? "";
  return (
    <div className="sc-associado">
      <div className="sc-associado__coluna">
        <GuardaSessao papeis={["associado"]}>
          {() => <main className="sc-associado__corpo">{children}</main>}
        </GuardaSessao>
        <nav className="sc-associado__nav" aria-label={ROTULO_NAV_ASSOCIADO}>
          {ITENS.map(({ href, rotulo, Icone }) => (
            <Link
              key={href}
              href={href}
              className="sc-associado__nav-item"
              aria-current={itemAtivo(caminho, href) ? "page" : undefined}
            >
              <Icone size={20} aria-hidden="true" />
              {rotulo}
            </Link>
          ))}
        </nav>
      </div>
    </div>
  );
}
