/**
 * Testes do bloco "Pergunte à IA sobre este caso" (Issue #66), com a API simulada.
 */

import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import PergunteIA from "@/components/painel/PergunteIA";
import * as api from "@/lib/api";
import { mocks } from "@/lib/mocks/index";
import { BOTAO_PERGUNTAR, ROTULO_PERGUNTA } from "@/lib/textos";

vi.mock("@/lib/api", () => ({
  perguntarIA: vi.fn(),
}));

const apiFalsa = vi.mocked(api);

beforeEach(() => {
  vi.clearAllMocks();
  apiFalsa.perguntarIA.mockResolvedValue(mocks.pergunta);
});

describe("PergunteIA", () => {
  it("começa com o botão desligado, sem pergunta", () => {
    render(<PergunteIA idTransacao={100001} />);

    expect(
      screen.getByRole("button", { name: BOTAO_PERGUNTAR }),
    ).toBeDisabled();
  });

  it("envia a pergunta e mostra a resposta, as ferramentas e a fonte", async () => {
    const usuario = userEvent.setup();
    render(<PergunteIA idTransacao={100001} />);

    await usuario.type(
      screen.getByRole("textbox", { name: ROTULO_PERGUNTA }),
      "Por que foi bloqueada?",
    );
    await usuario.click(
      screen.getByRole("button", { name: BOTAO_PERGUNTAR }),
    );

    expect(await screen.findByText(mocks.pergunta.resposta)).toBeInTheDocument();
    expect(apiFalsa.perguntarIA).toHaveBeenCalledWith(
      100001,
      "Por que foi bloqueada?",
    );
    expect(screen.getByText(/Sinais da transação/)).toBeInTheDocument();
    expect(screen.getByText(/modo local/)).toBeInTheDocument();
  });

  it("mostra o erro quando a API falha", async () => {
    apiFalsa.perguntarIA.mockRejectedValue(new Error("API fora do ar"));
    const usuario = userEvent.setup();
    render(<PergunteIA idTransacao={100001} />);

    await usuario.type(
      screen.getByRole("textbox", { name: ROTULO_PERGUNTA }),
      "Oi?",
    );
    await usuario.click(
      screen.getByRole("button", { name: BOTAO_PERGUNTAR }),
    );

    expect(await screen.findByText("API fora do ar")).toBeInTheDocument();
  });
});