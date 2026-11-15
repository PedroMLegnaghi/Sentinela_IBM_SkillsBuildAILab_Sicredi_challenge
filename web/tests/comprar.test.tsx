/**
 * Testes de simular compra, do aviso "Foi você?" e da contestação (Issue #95).
 */

import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import PaginaComprar from "@/components/associado/PaginaComprar";
import ConfirmarCompra from "@/components/associado/ConfirmarCompra";
import BotaoContestar from "@/components/associado/BotaoContestar";
import * as api from "@/lib/api";
import { mocks } from "@/lib/mocks/index";
import { mocksRefatoracao as m } from "@/lib/mocks/refatoracao";
import { CENARIOS, montarEntradaCompra } from "@/lib/compra";
import {
  BOTAO_COMPRAR,
  CAMPOS_COMPRA,
  CONTESTAR,
  CONTESTAR_CONFIRMAR,
  ERRO_CARTAO_BLOQUEADO,
  RESPOSTA_NAO,
  RESULTADO_COMPRA,
  RODAPE_SEGURANCA,
} from "@/lib/textos";

const navegar = { push: vi.fn(), replace: vi.fn() };
vi.mock("next/navigation", () => ({ useRouter: () => navegar }));

vi.mock("@/lib/api", () => ({
  obterInicio: vi.fn(),
  simularCompra: vi.fn(),
  obterNotificacao: vi.fn(),
  obterCompra: vi.fn(),
  responderNotificacao: vi.fn(),
  contestarCompra: vi.fn(),
}));

const apiFalsa = vi.mocked(api);

beforeEach(() => {
  vi.clearAllMocks();
  apiFalsa.obterInicio.mockResolvedValue(m.inicio);
});

describe("lógica da compra simulada", () => {
  it("monta a entrada com cartão, data do dia simulado, madrugada e risco do estabelecimento", () => {
    const entrada = montarEntradaCompra(CENARIOS[1].valores, "car-01-c");
    expect(entrada).toMatchObject({
      cartao: "car-01-c",
      estabelecimento: "Loja online",
      data_hora: "2025-03-31T03:00:00",
      hora: 3,
      madrugada: 1,
      nao_presente: 1,
      ip_pais_desconhecido: 0,
      risco_estabelecimento: 45,
      modalidade_transacao: "cartao_nao_presente",
    });
    expect(entrada).not.toHaveProperty("credito");
    expect(entrada).not.toHaveProperty("tipo_transacao");
  });

  it("a compra comum não é de madrugada nem pela internet", () => {
    const entrada = montarEntradaCompra(CENARIOS[0].valores, "car-01-d");
    expect(entrada.madrugada).toBe(0);
    expect(entrada.modalidade_transacao).toBe("cartao_presente");
  });
});

describe("PaginaComprar", () => {
  it("cada cenário preenche o formulário", async () => {
    render(<PaginaComprar />);
    const valor = await screen.findByLabelText(CAMPOS_COMPRA.valor);
    expect(valor).toHaveValue(86.4);

    await userEvent.click(screen.getByRole("button", { name: "Várias seguidas" }));

    expect(valor).toHaveValue(450);
    expect(screen.getByLabelText(CAMPOS_COMPRA.hora)).toHaveValue(2);
    expect(screen.getByLabelText(CAMPOS_COMPRA.pais)).toHaveValue("desconhecido");
    expect(screen.getByRole("button", { name: "Várias seguidas" })).toHaveAttribute("aria-pressed", "true");
  });

  it("envia a compra com o cartão do tipo escolhido e mostra a faixa de espera", async () => {
    apiFalsa.simularCompra.mockResolvedValue(m.compraSimulada);
    render(<PaginaComprar />);
    await userEvent.click(await screen.findByRole("button", { name: "Madrugada online" }));
    await userEvent.click(screen.getByRole("button", { name: BOTAO_COMPRAR }));

    expect(apiFalsa.simularCompra).toHaveBeenCalledWith(
      expect.objectContaining({ cartao: "car-01-c", valor: 980 }),
    );
    expect(await screen.findByText(RESULTADO_COMPRA.AGUARDANDO.titulo)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Responder ao aviso" })).toHaveAttribute(
      "href",
      "/associado/avisos/not-mock-003?compra=cmp-900001",
    );
  });

  it("cartão bloqueado mostra a mensagem em português", async () => {
    apiFalsa.simularCompra.mockRejectedValue(new Error("A API retornou um erro (409): cartão bloqueado"));
    render(<PaginaComprar />);
    await userEvent.click(await screen.findByRole("button", { name: BOTAO_COMPRAR }));
    expect(await screen.findByText(ERRO_CARTAO_BLOQUEADO)).toBeInTheDocument();
  });
});

describe("ConfirmarCompra", () => {
  it("'Não fui eu' responde e volta ao detalhe da compra", async () => {
    apiFalsa.obterNotificacao.mockResolvedValue(mocks.notificacaoAguardando);
    apiFalsa.obterCompra.mockResolvedValue({
      ...m.extrato.itens[2],
      bloqueio: null,
      resposta_associado: null,
      pode_contestar: false,
    });
    apiFalsa.responderNotificacao.mockResolvedValue(mocks.notificacaoNegada);

    render(<ConfirmarCompra idNotificacao="not-mock-001" idCompra="cmp-000004" />);

    expect(await screen.findByText(mocks.notificacaoAguardando.mensagem)).toBeInTheDocument();
    expect(screen.getByText(RODAPE_SEGURANCA)).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: RESPOSTA_NAO }));

    expect(apiFalsa.responderNotificacao).toHaveBeenCalledWith("not-mock-001", { resposta: "nao" });
    await waitFor(() => expect(navegar.push).toHaveBeenCalledWith("/associado/compras/cmp-000004"));
  });

  it("aviso já respondido não mostra os botões", async () => {
    apiFalsa.obterNotificacao.mockResolvedValue(mocks.notificacaoNegada);
    render(<ConfirmarCompra idNotificacao="not-mock-002" />);
    expect(await screen.findByText(/Você já respondeu/)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: RESPOSTA_NAO })).not.toBeInTheDocument();
  });
});

describe("BotaoContestar", () => {
  it("pede confirmação antes de contestar", async () => {
    apiFalsa.contestarCompra.mockResolvedValue(m.contestacao);
    const aoContestar = vi.fn();
    render(<BotaoContestar idCompra="cmp-000006" aoContestar={aoContestar} />);

    await userEvent.click(screen.getByRole("button", { name: CONTESTAR }));
    expect(apiFalsa.contestarCompra).not.toHaveBeenCalled();

    await userEvent.click(screen.getByRole("button", { name: CONTESTAR_CONFIRMAR }));
    expect(apiFalsa.contestarCompra).toHaveBeenCalledWith("cmp-000006");
    await waitFor(() => expect(aoContestar).toHaveBeenCalled());
  });
});
