/**
 * Testes do painel do gerente (Issue #99).
 */

import { beforeEach, describe, expect, it, vi } from "vitest";
import { act, render, screen, waitFor } from "@testing-library/react";
import PaginaPainelAgencia from "@/components/gerente/PaginaPainelAgencia";
import SoGerente from "@/components/gerente/SoGerente";
import * as api from "@/lib/api";
import { mocksRefatoracao as m } from "@/lib/mocks/refatoracao";
import { guardarSessao, sair } from "@/lib/sessao";
import { formatarTempoCurto } from "@/lib/formatacao";
import { SEM_RESPOSTAS_AINDA } from "@/lib/textos";

const navegar = { push: vi.fn(), replace: vi.fn() };
vi.mock("next/navigation", () => ({ useRouter: () => navegar }));
vi.mock("@/lib/api", () => ({ obterMetricasFilial: vi.fn() }));

const apiFalsa = vi.mocked(api);

beforeEach(() => {
  vi.clearAllMocks();
  sair();
});

describe("PaginaPainelAgencia", () => {
  it("mostra os indicadores, a taxa de acerto e as fraudes aprovadas", async () => {
    apiFalsa.obterMetricasFilial.mockResolvedValue(m.metricasFilial);
    render(<PaginaPainelAgencia />);

    expect(await screen.findByText("6.698")).toBeInTheDocument();
    expect(screen.getByText("79")).toBeInTheDocument();
    expect(screen.getByText("R$ 3.248,10 protegidos")).toBeInTheDocument();
    expect(screen.getByText("4 min")).toBeInTheDocument();
    expect(screen.getByRole("img", { name: /acertou 87%/ })).toBeInTheDocument();
    expect(screen.getByText("Diego P. · final 2288")).toBeInTheDocument();
    expect(
      screen.getByRole("img", { name: /Crédito, sem cartão: 1.170 aprovadas, 22 pedidos de confirmação e 22 bloqueadas/ }),
    ).toBeInTheDocument();
  });

  it("sem respostas, mostra o estado vazio no lugar da rosca", async () => {
    apiFalsa.obterMetricasFilial.mockResolvedValue({
      ...m.metricasFilial,
      acerto_modelo: { alertas_certos: 0, alertas_desnecessarios: 0, sem_resposta: 5, taxa: null },
      tempo_resposta_mediano_s: null,
    });
    render(<PaginaPainelAgencia />);
    expect(await screen.findAllByText(SEM_RESPOSTAS_AINDA)).toHaveLength(2);
    expect(screen.queryByRole("img", { name: /acertou/ })).not.toBeInTheDocument();
  });
});

describe("SoGerente", () => {
  it("leva o auditor para a fila", async () => {
    act(() => guardarSessao(m.sessaoDe("aud-01")));
    render(
      <SoGerente>
        <p>painel</p>
      </SoGerente>,
    );
    await waitFor(() => expect(navegar.replace).toHaveBeenCalledWith("/filial/fila"));
    expect(screen.queryByText("painel")).not.toBeInTheDocument();
  });
});

describe("formatarTempoCurto", () => {
  it("usa segundos, minutos ou horas", () => {
    expect(formatarTempoCurto(45)).toBe("45 s");
    expect(formatarTempoCurto(240)).toBe("4 min");
    expect(formatarTempoCurto(5400)).toBe("1,5 h");
    expect(formatarTempoCurto(null)).toBe("—");
  });
});
