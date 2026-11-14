/**
 * Testes do simulador e da página de respostas (Issue #45) e dos cenários prontos (Issue #110),
 * com a API simulada.
 */

import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import PaginaRespostas from "@/components/respostas/PaginaRespostas";
import PaginaSimulador from "@/components/simulador/PaginaSimulador";
import * as api from "@/lib/api";
import { mocks } from "@/lib/mocks/index";
import {
  CENARIOS,
  gerarCsvRespostas,
  montarEntradaSimulada,
  valoresIniciais,
} from "@/lib/simulacao";
import {
  BOTAO_ANALISAR,
  RESPOSTAS_VAZIAS,
  TITULO_SIMULADA,
} from "@/lib/textos";

vi.mock("@/lib/api", () => ({
  obterFila: vi.fn(),
  obterTransacao: vi.fn(),
  analisar: vi.fn(),
  iniciarAuditoria: vi.fn(),
  obterAuditoria: vi.fn(),
  obterRespostas: vi.fn(),
}));

const apiFalsa = vi.mocked(api);

beforeEach(() => {
  vi.clearAllMocks();
  apiFalsa.obterFila.mockResolvedValue(mocks.fila);
  apiFalsa.obterTransacao.mockResolvedValue(mocks.transacao);
  apiFalsa.analisar.mockResolvedValue(mocks.analisar);
  apiFalsa.obterAuditoria.mockResolvedValue(mocks.auditoriaConcluida);
  apiFalsa.obterRespostas.mockResolvedValue(mocks.respostas);
});

describe("lógica do simulador", () => {
  it("recalcula a madrugada pela hora, sem edição manual", () => {
    const valores = { ...valoresIniciais(mocks.transacao.transacao), hora: 3 };

    const entrada = montarEntradaSimulada(mocks.transacao.transacao, valores);

    expect(entrada.madrugada).toBe(1);
    expect(
      montarEntradaSimulada(mocks.transacao.transacao, { ...valores, hora: 14 })
        .madrugada,
    ).toBe(0);
  });

  it("converte as chaves em 0 ou 1 e sempre pede a auditoria", () => {
    const valores = {
      ...valoresIniciais(mocks.transacao.transacao),
      credito: false,
    };

    const entrada = montarEntradaSimulada(mocks.transacao.transacao, valores);

    expect(entrada.credito).toBe(0);
    expect(entrada.tipo_transacao).toBe("debito");
    expect(entrada.auditar).toBe(true);
  });

  it("gera o CSV das respostas com cabeçalho", () => {
    const csv = gerarCsvRespostas(mocks.respostas.itens);

    expect(csv.split("\n")[0]).toBe(
      "id_transacao,resposta,registrado_em,decisao,nota",
    );
    expect(csv).toContain("100001,fraude,2025-03-15T10:00:00,BLOQUEAR,97.3");
  });
});

describe("PaginaSimulador", () => {
  it("analisa a compra simulada e mostra o resultado ao lado do original", async () => {
    const usuario = userEvent.setup();
    render(<PaginaSimulador />);

    await usuario.click(
      await screen.findByRole("button", { name: BOTAO_ANALISAR }),
    );

    expect(await screen.findByText(TITULO_SIMULADA)).toBeInTheDocument();
    expect(apiFalsa.analisar).toHaveBeenCalledTimes(1);
  });
});

describe("cenários prontos", () => {
  it.each(CENARIOS)(
    "o botão $nome preenche os campos e analisa",
    async (cenario) => {
      const usuario = userEvent.setup();
      render(<PaginaSimulador />);

      await usuario.click(
        await screen.findByRole("button", { name: cenario.nome }),
      );

      await waitFor(() =>
        expect(apiFalsa.analisar).toHaveBeenCalledWith(
          montarEntradaSimulada(mocks.transacao.transacao, cenario.valores),
        ),
      );
    },
  );
});

describe("PaginaRespostas", () => {
  it("mostra o resumo e a concordância", async () => {
    render(<PaginaRespostas />);

    expect(await screen.findByText("66,7%")).toBeInTheDocument();
  });

  it("mostra o estado vazio sem respostas", async () => {
    apiFalsa.obterRespostas.mockResolvedValue({
      total: 0,
      fraudes: 0,
      legitimas: 0,
      concordancia: null,
      itens: [],
    });

    render(<PaginaRespostas />);

    expect(await screen.findByText(RESPOSTAS_VAZIAS)).toBeInTheDocument();
  });
});