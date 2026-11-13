/**
 * Testes da fila de alertas e do painel da transação (Issue #43), com a API simulada.
 */

import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import PaginaFila from "@/components/fila/PaginaFila";
import CartaoAuditoria from "@/components/painel/CartaoAuditoria";
import GraficoContribuicoes from "@/components/painel/GraficoContribuicoes";
import RespostaAnalista from "@/components/painel/RespostaAnalista";
import * as api from "@/lib/api";
import { mocks } from "@/lib/mocks/index";
import {
  AUDITORIA_PENDENTE,
  FILTRO_VAZIO,
  ROTULO_TABELA_FILA,
  ROTULOS_PARECER,
  SEM_RESPOSTA,
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

describe("PaginaFila", () => {
  it("mostra os indicadores da fila inteira", async () => {
    render(<PaginaFila />);

    expect(await screen.findByText("2.054")).toBeInTheDocument();
  });

  it("abre só com Bloquear e Pedir confirmação na tabela", async () => {
    render(<PaginaFila />);
    await screen.findByText("2.054");

    const tabela = screen.getByRole("table", { name: ROTULO_TABELA_FILA });
    const linhas = within(tabela).getAllByRole("row").slice(1);
    const aprovadas = mocks.fila.itens.filter(
      (i) => i.decisao === "APROVAR",
    ).length;
    expect(linhas).toHaveLength(mocks.fila.itens.length - aprovadas);
  });

  it("mostra a mensagem de filtro vazio quando nenhuma decisão está marcada", async () => {
    const usuario = userEvent.setup();
    render(<PaginaFila />);
    await screen.findByText("2.054");

    await usuario.click(screen.getByLabelText("Bloquear"));
    await usuario.click(screen.getByLabelText("Pedir confirmação"));

    expect(screen.getByText(FILTRO_VAZIO)).toBeInTheDocument();
  });

  it("abre o painel com a decisão do modelo e o parecer da IA", async () => {
    render(<PaginaFila />);

    expect(await screen.findByText(/Transação 100001/)).toBeInTheDocument();
    expect(
      await screen.findByText(new RegExp(ROTULOS_PARECER.CONFIRMA)),
    ).toBeInTheDocument();
  });
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

describe("RespostaAnalista", () => {
  it("grava a resposta e mostra a resposta atual", async () => {
    const usuario = userEvent.setup();
    apiFalsa.registrarResposta.mockResolvedValue({
      id_transacao: 7,
      resposta: "fraude",
      registrado_em: "2025-03-15T10:00:00",
    });

    render(<RespostaAnalista idTransacao={7} respostaInicial={null} />);
    expect(screen.getByText(SEM_RESPOSTA)).toBeInTheDocument();
    await usuario.click(
      screen.getByRole("button", { name: "Confirmar fraude" }),
    );

    expect(apiFalsa.registrarResposta).toHaveBeenCalledWith({
      id_transacao: 7,
      resposta: "fraude",
    });
    expect(
      await screen.findByText(/Fraude confirmada em 15\/03\/2025 10:00/),
    ).toBeInTheDocument();
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
