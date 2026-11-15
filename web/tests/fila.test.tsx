/**
 * Testes da auditoria por IA e do gráfico de contribuições, reaproveitados no painel da filial.
 */

import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import CartaoAuditoria from "@/components/painel/CartaoAuditoria";
import GraficoContribuicoes from "@/components/painel/GraficoContribuicoes";
import * as api from "@/lib/api";
import { mocks } from "@/lib/mocks/index";
import {
  AUDITORIA_PENDENTE,
  TENTAR_NOVAMENTE,
} from "@/lib/textos";

vi.mock("@/lib/api", () => ({
  obterFila: vi.fn(),
  obterTransacao: vi.fn(),
  iniciarAuditoria: vi.fn(),
  obterAuditoria: vi.fn(),
  registrarResposta: vi.fn(),
}));

const apiFalsa = vi.mocked(api);

beforeEach(() => {
  vi.clearAllMocks();
  apiFalsa.obterFila.mockResolvedValue(mocks.fila);
  apiFalsa.obterTransacao.mockResolvedValue(mocks.transacao);
  apiFalsa.iniciarAuditoria.mockResolvedValue(mocks.auditoriaIniciada);
  apiFalsa.obterAuditoria.mockResolvedValue(mocks.auditoriaConcluida);
});

describe("CartaoAuditoria", () => {
  it("mostra o carregando enquanto a auditoria está pendente", async () => {
    apiFalsa.obterAuditoria.mockReturnValue(new Promise(() => {}));

    render(<CartaoAuditoria idTransacao={1} />);

    expect(await screen.findByText(AUDITORIA_PENDENTE)).toBeInTheDocument();
  });

  it("mostra o erro e tenta de novo", async () => {
    const usuario = userEvent.setup();
    apiFalsa.obterAuditoria.mockResolvedValueOnce({
      ...mocks.auditoriaConcluida,
      status: "erro",
      relatorio: null,
      mensagem: "Falha inventada.",
    });

    render(<CartaoAuditoria idTransacao={1} />);
    await usuario.click(await screen.findByText(TENTAR_NOVAMENTE));

    await waitFor(() =>
      expect(apiFalsa.iniciarAuditoria).toHaveBeenCalledTimes(2),
    );
  });

  it("lista as ferramentas na ordem em que a IA usou", async () => {
    render(<CartaoAuditoria idTransacao={1} />);

    const itens = await screen.findAllByText(/: /, { selector: "li" });
    expect(itens[0]).toHaveTextContent("Sinais da transação");
  });
});

describe("GraficoContribuicoes", () => {
  it("mostra o sinal de cada contribuição", () => {
    render(
      <GraficoContribuicoes
        contribuicoes={[
          { variavel: "a", nome: "Rajada inventada", contribuicao: 2.5 },
          { variavel: "b", nome: "Valor inventado", contribuicao: -1.25 },
        ]}
      />,
    );

    expect(screen.getByText("+2,50")).toBeInTheDocument();
    expect(screen.getByText("−1,25")).toBeInTheDocument();
  });
});
