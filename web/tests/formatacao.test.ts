/**
 * Testes das funções de formatação pt-BR (ESPECIFICACAO, seção 14).
 */

import { describe, it, expect } from "vitest";
import {
  formatarMoeda,
  formatarNota,
  formatarInteiro,
  formatarDecimal,
  formatarPercentual,
  formatarDataHora,
  formatarTipo,
  formatarModalidade,
  formatarResposta,
} from "@/lib/formatacao";

describe("formatarMoeda", () => {
  it("formata valor com separador de milhar e casas decimais", () => {
    expect(formatarMoeda(1234.5)).toBe("R$\u00a01.234,50");
  });

  it("retorna traço para null", () => {
    expect(formatarMoeda(null)).toBe("—");
  });

  it("retorna traço para undefined", () => {
    expect(formatarMoeda(undefined)).toBe("—");
  });
});

describe("formatarNota", () => {
  it("formata nota com 1 casa decimal", () => {
    expect(formatarNota(97.34)).toBe("97,3");
  });

  it("formata nota inteira com 1 casa decimal", () => {
    expect(formatarNota(100)).toBe("100,0");
  });
});

describe("formatarInteiro", () => {
  it("formata inteiro com separador de milhar", () => {
    expect(formatarInteiro(2054)).toBe("2.054");
  });
});

describe("formatarDecimal", () => {
  it("formata decimal com 3 casas", () => {
    expect(formatarDecimal(0.99812, 3)).toBe("0,998");
  });
});

describe("formatarPercentual", () => {
  it("formata 26/54 (fraudes bloqueadas no projeto) como 48,1%", () => {
    // 26/54 = 0.48148... → 48.148...% → "48,1%"
    expect(formatarPercentual(26 / 54)).toBe("48,1%");
  });

  it("formata 100% sem ambiguidade de arredondamento", () => {
    expect(formatarPercentual(1)).toBe("100,0%");
  });
});

describe("formatarDataHora", () => {
  it("formata data e hora no padrão pt-BR sem fuso", () => {
    // Usa UTC fixo para evitar variação por fuso do ambiente de CI
    // A função interpreta a string como local, então testamos o formato
    const resultado = formatarDataHora("2025-03-03T00:17:00");
    expect(resultado).toMatch(/\d{2}\/\d{2}\/2025 \d{2}:\d{2}/);
  });

  it("retorna traço para null", () => {
    expect(formatarDataHora(null)).toBe("—");
  });

  it("retorna traço para undefined", () => {
    expect(formatarDataHora(undefined)).toBe("—");
  });

  it("retorna traço para string inválida", () => {
    expect(formatarDataHora("nao-e-data")).toBe("—");
  });
});

describe("formatarTipo", () => {
  it("retorna rótulo legível para credito", () => {
    expect(formatarTipo("credito")).toBe("Crédito");
  });

  it("retorna o valor original para tipo desconhecido", () => {
    expect(formatarTipo("xyz")).toBe("xyz");
  });
});

describe("formatarModalidade", () => {
  it("retorna rótulo legível para cartao_nao_presente", () => {
    expect(formatarModalidade("cartao_nao_presente")).toBe("Não presente");
  });

  it("retorna rótulo legível para cartao_presente", () => {
    expect(formatarModalidade("cartao_presente")).toBe("Presente");
  });
});

describe("formatarResposta", () => {
  it("retorna rótulo para legitima", () => {
    expect(formatarResposta("legitima")).toBe("Transação legítima");
  });

  it("retorna rótulo para fraude", () => {
    expect(formatarResposta("fraude")).toBe("Fraude confirmada");
  });
});
