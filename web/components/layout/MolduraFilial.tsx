"use client";

/**
 * Moldura da área da filial (Issue #91): menu lateral com a agência, os links do papel e
 * quem entrou. Os links mudam para auditor e gerente.
 */

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import GuardaSessao from "@/components/layout/GuardaSessao";
import { iniciais, sair } from "@/lib/sessao";
import type { Papel } from "@/lib/tipos";
import {
  ALT_LOGO,
  NAV_COMO_FUNCIONA,
  NAV_DESEMPENHO,
  NAV_FILA,
  NAV_PAINEL_AGENCIA,
  ROTULO_NAV_FILIAL,
  ROTULOS_PAPEL,
  SAIR,
} from "@/lib/textos";

const LINKS: Record<Exclude<Papel, "associado">, { href: string; rotulo: string }[]> = {
  auditor: [
    { href: "/filial/fila", rotulo: NAV_FILA },
    { href: "/filial/desempenho", rotulo: NAV_DESEMPENHO },
    { href: "/filial/como-funciona", rotulo: NAV_COMO_FUNCIONA },
  ],
  gerente: [
    { href: "/filial/painel", rotulo: NAV_PAINEL_AGENCIA },
    { href: "/filial/fila", rotulo: NAV_FILA },
    { href: "/filial/desempenho", rotulo: NAV_DESEMPENHO },
    { href: "/filial/como-funciona", rotulo: NAV_COMO_FUNCIONA },
  ],
};

/** Links do menu para o papel (associado não entra na filial). */
export function linksDoPapel(papel: Papel) {
  return papel === "associado" ? [] : LINKS[papel];
}

export default function MolduraFilial({ children }: { children: React.ReactNode }) {
  const caminho = usePathname() ?? "";
  const router = useRouter();

  return (
    <GuardaSessao papeis={["auditor", "gerente"]}>
      {(sessao) => (
        <div className="sc-filial">
          <aside className="sc-filial__lado">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img className="sc-filial__logo" src="/logo-sicredi.png" alt={ALT_LOGO} />
            <div className="sc-filial__agencia">{sessao.perfil.filial.nome}</div>
            <nav aria-label={ROTULO_NAV_FILIAL} style={{ display: "contents" }}>
              {linksDoPapel(sessao.perfil.papel).map(({ href, rotulo }) => (
                <Link
                  key={href}
                  href={href}
                  className="sc-filial__link"
                  aria-current={caminho.startsWith(href) ? "page" : undefined}
                >
                  {rotulo}
                </Link>
              ))}
            </nav>
            <div className="sc-filial__quem">
              <span className="sc-avatar" aria-hidden="true">
                {iniciais(sessao.perfil.nome)}
              </span>
              <div>
                <b>{sessao.perfil.nome}</b>
                <small>{ROTULOS_PAPEL[sessao.perfil.papel]}</small>
                <button
                  type="button"
                  className="sc-filial__sair"
                  onClick={() => {
                    sair();
                    router.replace("/entrar");
                  }}
                >
                  {SAIR}
                </button>
              </div>
            </div>
          </aside>
          <main className="sc-filial__area">{children}</main>
        </div>
      )}
    </GuardaSessao>
  );
}
