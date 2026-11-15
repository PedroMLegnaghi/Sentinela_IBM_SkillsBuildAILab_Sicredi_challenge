/**
 * Testes de acessibilidade do site Sentinela (Issue #48).
 * Verifica rótulos, texto alternativo, estados sem depender só de cor e foco navegável.
 */

import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import GraficoContribuicoes from "@/components/painel/GraficoContribuicoes";
import FaixaDecisao from "@/components/comuns/FaixaDecisao";
import BarraNota from "@/components/comuns/BarraNota";
import TabelaFila from "@/components/fila/TabelaFila";
import * as api from "@/lib/api";
import { mocks } from "@/lib/mocks/index";

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

describe("GraficoContribuicoes — acessibilidade", () => {
  const contribuicoes = [
    { variavel: "vel_1h", nome: "Uso em terminais", contribuicao: 3.1 },
    { variavel: "valor", nome: "Valor alto", contribuicao: -1.2 },
  ];

  it("exibe texto alternativo para leitores de tela com as contribuições", () => {
    render(<GraficoContribuicoes contribuicoes={contribuicoes} />);

    // O parágrafo sr-only deve conter o nome da variável e a direção do risco
    const srOnly = document.querySelector(".sentinela-sr-only");
    expect(srOnly).not.toBeNull();
    expect(srOnly?.textContent).toContain("Uso em terminais");
    expect(srOnly?.textContent).toContain("aumentou o risco");
    expect(srOnly?.textContent).toContain("Valor alto");
    expect(srOnly?.textContent).toContain("reduziu o risco");
  });

  it("as barras visuais são aria-hidden e o texto numérico permanece visível", () => {
    render(<GraficoContribuicoes contribuicoes={contribuicoes} />);

    // Lista de barras é aria-hidden
    const lista = document.querySelector("ul.sentinela-contribuicoes");
    expect(lista?.getAttribute("aria-hidden")).toBe("true");

    // Mas os valores numéricos ainda são exibidos (dentro da lista aria-hidden,
    // leitores de tela já usam o parágrafo sr-only)
    expect(screen.getAllByText(/3,10/)[0]).toBeInTheDocument();
  });

  it("mostra mensagem sem contribuições quando a lista está vazia", () => {
    render(<GraficoContribuicoes contribuicoes={[]} />);
    expect(
      screen.getByText(/ainda não estão disponíveis/i),
    ).toBeInTheDocument();
  });
});

describe("FaixaDecisao — estado não depende só de cor", () => {
  it("BLOQUEAR exibe ícone e texto além da cor", () => {
    render(<FaixaDecisao decisao="BLOQUEAR" />);
    // Ícone simbólico presente no texto
    expect(screen.getByText(/⛔/)).toBeInTheDocument();
    // Texto legível
    expect(screen.getByText(/Bloquear e enviar ao analista/i)).toBeInTheDocument();
  });

  it("PEDIR_CONFIRMACAO exibe ícone e texto além da cor", () => {
    render(<FaixaDecisao decisao="PEDIR_CONFIRMACAO" />);
    expect(screen.getByText(/⚠️/)).toBeInTheDocument();
    expect(screen.getByText(/Pedir confirmação ao cliente/i)).toBeInTheDocument();
  });

  it("APROVAR exibe ícone e texto além da cor", () => {
    render(<FaixaDecisao decisao="APROVAR" />);
    expect(screen.getByText(/✅/)).toBeInTheDocument();
    expect(screen.getByText(/Aprovar/i)).toBeInTheDocument();
  });

  it("tem texto descritivo acessível no DOM (aria-label na faixa ou texto visível)", () => {
    const { container } = render(<FaixaDecisao decisao="BLOQUEAR" />);
    // FaixaDecisao exibe sempre texto visível + ícone — sem depender só de cor.
    // Verifica que existe pelo menos um elemento com aria-label contendo "Bloquear".
    const comAriaLabel = container.querySelector("[aria-label*='Bloquear']");
    const textoDecisao = screen.queryByText(/Bloquear/i);
    expect(comAriaLabel ?? textoDecisao).not.toBeNull();
  });
});

describe("BarraNota — acessibilidade", () => {
  it("tem role meter com aria-valuenow correto", () => {
    render(<BarraNota nota={72} />);
    const barra = screen.getByRole("meter");
    expect(barra).toHaveAttribute("aria-valuenow", "72");
    expect(barra).toHaveAttribute("aria-valuemin", "0");
    expect(barra).toHaveAttribute("aria-valuemax", "100");
  });

  it("aria-label informa a nota para leitores de tela", () => {
    render(<BarraNota nota={72} />);
    const barra = screen.getByRole("meter");
    expect(barra).toHaveAttribute(
      "aria-label",
      expect.stringContaining("72"),
    );
  });
});

describe("TabelaFila — acessibilidade", () => {
  it("tabela tem aria-label descritivo", () => {
    render(
      <TabelaFila
        itens={mocks.fila.itens.slice(0, 3)}
        total={mocks.fila.total_fila}
        idSelecionado={null}
        aoSelecionar={() => {}}
      />,
    );
    const tabela = screen.getByRole("table");
    expect(tabela).toHaveAttribute("aria-label");
  });

  it("botão de abrir transação tem aria-label com o ID", () => {
    const item = mocks.fila.itens[0];
    render(
      <TabelaFila
        itens={[item]}
        total={1}
        idSelecionado={null}
        aoSelecionar={() => {}}
      />,
    );
    const botao = screen.getByRole("button", {
      name: new RegExp(`${item.id_transacao}`),
    });
    expect(botao).toBeInTheDocument();
  });

  it("colunas de cabeçalho têm scope col", () => {
    render(
      <TabelaFila
        itens={mocks.fila.itens.slice(0, 1)}
        total={mocks.fila.total_fila}
        idSelecionado={null}
        aoSelecionar={() => {}}
      />,
    );
    const ths = document.querySelectorAll("thead th");
    ths.forEach((th) => {
      expect(th).toHaveAttribute("scope", "col");
    });
  });
});
