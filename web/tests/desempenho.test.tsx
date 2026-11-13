/**
 * Testes das páginas Desempenho e Como funciona (Issue #44), com a API simulada.
 */

import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import PaginaComoFunciona from "@/components/como-funciona/PaginaComoFunciona";
import PaginaDesempenho from "@/components/desempenho/PaginaDesempenho";
import SecaoCustos from "@/components/desempenho/SecaoCustos";
import * as api from "@/lib/api";
import { mocks } from "@/lib/mocks/index";
import { SINAIS_EXPLICADOS, TITULO_IA_CONTRA_MODELO } from "@/lib/textos";

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
  it("lista os 9 sinais de alerta", () => {
    render(<PaginaComoFunciona />);

    expect(SINAIS_EXPLICADOS).toHaveLength(9);
    expect(screen.getByText("Salto geográfico")).toBeInTheDocument();
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
