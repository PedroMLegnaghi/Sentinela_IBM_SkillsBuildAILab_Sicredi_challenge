/**
 * Layout raiz do site Sentinela: fontes da Sicredi (Exo 2 e Nunito) e tema Carbon.
 * Cada área (associado e filial) tem a própria moldura no seu layout.
 */

import type { Metadata } from "next";
import { Exo_2, Nunito } from "next/font/google";
import { GlobalTheme } from "@carbon/react";
import "@/app/globals.scss";

const fonteTitulo = Exo_2({
  subsets: ["latin"],
  style: ["normal", "italic"],
  variable: "--fonte-titulo",
});

const fonteTexto = Nunito({
  subsets: ["latin"],
  variable: "--fonte-texto",
});

export const metadata: Metadata = {
  title: "Sentinela · Sicredi",
  description:
    "Sentinela: agente antifraude para compras com cartão. Protótipo do IBM SkillsBuild AI Lab, Desafio Sicredi.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR" className={`${fonteTitulo.variable} ${fonteTexto.variable}`}>
      <body>
        <GlobalTheme theme="white">{children}</GlobalTheme>
      </body>
    </html>
  );
}
