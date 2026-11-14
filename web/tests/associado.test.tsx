/**
 * Testes do app do associado (Issue #63), com a API simulada.
 */

import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import ListaNotificacoes from "@/components/associado/ListaNotificacoes";
import ItemNotificacao from "@/components/associado/ItemNotificacao";
import * as api from "@/lib/api";
import { mocks } from "@/lib/mocks/index";
import {
  BOTAO_NAO_FUI_EU,
  BOTAO_SIM_FUI_EU,
  ERRO_RESPOSTA_409,
  SEM_NOTIFICACOES,
} from "@/lib/textos";
import type { Notificacao } from "@/lib/tipos";

vi.mock("@/lib/api", () => ({
  obterNotificacoes: vi.fn(),
  responderNotificacao: vi.fn(),
  notificarAssociado: vi.fn(),
}));

const apiFalsa = vi.mocked(api);

beforeEach(() => {
  vi.clearAllMocks();
});

describe("ListaNotificacoes", () => {
  it("mostra notificações quando há itens", async () => {
    apiFalsa.obterNotificacoes.mockResolvedValue(mocks.notificacoes);

    render(<ListaNotificacoes />);

    expect(
      await screen.findByText(mocks.notificacaoAguardando.mensagem),
    ).toBeInTheDocument();
  });

  it("mostra mensagem quando não há notificações", async () => {
    apiFalsa.obterNotificacoes.mockResolvedValue({ itens: [] });

    render(<ListaNotificacoes />);

    expect(await screen.findByText(SEM_NOTIFICACOES)).toBeInTheDocument();
  });
});

describe("ItemNotificacao", () => {
  const aoResponder = vi.fn();

  it("mostra os botões quando status é aguardando", () => {
    render(
      <ItemNotificacao
        notificacao={mocks.notificacaoAguardando}
        aoResponder={aoResponder}
      />,
    );

    expect(
      screen.getByRole("button", { name: BOTAO_SIM_FUI_EU }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: BOTAO_NAO_FUI_EU }),
    ).toBeInTheDocument();
  });

  it("ao responder não, chama aoResponder com a notificação atualizada", async () => {
    const usuario = userEvent.setup();
    const notificacaoAtualizada: Notificacao = {
      ...mocks.notificacaoAguardando,
      status: "negada",
      respondida_em: "2025-03-15T14:40:00",
      resultado:
        "Compra bloqueada e cartão protegido. O caso foi para o analista.",
    };
    apiFalsa.responderNotificacao.mockResolvedValue(notificacaoAtualizada);

    render(
      <ItemNotificacao
        notificacao={mocks.notificacaoAguardando}
        aoResponder={aoResponder}
      />,
    );

    await usuario.click(screen.getByRole("button", { name: BOTAO_NAO_FUI_EU }));

    expect(aoResponder).toHaveBeenCalledWith(notificacaoAtualizada);
  });

  it("botões somem depois que a notificação é respondida", () => {
    render(
      <ItemNotificacao
        notificacao={mocks.notificacaoNegada}
        aoResponder={aoResponder}
      />,
    );

    expect(
      screen.queryByRole("button", { name: BOTAO_SIM_FUI_EU }),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: BOTAO_NAO_FUI_EU }),
    ).not.toBeInTheDocument();
  });

  it("mostra o resultado depois de respondida", () => {
    render(
      <ItemNotificacao
        notificacao={mocks.notificacaoNegada}
        aoResponder={aoResponder}
      />,
    );

    expect(
      screen.getByText(mocks.notificacaoNegada.resultado!),
    ).toBeInTheDocument();
  });

  it("erro 409 mostra mensagem em português", async () => {
    const usuario = userEvent.setup();
    apiFalsa.responderNotificacao.mockRejectedValue(
      new Error("A API retornou um erro (409): já respondida"),
    );

    render(
      <ItemNotificacao
        notificacao={mocks.notificacaoAguardando}
        aoResponder={aoResponder}
      />,
    );

    await usuario.click(screen.getByRole("button", { name: BOTAO_SIM_FUI_EU }));

    expect(
      await screen.findByText(ERRO_RESPOSTA_409),
    ).toBeInTheDocument();
  });
});
