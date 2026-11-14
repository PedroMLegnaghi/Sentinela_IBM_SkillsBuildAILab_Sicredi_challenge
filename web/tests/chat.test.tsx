/**
 * Testes do chat do associado e do "conversar com gerente" (Issue #106).
 */

import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import PaginaChat, { historicoParaApi, LIMITE_HISTORICO } from "@/components/associado/PaginaChat";
import * as api from "@/lib/api";
import { mocksRefatoracao as m } from "@/lib/mocks/refatoracao";
import {
  AVISO_GERENTE_SIMULADO,
  CAMPO_CHAT,
  CONVERSAR_COM_GERENTE,
  ENVIAR,
  ERRO_CHAT,
  FONTE_CHAT,
  SUGESTOES_CHAT,
} from "@/lib/textos";

vi.mock("@/lib/api", () => ({ perguntarAoChat: vi.fn(), chamarGerente: vi.fn() }));

const apiFalsa = vi.mocked(api);

beforeEach(() => vi.clearAllMocks());

describe("PaginaChat", () => {
  it("envia a pergunta digitada e mostra a resposta com a fonte", async () => {
    apiFalsa.perguntarAoChat.mockResolvedValue(m.respostaChat);
    render(<PaginaChat />);

    await userEvent.type(screen.getByLabelText(CAMPO_CHAT), "Quanto gastei?");
    await userEvent.click(screen.getByRole("button", { name: ENVIAR }));

    expect(apiFalsa.perguntarAoChat).toHaveBeenCalledWith({ mensagem: "Quanto gastei?", historico: [] });
    expect(await screen.findByText(m.respostaChat.resposta)).toBeInTheDocument();
    expect(screen.getByText(FONTE_CHAT.local)).toBeInTheDocument();
  });

  it("a sugestão pergunta direto e manda o histórico na pergunta seguinte", async () => {
    apiFalsa.perguntarAoChat.mockResolvedValue(m.respostaChat);
    render(<PaginaChat />);

    await userEvent.click(screen.getByRole("button", { name: SUGESTOES_CHAT[1] }));
    await screen.findByText(m.respostaChat.resposta);
    await userEvent.type(screen.getByLabelText(CAMPO_CHAT), "E agora?");
    await userEvent.click(screen.getByRole("button", { name: ENVIAR }));

    expect(apiFalsa.perguntarAoChat).toHaveBeenLastCalledWith({
      mensagem: "E agora?",
      historico: [
        { autor: "associado", texto: SUGESTOES_CHAT[1] },
        { autor: "ia", texto: m.respostaChat.resposta },
      ],
    });
  });

  it("erro da API vira uma mensagem amigável", async () => {
    apiFalsa.perguntarAoChat.mockRejectedValue(new Error("falhou"));
    render(<PaginaChat />);
    await userEvent.click(screen.getByRole("button", { name: SUGESTOES_CHAT[0] }));
    expect(await screen.findByText(ERRO_CHAT)).toBeInTheDocument();
  });

  it("conversar com gerente troca o cabeçalho, mostra o resumo e encerra o campo", async () => {
    apiFalsa.chamarGerente.mockResolvedValue(m.resumoGerente);
    render(<PaginaChat />);

    await userEvent.click(screen.getByRole("button", { name: CONVERSAR_COM_GERENTE }));

    expect(await screen.findByText(m.resumoGerente.resumo)).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /Helena Castro · gerente da agência/ })).toBeInTheDocument();
    expect(screen.getByText(AVISO_GERENTE_SIMULADO)).toBeInTheDocument();
    expect(screen.queryByLabelText(CAMPO_CHAT)).not.toBeInTheDocument();
  });
});

describe("historicoParaApi", () => {
  it("tira o gerente e limita aos 20 mais recentes", () => {
    const muitas = Array.from({ length: 25 }, (_, i) => ({ autor: "associado" as const, texto: `p${i}` }));
    const historico = historicoParaApi([...muitas, { autor: "gerente", texto: "oi" }]);
    expect(historico).toHaveLength(LIMITE_HISTORICO);
    expect(historico.at(-1)).toEqual({ autor: "associado", texto: "p24" });
  });
});
