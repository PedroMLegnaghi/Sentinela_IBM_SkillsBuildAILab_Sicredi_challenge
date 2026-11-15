"use client";

/**
 * Cabeçalho e menu lateral do site Sentinela com tema Carbon g10.
 * As 5 rotas da ESPECIFICACAO, seção 14.
 * Abaixo de 1056 px o menu começa fechado e abre pelo botão hambúrguer.
 */

import { useCallback, useEffect, useState } from "react";
import {
  Header,
  HeaderMenuButton,
  HeaderName,
  SideNav,
  SideNavItems,
  SideNavLink,
  Content,
} from "@carbon/react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import {
  NAV_ASSOCIADO,
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
  { href: "/associado", rotulo: NAV_ASSOCIADO },
];

// Largura de quebra do Carbon (lg): abaixo disso o menu começa fechado.
const LARGURA_MENU_FIXO = 1056;

interface PropsShell {
  children: React.ReactNode;
}

export default function Shell({ children }: PropsShell) {
  const caminho = usePathname();
  const [menuAberto, setMenuAberto] = useState(false);
  const [telaLarga, setTelaLarga] = useState(true);

  useEffect(() => {
    function verificarLargura() {
      setTelaLarga(window.innerWidth >= LARGURA_MENU_FIXO);
      if (window.innerWidth >= LARGURA_MENU_FIXO) {
        setMenuAberto(false);
      }
    }
    verificarLargura();
    window.addEventListener("resize", verificarLargura);
    return () => window.removeEventListener("resize", verificarLargura);
  }, []);

  const fecharMenu = useCallback(() => {
    if (!telaLarga) setMenuAberto(false);
  }, [telaLarga]);

  return (
    <>
      <Header aria-label="Sentinela">
        {!telaLarga && (
          <HeaderMenuButton
            aria-label={menuAberto ? "Fechar menu" : "Abrir menu"}
            isActive={menuAberto}
            onClick={() => setMenuAberto((v) => !v)}
          />
        )}
        <HeaderName prefix="">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="/logo-sicredi.png"
            alt="Sicredi"
            height={28}
            style={{ marginRight: "0.5rem", verticalAlign: "middle" }}
          />
          Sentinela
        </HeaderName>
      </Header>
      <SideNav
        aria-label="Menu de navegação"
        isFixedNav
        expanded={telaLarga || menuAberto}
        isPersistent={telaLarga}
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
              onClick={fecharMenu}
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
