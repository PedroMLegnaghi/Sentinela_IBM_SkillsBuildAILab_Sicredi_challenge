/**
 * Testes das páginas Desempenho e Como funciona da filial (Issues #44 e #100), com a API simulada.
 */

import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import PaginaComoFunciona from "@/components/como-funciona/PaginaComoFunciona";
import PaginaDesempenho from "@/components/desempenho/PaginaDesempenho";
import SecaoCustos from "@/components/desempenho/SecaoCustos";
import * as api from "@/lib/api";
import { mocks } from "@/lib/mocks/index";
import {
  PASSOS_CAMINHO,
  PRIVACIDADE_COMO,
  SINAIS_EXPLICADOS,
  TITULO_IA_CONTRA_MODELO,
  TITULO_PRIVACIDADE_COMO,
} from "@/lib/textos";

vi.mock("@/lib/api", () => ({ obterMetricas: vi.fn() }));

const apiFalsa = vi.mocked(api);

beforeEach(() => {
  vi.clearAllMocks();
  apiFalsa.obterMetricas.mockResolvedValue(mocks.metricas);
});

describe("PaginaDesempenho", () => {
  it("mostra os indicadores de março com a diferença para o sistema atual", async () => {
    render(<PaginaDesempenho />);

    expect(
      await screen.findByText("+28 em relação ao sistema atual"),
    ).toBeInTheDocument();
    expect(screen.getAllByText("54 de 54").length).toBeGreaterThan(0);
    expect(screen.getAllByText("26 de 54").length).toBeGreaterThan(0);
    expect(screen.getByText("48,1%")).toBeInTheDocument();
  });

  it("mostra o modelo e a IA lado a lado quando o JSON da #46 existe", async () => {
    render(<PaginaDesempenho />);

    expect(
      await screen.findByText(TITULO_IA_CONTRA_MODELO),
    ).toBeInTheDocument();
  });

  it("esconde a seção da IA quando o JSON da #46 não existe", async () => {
    apiFalsa.obterMetricas.mockResolvedValue({
      ...mocks.metricas,
      extras: { ...mocks.metricas.extras, ia_contra_modelo: null },
    });

    render(<PaginaDesempenho />);
    await screen.findByText("+28 em relação ao sistema atual");

    expect(screen.queryByText(TITULO_IA_CONTRA_MODELO)).not.toBeInTheDocument();
  });

  it("mostra o erro quando a API falha", async () => {
    apiFalsa.obterMetricas.mockRejectedValue(new Error("Falha inventada."));

    render(<PaginaDesempenho />);

    expect(await screen.findByText("Falha inventada.")).toBeInTheDocument();
  });
});

describe("Barras da comparação", () => {
  it("usam as cores da identidade Sicredi", async () => {
    const { container } = render(<PaginaDesempenho />);
    await screen.findByText("+28 em relação ao sistema atual");

    const barras = container.querySelectorAll(
      ".sentinela-barras-trilho > span",
    );

    expect((barras[0] as HTMLElement).style.backgroundColor).toBe(
      "var(--sc-verde)",
    );
    expect((barras[1] as HTMLElement).style.backgroundColor).toBe(
      "var(--sc-texto-apoio)",
    );
  });
});

describe("Rotas das duas páginas", () => {
  const app = (caminho: string) => resolve(__dirname, "../app", caminho);

  it("ficam dentro da área da filial", () => {
    expect(existsSync(app("filial/desempenho/page.tsx"))).toBe(true);
    expect(existsSync(app("filial/como-funciona/page.tsx"))).toBe(true);
  });

  it("não existem mais fora da filial", () => {
    expect(existsSync(app("desempenho"))).toBe(false);
    expect(existsSync(app("como-funciona"))).toBe(false);
  });

  it("aparecem no menu da filial com os caminhos novos", () => {
    const moldura = readFileSync(
      resolve(__dirname, "../components/layout/MolduraFilial.tsx"),
      "utf-8",
    );

    expect(moldura).toContain('"/filial/desempenho"');
    expect(moldura).toContain('"/filial/como-funciona"');
  });
});

describe("SecaoCustos", () => {
  it("mostra o prejuízo evitado em reais", () => {
    render(
      <SecaoCustos
        custos={{
          prejuizo_evitado: 1234.5,
          sentinela: { custo_total: 159 },
          sistema_atual: { custo_total: 1393.5 },
        }}
      />,
    );

    expect(screen.getByText("R$ 1.234,50")).toBeInTheDocument();
  });

  it("não aparece quando falta um campo", () => {
    const { container } = render(
      <SecaoCustos custos={{ prejuizo_evitado: 10 }} />,
    );

    expect(container).toBeEmptyDOMElement();
  });
});

describe("PaginaComoFunciona", () => {
  it("conta a história em quatro passos, do associado à filial", () => {
    render(<PaginaComoFunciona />);

    const passos = screen
      .getAllByRole("listitem")
      .slice(0, 4)
      .map((li) => li.textContent);

    expect(PASSOS_CAMINHO).toHaveLength(4);
    expect(passos).toEqual(PASSOS_CAMINHO);
    expect(passos[0]).toContain("associado faz a compra");
    expect(passos[1]).toContain("decide na hora");
    expect(passos[2]).toContain("IA audita");
    expect(passos[3]).toContain("filial acompanha");
  });

  it("lista os 9 sinais de alerta", () => {
    render(<PaginaComoFunciona />);

    expect(SINAIS_EXPLICADOS).toHaveLength(9);
    expect(screen.getByText("Salto geográfico")).toBeInTheDocument();
  });

  it("mostra a seção de privacidade com os números de experiência", () => {
    render(<PaginaComoFunciona />);

    expect(screen.getByText(TITULO_PRIVACIDADE_COMO)).toBeInTheDocument();
    expect(PRIVACIDADE_COMO.length).toBeGreaterThanOrEqual(3);
    const textoCompleto = PRIVACIDADE_COMO.join(" ");
    expect(textoCompleto).toContain("159");
    expect(textoCompleto).toContain("13.608");
    expect(textoCompleto).toContain("0");
  });

  it("usa os mesmos limiares de src/config.py", () => {
    const config = readFileSync(
      resolve(__dirname, "../../src/config.py"),
      "utf-8",
    );
    const valor = (nome: string) =>
      config.match(new RegExp(`^${nome} = (\\d+)`, "m"))?.[1];
    const textos = SINAIS_EXPLICADOS.map(([, quando]) => quando).join(" | ");

    for (const nome of [
      "LIMIAR_VELOCIDADE_TERMINAL",
      "LIMIAR_RAJADA_1MIN",
      "LIMIAR_TOKEN_CARTEIRA",
      "LIMIAR_DISTANCIA_KM",
      "HORA_FIM_MADRUGADA",
      "LIMIAR_VALOR_ALTO",
      "LIMIAR_RISCO_ESTABELECIMENTO",
    ]) {
      expect(textos).toContain(valor(nome));
    }
  });
});
