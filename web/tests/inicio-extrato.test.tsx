/**
 * Testes do início, do extrato e do detalhe da compra do associado (Issue #93).
 */

import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import PaginaInicio from "@/components/associado/PaginaInicio";
import PaginaExtrato, { agruparPorMes } from "@/components/associado/PaginaExtrato";
import DetalheCompra from "@/components/associado/DetalheCompra";
import * as api from "@/lib/api";
import { mocksRefatoracao as m } from "@/lib/mocks/refatoracao";
import { formatarDiaHora, formatarMesAno } from "@/lib/formatacao";
import { PENDENTE_TITULO, ROTULOS_FILTRO_SITUACAO } from "@/lib/textos";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
}));

vi.mock("@/lib/api", () => ({
  obterInicio: vi.fn(),
  obterExtrato: vi.fn(),
  obterCompra: vi.fn(),
}));

const apiFalsa = vi.mocked(api);

beforeEach(() => vi.clearAllMocks());

describe("PaginaInicio", () => {
  it("mostra saldo, limite, cartões e o aviso pendente", async () => {
    apiFalsa.obterInicio.mockResolvedValue(m.inicio);
    render(<PaginaInicio />);

    expect(await screen.findByText("Olá, Ana")).toBeInTheDocument();
    expect(screen.getByText("R$ 4.820,35")).toBeInTheDocument();
    expect(screen.getByText("R$ 2.150,00")).toBeInTheDocument();
    expect(screen.getByText("Crédito · final 4821")).toBeInTheDocument();
    expect(screen.getByText(PENDENTE_TITULO)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Responder" })).toHaveAttribute(
      "href",
      "/associado/avisos/not-mock-001",
    );
    expect(screen.getByRole("button", { name: /Investir/ })).toBeDisabled();
  });

  it("não mostra detalhe técnico ao associado", async () => {
    apiFalsa.obterInicio.mockResolvedValue(m.inicio);
    render(<PaginaInicio />);
    await screen.findByText("Olá, Ana");
    expect(screen.queryByText(/nota|sinais|watsonx/i)).not.toBeInTheDocument();
  });
});

describe("PaginaExtrato", () => {
  it("filtra só as bloqueadas", async () => {
    apiFalsa.obterExtrato.mockImplementation(async (situacoes) => {
      const itens = situacoes?.length
        ? m.extrato.itens.filter((c) => situacoes.includes(c.situacao))
        : m.extrato.itens;
      return { total: itens.length, itens };
    });
    render(<PaginaExtrato />);
    expect(await screen.findByText("Mercado Bom Preço")).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: ROTULOS_FILTRO_SITUACAO.BLOQUEADA }));

    expect(await screen.findByText("Eletrônicos Web")).toBeInTheDocument();
    expect(screen.queryByText("Mercado Bom Preço")).not.toBeInTheDocument();
    expect(apiFalsa.obterExtrato).toHaveBeenLastCalledWith(["BLOQUEADA"]);
  });

  it("agrupa as compras por mês", () => {
    const grupos = agruparPorMes(m.extrato.itens);
    expect(grupos).toHaveLength(1);
    expect(grupos[0][0]).toBe("Março de 2025");
    expect(grupos[0][1]).toHaveLength(6);
  });
});

describe("DetalheCompra", () => {
  it("mostra quem bloqueou e o motivo genérico", async () => {
    apiFalsa.obterCompra.mockResolvedValue(m.compraBloqueada);
    render(<DetalheCompra idCompra="cmp-000005" />);

    expect(await screen.findByText("Sentinela")).toBeInTheDocument();
    expect(screen.getByText(m.compraBloqueada.bloqueio!.motivo)).toBeInTheDocument();
    const aviso = screen.getByText(/Você respondeu/);
    expect(within(aviso).getByText(/O valor não foi cobrado/)).toBeInTheDocument();
  });
});

describe("formatação do extrato", () => {
  it("formata dia e hora curtos e o mês por extenso", () => {
    expect(formatarDiaHora("2025-03-14T18:42:00")).toBe("14/03, 18:42");
    expect(formatarDiaHora(null)).toBe("Sem data");
    expect(formatarMesAno("2025-03-14T18:42:00")).toBe("Março de 2025");
  });
});
