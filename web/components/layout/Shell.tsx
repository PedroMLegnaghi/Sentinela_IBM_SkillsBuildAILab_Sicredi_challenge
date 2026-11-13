"use client";

/**
 * Cabeçalho e menu lateral do site Sentinela com tema Carbon g10.
 * As 5 rotas da ESPECIFICACAO, seção 14.
 */

import {
  Header,
  HeaderName,
  SideNav,
  SideNavItems,
  SideNavLink,
  Content,
} from "@carbon/react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import {
  NAV_FILA,
  NAV_DESEMPENHO,
  NAV_COMO_FUNCIONA,
  NAV_SIMULADOR,
  NAV_RESPOSTAS,
  RODAPE_DADOS,
} from "@/lib/textos";

const ROTAS = [
  { href: "/", rotulo: NAV_FILA },
  { href: "/desempenho", rotulo: NAV_DESEMPENHO },
  { href: "/como-funciona", rotulo: NAV_COMO_FUNCIONA },
  { href: "/simulador", rotulo: NAV_SIMULADOR },
  { href: "/respostas", rotulo: NAV_RESPOSTAS },
];

interface PropsShell {
  children: React.ReactNode;
}

export default function Shell({ children }: PropsShell) {
  const caminho = usePathname();

  return (
    <>
      <Header aria-label="Sentinela">
        <HeaderName prefix="">Sentinela</HeaderName>
      </Header>
      <SideNav
        aria-label="Menu de navegação"
        isFixedNav
        expanded
        isPersistent
      >
        <SideNavItems>
          {ROTAS.map((rota) => (
            <SideNavLink
              key={rota.href}
              renderIcon={() => null}
              href={rota.href}
              element={Link}
              isActive={caminho === rota.href}
              aria-current={caminho === rota.href ? "page" : undefined}
            >
              {rota.rotulo}
            </SideNavLink>
          ))}
        </SideNavItems>
        <footer
          style={{
            padding: "16px",
            fontSize: "0.75rem",
            color: "#525252",
            marginTop: "auto",
          }}
        >
          {RODAPE_DADOS}
        </footer>
      </SideNav>
      <Content>{children}</Content>
    </>
  );
}
