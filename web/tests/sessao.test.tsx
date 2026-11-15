/**
 * Testes da entrada simulada e das molduras (Issue #91), com a API simulada.
 */

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { act, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import PaginaEntrar from "@/components/sessao/PaginaEntrar";
import MolduraFilial, { linksDoPapel } from "@/components/layout/MolduraFilial";
import { itemAtivo } from "@/components/layout/MolduraAssociado";
import * as api from "@/lib/api";
import { mocksRefatoracao } from "@/lib/mocks/refatoracao";
import { guardarSessao, iniciais, inicioDoPapel, obterSessao, sair } from "@/lib/sessao";
import { ENTRAR_BOTAO, NAV_PAINEL_AGENCIA, NAV_FILA } from "@/lib/textos";

const navegar = { push: vi.fn(), replace: vi.fn() };

vi.mock("next/navigation", () => ({
  useRouter: () => navegar,
  usePathname: () => "/filial/fila",
}));

vi.mock("@/lib/api", () => ({ obterPerfis: vi.fn(), entrar: vi.fn() }));

const apiFalsa = vi.mocked(api);

beforeEach(() => {
  vi.clearAllMocks();
  sair();
});

afterEach(() => sair());

describe("PaginaEntrar", () => {
  it("lista os perfis agrupados e entra como associado", async () => {
    apiFalsa.obterPerfis.mockResolvedValue(mocksRefatoracao.perfis);
    apiFalsa.entrar.mockResolvedValue(mocksRefatoracao.sessaoDe("asc-01"));

    render(<PaginaEntrar />);

    expect(await screen.findByText("Ana Souza")).toBeInTheDocument();
    expect(screen.getByText("Helena Castro")).toBeInTheDocument();
    expect(screen.getByRole("region", { name: "Associados" })).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: ENTRAR_BOTAO }));

    expect(apiFalsa.entrar).toHaveBeenCalledWith("asc-01");
    await waitFor(() => expect(navegar.push).toHaveBeenCalledWith("/associado"));
    expect(obterSessao()?.perfil.nome).toBe("Ana Souza");
  });

  it("entra como gerente e vai para o painel da agência", async () => {
    apiFalsa.obterPerfis.mockResolvedValue(mocksRefatoracao.perfis);
    apiFalsa.entrar.mockResolvedValue(mocksRefatoracao.sessaoDe("ger-01"));

    render(<PaginaEntrar />);

    await userEvent.click(await screen.findByRole("button", { name: /Helena Castro/ }));
    await userEvent.click(screen.getByRole("button", { name: ENTRAR_BOTAO }));

    expect(apiFalsa.entrar).toHaveBeenCalledWith("ger-01");
    await waitFor(() => expect(navegar.push).toHaveBeenCalledWith("/filial/painel"));
  });
});

describe("MolduraFilial", () => {
  it("sem sessão, leva para /entrar", async () => {
    render(
      <MolduraFilial>
        <p>conteúdo</p>
      </MolduraFilial>,
    );
    await waitFor(() => expect(navegar.replace).toHaveBeenCalledWith("/entrar"));
    expect(screen.queryByText("conteúdo")).not.toBeInTheDocument();
  });

  it("associado não entra na filial", async () => {
    act(() => guardarSessao(mocksRefatoracao.sessaoDe("asc-01")));
    render(
      <MolduraFilial>
        <p>conteúdo</p>
      </MolduraFilial>,
    );
    await waitFor(() => expect(navegar.replace).toHaveBeenCalledWith("/associado"));
  });

  it("mostra a agência e os links do auditor", () => {
    act(() => guardarSessao(mocksRefatoracao.sessaoDe("aud-01")));
    render(
      <MolduraFilial>
        <p>conteúdo</p>
      </MolduraFilial>,
    );
    expect(screen.getByText("Agência Centro")).toBeInTheDocument();
    expect(screen.getByText("conteúdo")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: NAV_FILA })).toHaveAttribute("aria-current", "page");
    expect(screen.queryByRole("link", { name: NAV_PAINEL_AGENCIA })).not.toBeInTheDocument();
  });
});

describe("funções de sessão e navegação", () => {
  it("cada papel tem a sua página inicial", () => {
    expect(inicioDoPapel("associado")).toBe("/associado");
    expect(inicioDoPapel("auditor")).toBe("/filial/fila");
    expect(inicioDoPapel("gerente")).toBe("/filial/painel");
  });

  it("o gerente vê o painel e o associado não tem links da filial", () => {
    expect(linksDoPapel("gerente")[0].href).toBe("/filial/painel");
    expect(linksDoPapel("associado")).toEqual([]);
  });

  it("marca o item ativo da navegação do associado", () => {
    expect(itemAtivo("/associado", "/associado")).toBe(true);
    expect(itemAtivo("/associado/extrato", "/associado")).toBe(false);
    expect(itemAtivo("/associado/compras/cmp-1", "/associado/extrato")).toBe(false);
    expect(itemAtivo("/associado/extrato", "/associado/extrato")).toBe(true);
  });

  it("gera as iniciais do nome", () => {
    expect(iniciais("Ana Souza")).toBe("AS");
    expect(iniciais("Helena")).toBe("H");
  });
});
