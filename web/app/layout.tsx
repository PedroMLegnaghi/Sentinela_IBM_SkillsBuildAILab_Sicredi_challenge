/**
 * Layout raiz do site Sentinela.
 * Aplica o tema Carbon g10 e o shell de navegação.
 */

import type { Metadata } from "next";
import { GlobalTheme } from "@carbon/react";
import Shell from "@/components/layout/Shell";
import "@/app/globals.scss";

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
      <body>
        <GlobalTheme theme="g10">
          <Shell>{children}</Shell>
        </GlobalTheme>
      </body>
    </html>
  );
}
