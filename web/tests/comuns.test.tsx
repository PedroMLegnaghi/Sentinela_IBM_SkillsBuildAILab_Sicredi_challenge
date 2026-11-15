/**
 * Testes dos componentes comuns do site Sentinela.
 */

import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import FaixaDecisao from "@/components/comuns/FaixaDecisao";
import BarraNota from "@/components/comuns/BarraNota";
import EstadoCarregando from "@/components/comuns/EstadoCarregando";
import EstadoVazio from "@/components/comuns/EstadoVazio";
import EstadoErro from "@/components/comuns/EstadoErro";

describe("FaixaDecisao", () => {
  it("exibe ícone e texto para decisão BLOQUEAR", () => {
    render(<FaixaDecisao decisao="BLOQUEAR" />);
    expect(screen.getByRole("status")).toBeInTheDocument();
    const texto = screen.getByText(/Bloquear e enviar ao analista/i);
    expect(texto).toBeInTheDocument();
  });

  it("exibe ícone e texto para decisão PEDIR_CONFIRMACAO", () => {
    render(<FaixaDecisao decisao="PEDIR_CONFIRMACAO" />);
    const texto = screen.getByText(/Pedir confirmação ao cliente/i);
    expect(texto).toBeInTheDocument();
  });

  it("exibe ícone e texto para decisão APROVAR", () => {
    render(<FaixaDecisao decisao="APROVAR" />);
    const texto = screen.getByText(/Aprovar/i);
    expect(texto).toBeInTheDocument();
  });

  it("usa decisaoLegivel quando fornecido", () => {
    render(
      <FaixaDecisao
        decisao="BLOQUEAR"
        decisaoLegivel="Texto customizado de decisão"
      />,
    );
    expect(screen.getByText(/Texto customizado de decisão/i)).toBeInTheDocument();
  });
});

describe("BarraNota", () => {
  it("exibe a nota formatada em pt-BR", () => {
    render(<BarraNota nota={97.3} />);
    expect(screen.getByText(/97,3/)).toBeInTheDocument();
  });

  it("exibe aria-label com a nota", () => {
    render(<BarraNota nota={50.0} />);
    const barra = screen.getByRole("meter");
    expect(barra).toHaveAttribute("aria-label", expect.stringContaining("50,0"));
  });

  it("exibe nota zero", () => {
    render(<BarraNota nota={0} />);
    expect(screen.getByRole("meter")).toHaveAttribute("aria-valuenow", "0");
  });
});

describe("EstadoCarregando", () => {
  it("exibe mensagem padrão de carregamento", () => {
    render(<EstadoCarregando />);
    expect(screen.getByRole("status")).toBeInTheDocument();
  });

  it("exibe mensagem personalizada", () => {
    render(<EstadoCarregando mensagem="Buscando dados…" />);
    // Carbon Loading renderiza o texto como título SVG e como span; usa getAllByText
    const elementos = screen.getAllByText("Buscando dados…");
    expect(elementos.length).toBeGreaterThan(0);
  });
});

describe("EstadoVazio", () => {
  it("exibe mensagem padrão de vazio", () => {
    render(<EstadoVazio />);
    expect(screen.getByRole("status")).toBeInTheDocument();
  });

  it("exibe mensagem personalizada", () => {
    render(<EstadoVazio mensagem="Nenhuma transação encontrada." />);
    expect(
      screen.getByText("Nenhuma transação encontrada."),
    ).toBeInTheDocument();
  });
});

describe("EstadoErro", () => {
  it("exibe mensagem de erro", () => {
    render(<EstadoErro mensagem="Falha ao carregar dados." />);
    expect(screen.getByRole("alert")).toBeInTheDocument();
    expect(screen.getByText("Falha ao carregar dados.")).toBeInTheDocument();
  });

  it("não exibe botão Tentar de novo quando aoTentarNovamente não é passado", () => {
    render(<EstadoErro mensagem="Erro genérico." />);
    expect(
      screen.queryByRole("button", { name: /tentar de novo/i }),
    ).not.toBeInTheDocument();
  });

  it("exibe botão Tentar de novo quando aoTentarNovamente é passado", () => {
    render(
      <EstadoErro
        mensagem="Erro com retry."
        aoTentarNovamente={() => {}}
      />,
    );
    expect(
      screen.getByRole("button", { name: /tentar de novo/i }),
    ).toBeInTheDocument();
  });
});
