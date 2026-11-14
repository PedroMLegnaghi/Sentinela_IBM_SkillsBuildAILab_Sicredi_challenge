/**
 * Testes do componente PerfilAssociado (Issue #64).
 */

import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import PerfilAssociado from "@/components/painel/PerfilAssociado";
import { mocks } from "@/lib/mocks/index";
import {
  TITULO_PERFIL_ASSOCIADO,
  PERFIL_SEM_HISTORICO,
} from "@/lib/textos";
import type { PerfilAssociado as TPerfilAssociado } from "@/lib/tipos";

describe("PerfilAssociado", () => {
  it("mostra o título do cartão", () => {
    render(<PerfilAssociado perfil={mocks.transacao.perfil_associado} />);

    expect(screen.getByText(TITULO_PERFIL_ASSOCIADO)).toBeInTheDocument();
  });

  it("mostra a mensagem de primeira compra quando perfil é null", () => {
    render(<PerfilAssociado perfil={null} />);

    expect(screen.getByText(PERFIL_SEM_HISTORICO)).toBeInTheDocument();
  });

  it("mostra compras anteriores quando o perfil tem histórico", async () => {
    const perfil: TPerfilAssociado = {
      compras_anteriores: 5,
      mediana_valor: 200.0,
      valor_atual_sobre_mediana: 1.5,
      hora_mais_comum: 10,
      percentual_madrugada: 0.0,
      percentual_credito_nao_presente: 20.0,
    };

    render(<PerfilAssociado perfil={perfil} />);

    // Clica no accordion para expandir
    const btn = screen.getByRole("button", { name: TITULO_PERFIL_ASSOCIADO });
    btn.click();

    expect(screen.getByText(/5 compras anteriores/)).toBeInTheDocument();
  });

  it("destaca razão alta quando valor_atual_sobre_mediana >= 3", async () => {
    const perfil: TPerfilAssociado = {
      compras_anteriores: 8,
      mediana_valor: 150.0,
      valor_atual_sobre_mediana: 30.1,
      hora_mais_comum: 14,
      percentual_madrugada: 12.5,
      percentual_credito_nao_presente: 25.0,
    };

    render(<PerfilAssociado perfil={perfil} />);

    const btn = screen.getByRole("button", { name: TITULO_PERFIL_ASSOCIADO });
    btn.click();

    expect(
      screen.getByText(/Esta compra é alta em relação à mediana/),
    ).toBeInTheDocument();
  });
});
