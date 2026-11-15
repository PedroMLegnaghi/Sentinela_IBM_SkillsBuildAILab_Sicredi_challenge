/**
 * Testes do painel da matriz (seção 17.8).
 */

import { beforeEach, describe, expect, it, vi } from "vitest";
import { act, render, screen, waitFor, within } from "@testing-library/react";
import PaginaPainelMatriz, {
  consolidadoComoFilial,
} from "@/components/matriz/PaginaPainelMatriz";
import SoPapeis from "@/components/layout/SoPapeis";
import { linksDoPapel } from "@/components/layout/MolduraFilial";
import * as api from "@/lib/api";
import { mocksRefatoracao as m } from "@/lib/mocks/refatoracao";
import { guardarSessao, inicioDoPapel, sair } from "@/lib/sessao";
import { ROTULO_TABELA_AGENCIAS, TOTAL_COOPERATIVA } from "@/lib/textos";

const navegar = { push: vi.fn(), replace: vi.fn() };
vi.mock("next/navigation", () => ({ useRouter: () => navegar }));
vi.mock("@/lib/api", () => ({ obterMetricasMatriz: vi.fn() }));

const apiFalsa = vi.mocked(api);

beforeEach(() => {
  vi.clearAllMocks();
  sair();
});

describe("PaginaPainelMatriz", () => {
  it("mostra o consolidado, o modelo na base de teste (sem o sistema atual) e as agências", async () => {
    apiFalsa.obterMetricasMatriz.mockResolvedValue(m.metricasMatriz);
    render(<PaginaPainelMatriz />);

    expect(
      await screen.findByText(/13.608 compras em 2 agências/),
    ).toBeInTheDocument();
    expect(screen.getByText("54 de 54")).toBeInTheDocument();
    expect(screen.getByText("92")).toBeInTheDocument();
    expect(screen.queryByText(/sistema atual/i)).not.toBeInTheDocument();

    const tabela = screen.getByRole("table", { name: ROTULO_TABELA_AGENCIAS });
    const linhas = within(tabela).getAllByRole("row");
    expect(linhas).toHaveLength(4);
    expect(within(linhas[1]).getByText("Agência Centro")).toBeInTheDocument();
    expect(within(linhas[3]).getByText(TOTAL_COOPERATIVA)).toBeInTheDocument();
    expect(within(linhas[3]).getByText("13.608")).toBeInTheDocument();
  });

  it("os bloqueios da equipe mostram a agência de cada auditor", async () => {
    apiFalsa.obterMetricasMatriz.mockResolvedValue(m.metricasMatriz);
    render(<PaginaPainelMatriz />);
    const linha = (await screen.findByText("Tiago Nunes")).closest("tr")!;
    expect(linha).toHaveTextContent("Agência Norte");
  });

  it("sem os arquivos do modelo, o bloco do modelo não aparece", async () => {
    apiFalsa.obterMetricasMatriz.mockResolvedValue({
      ...m.metricasMatriz,
      modelo: null,
    });
    render(<PaginaPainelMatriz />);
    await screen.findByText(/compras em 2 agências/);
    expect(screen.queryByText("54 de 54")).not.toBeInTheDocument();
  });
});

describe("papel matriz", () => {
  it("entra em /matriz e vê painel, desempenho e como funciona", () => {
    expect(inicioDoPapel("matriz")).toBe("/matriz");
    expect(linksDoPapel("matriz").map((l) => l.href)).toEqual([
      "/matriz",
      "/filial/desempenho",
      "/filial/como-funciona",
    ]);
  });

  it("a matriz não abre a fila de uma agência", async () => {
    act(() =>
      guardarSessao({
        token: "t",
        perfil: m.perfis.perfis.find((p) => p.papel === "matriz")!,
      }),
    );
    render(
      <SoPapeis papeis={["auditor", "gerente"]}>
        <p>fila</p>
      </SoPapeis>,
    );
    await waitFor(() =>
      expect(navegar.replace).toHaveBeenCalledWith("/matriz"),
    );
    expect(screen.queryByText("fila")).not.toBeInTheDocument();
  });

  it("o consolidado vira o formato do painel do gerente", () => {
    const c = consolidadoComoFilial(m.metricasMatriz);
    expect(c.totais.compras).toBe(13608);
    expect(c.periodo).toBe("2025-03");
  });
});
