/**
 * Testes do bloqueio pelo auditor (Issue #103).
 */

import { beforeEach, describe, expect, it, vi } from "vitest";
import { act, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import PainelCompraFilial from "@/components/filial/PainelCompraFilial";
import * as api from "@/lib/api";
import { mocks } from "@/lib/mocks/index";
import { mocksRefatoracao as m } from "@/lib/mocks/refatoracao";
import { guardarSessao, sair } from "@/lib/sessao";
import {
  BLOQUEAR_COMPRA,
  BLOQUEIO_FEITO,
  CONFIRMAR_BLOQUEIO,
  ERRO_BLOQUEIO_409,
  NOTA_DO_AUDITOR,
} from "@/lib/textos";

vi.mock("@/lib/api", () => ({
  obterCompraFilial: vi.fn(),
  obterAuditoria: vi.fn(),
  iniciarAuditoria: vi.fn(),
  bloquearCompra: vi.fn(),
}));

const apiFalsa = vi.mocked(api);
const aguardando = { ...m.compraFilial, compra: m.filaFilial.itens[1], bloqueio: null, resposta_associado: null };

beforeEach(() => {
  vi.clearAllMocks();
  sair();
  apiFalsa.obterAuditoria.mockResolvedValue(mocks.auditoriaConcluida);
});

describe("Bloquear compra", () => {
  it("o auditor bloqueia com nota e o painel mostra o bloqueio", async () => {
    act(() => guardarSessao(m.sessaoDe("aud-01")));
    apiFalsa.obterCompraFilial.mockResolvedValue(aguardando);
    apiFalsa.bloquearCompra.mockResolvedValue(m.compraBloqueadaPeloAuditor);
    render(<PainelCompraFilial idCompra="cmp-000004" />);

    await userEvent.click(await screen.findByRole("button", { name: BLOQUEAR_COMPRA }));
    await userEvent.type(screen.getByLabelText(NOTA_DO_AUDITOR), "  valor alto  ");
    await userEvent.click(screen.getByRole("button", { name: CONFIRMAR_BLOQUEIO }));

    expect(apiFalsa.bloquearCompra).toHaveBeenCalledWith("cmp-000004", "valor alto");
    expect(await screen.findByText(BLOQUEIO_FEITO)).toBeInTheDocument();
    expect(screen.getByText(/Bloqueada por Rafael Moura/)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: BLOQUEAR_COMPRA })).not.toBeInTheDocument();
  });

  it("o gerente não vê o botão", async () => {
    act(() => guardarSessao(m.sessaoDe("ger-01")));
    apiFalsa.obterCompraFilial.mockResolvedValue(aguardando);
    render(<PainelCompraFilial idCompra="cmp-000004" />);
    await screen.findByText(/Sinais de alerta/);
    expect(screen.queryByRole("button", { name: BLOQUEAR_COMPRA })).not.toBeInTheDocument();
  });

  it("compra já bloqueada não tem o botão", async () => {
    act(() => guardarSessao(m.sessaoDe("aud-01")));
    apiFalsa.obterCompraFilial.mockResolvedValue(m.compraFilial);
    render(<PainelCompraFilial idCompra="cmp-000005" />);
    await screen.findByText(/Sinais de alerta/);
    expect(screen.queryByRole("button", { name: BLOQUEAR_COMPRA })).not.toBeInTheDocument();
  });

  it("409 mostra a mensagem em português", async () => {
    act(() => guardarSessao(m.sessaoDe("aud-01")));
    apiFalsa.obterCompraFilial.mockResolvedValue(aguardando);
    apiFalsa.bloquearCompra.mockRejectedValue(new Error("A API retornou um erro (409): x"));
    render(<PainelCompraFilial idCompra="cmp-000004" />);
    await userEvent.click(await screen.findByRole("button", { name: BLOQUEAR_COMPRA }));
    await userEvent.click(screen.getByRole("button", { name: CONFIRMAR_BLOQUEIO }));
    expect(await screen.findByText(ERRO_BLOQUEIO_409)).toBeInTheDocument();
  });
});
