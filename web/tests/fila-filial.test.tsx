/**
 * Testes da fila do auditor e do painel da compra na filial (Issue #97).
 */

import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import PaginaFilaFilial, { filtrarFila } from "@/components/filial/PaginaFilaFilial";
import PainelCompraFilial from "@/components/filial/PainelCompraFilial";
import { faixaDaNota } from "@/components/filial/NotaRisco";
import * as api from "@/lib/api";
import { mocks } from "@/lib/mocks/index";
import { mocksRefatoracao as m } from "@/lib/mocks/refatoracao";
import { ROTULO_TABELA_FILA_FILIAL, ROTULOS_FILTRO_FILA } from "@/lib/textos";

vi.mock("@/lib/api", () => ({
  obterFilaFilial: vi.fn(),
  obterCompraFilial: vi.fn(),
  obterAuditoria: vi.fn(),
  iniciarAuditoria: vi.fn(),
}));

const apiFalsa = vi.mocked(api);

beforeEach(() => {
  vi.clearAllMocks();
  apiFalsa.obterFilaFilial.mockResolvedValue(m.filaFilial);
  apiFalsa.obterCompraFilial.mockImplementation(async (id) => ({
    ...m.compraFilial,
    compra: m.filaFilial.itens.find((i) => i.id_compra === id) ?? m.compraFilial.compra,
  }));
  apiFalsa.obterAuditoria.mockResolvedValue(mocks.auditoriaConcluida);
});

describe("PaginaFilaFilial", () => {
  it("mostra a fila com nome abreviado e final do cartão, e abre a primeira compra", async () => {
    render(<PaginaFilaFilial />);
    const tabela = await screen.findByRole("table", { name: ROTULO_TABELA_FILA_FILIAL });
    expect(within(tabela).getAllByText("Ana S. · final 4821")).toHaveLength(2);
    expect(screen.getByText(/carteira da Agência Centro/)).toBeInTheDocument();
    expect(apiFalsa.obterCompraFilial).toHaveBeenCalledWith("cmp-000005");
  });

  it("filtra as contestadas e troca a compra do painel ao clicar", async () => {
    render(<PaginaFilaFilial />);
    await screen.findByRole("table");
    await userEvent.click(screen.getByRole("button", { name: /Contestadas/ }));

    const linhas = within(screen.getByRole("table")).getAllByRole("row");
    expect(linhas).toHaveLength(2);
    expect(within(linhas[1]).getByText("Diego P. · final 2288")).toBeInTheDocument();

    await userEvent.click(linhas[1]);
    expect(apiFalsa.obterCompraFilial).toHaveBeenLastCalledWith("cmp-000103");
  });

  it("filtrarFila sem filtro devolve tudo", () => {
    expect(filtrarFila(m.filaFilial.itens, null)).toHaveLength(6);
    expect(filtrarFila(m.filaFilial.itens, "AGUARDANDO")).toHaveLength(2);
    expect(ROTULOS_FILTRO_FILA.AGUARDANDO).toBe("Aguardando associado");
  });
});

describe("PainelCompraFilial", () => {
  it("mostra sinais, explicação, parecer da IA e 'Fraude provável', sem saldo", async () => {
    render(<PainelCompraFilial idCompra="cmp-000005" />);

    expect(await screen.findByText(m.compraFilial.analise.sinais[0].descricao)).toBeInTheDocument();
    expect(screen.getByText(/Fraude provável/)).toBeInTheDocument();
    expect(screen.getByText(/38 compras em 90 dias/)).toBeInTheDocument();
    expect(await screen.findByText(mocks.auditoriaConcluida.relatorio!.explicacao)).toBeInTheDocument();
    expect(screen.queryByText(/saldo/i)).not.toBeInTheDocument();
    expect(screen.queryByText("Ana Souza")).not.toBeInTheDocument();
  });
});

describe("faixa da nota", () => {
  it("usa os cortes do agente", () => {
    expect(faixaDaNota(100)).toBe("alta");
    expect(faixaDaNota(58)).toBe("media");
    expect(faixaDaNota(12)).toBe("baixa");
  });
});
