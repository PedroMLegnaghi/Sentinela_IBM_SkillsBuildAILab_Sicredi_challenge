/**
 * Layout raiz do site Sentinela.
 * Aplica o tema Carbon g10, identidade Sicredi e o shell de navegação.
 */

import type { Metadata } from "next";
import { Nunito, Exo_2 } from "next/font/google";
import { GlobalTheme } from "@carbon/react";
import Shell from "@/components/layout/Shell";
import "@/app/globals.scss";

const nunito = Nunito({
  subsets: ["latin"],
  weight: ["400", "600", "700", "800"],
  variable: "--fonte-texto",
  display: "swap",
});

const exo2 = Exo_2({
  subsets: ["latin"],
  weight: ["600", "700"],
  style: ["normal", "italic"],
  variable: "--fonte-titulo",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Sentinela · Agente antifraude",
  description:
    "Agente antifraude para análise de transações de cartão. Protótipo do IBM SkillsBuild AI Lab, Desafio Sicredi.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <body className={`${nunito.variable} ${exo2.variable}`}>
        <GlobalTheme theme="g10">
          <Shell>{children}</Shell>
        </GlobalTheme>
      </body>
    </html>
  );
}
