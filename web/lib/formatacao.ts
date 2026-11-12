/**
 * Funções de formatação em pt-BR para o site Sentinela (ESPECIFICACAO, seção 14).
 * Todas as funções são puras e testáveis de forma independente.
 */

const LOCALE = "pt-BR";

/**
 * Formata valor monetário em reais.
 * @param valor - Número a formatar, ou null/undefined para vazio.
 * @returns "R$ 1.234,50" ou "—" quando vazio.
 */
export function formatarMoeda(valor: number | null | undefined): string {
  if (valor === null || valor === undefined) return "—";
  return valor.toLocaleString(LOCALE, {
    style: "currency",
    currency: "BRL",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

/**
 * Formata nota de risco com 1 casa decimal.
 * @param nota - Número entre 0 e 100.
 * @returns "97,3" ou "100,0".
 */
export function formatarNota(nota: number): string {
  return nota.toLocaleString(LOCALE, {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  });
}

/**
 * Formata inteiro com separador de milhar.
 * @param n - Número inteiro.
 * @returns "2.054".
 */
export function formatarInteiro(n: number): string {
  return n.toLocaleString(LOCALE, {
    maximumFractionDigits: 0,
  });
}

/**
 * Formata decimal com número fixo de casas.
 * @param valor - Número.
 * @param casas - Quantidade de casas decimais.
 * @returns "0,998".
 */
export function formatarDecimal(valor: number, casas: number): string {
  return valor.toLocaleString(LOCALE, {
    minimumFractionDigits: casas,
    maximumFractionDigits: casas,
  });
}

/**
 * Formata fração como percentual com 1 casa decimal.
 * @param fracao - Número entre 0 e 1.
 * @returns "48,1%" ou "1,2%".
 */
export function formatarPercentual(fracao: number): string {
  return (fracao * 100).toLocaleString(LOCALE, {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  }) + "%";
}

/**
 * Formata string de data/hora ISO para exibição pt-BR.
 * @param dataHora - String ISO 8601 sem fuso, ou null.
 * @returns "03/03/2025 00:17" ou "—" quando vazio.
 */
export function formatarDataHora(dataHora: string | null | undefined): string {
  if (!dataHora) return "—";
  // Strings sem fuso são tratadas como horário local
  const d = new Date(dataHora);
  if (isNaN(d.getTime())) return "—";
  const dia = String(d.getDate()).padStart(2, "0");
  const mes = String(d.getMonth() + 1).padStart(2, "0");
  const ano = d.getFullYear();
  const hora = String(d.getHours()).padStart(2, "0");
  const min = String(d.getMinutes()).padStart(2, "0");
  return `${dia}/${mes}/${ano} ${hora}:${min}`;
}

const ROTULOS_TIPO: Record<string, string> = {
  credito: "Crédito",
  debito: "Débito",
};

/**
 * Retorna rótulo legível do tipo de transação.
 * @param tipo - Valor bruto ("credito", "debito").
 * @returns Rótulo em português, ou o valor original se desconhecido.
 */
export function formatarTipo(tipo: string): string {
  return ROTULOS_TIPO[tipo] ?? tipo;
}

const ROTULOS_MODALIDADE: Record<string, string> = {
  cartao_presente: "Presente",
  cartao_nao_presente: "Não presente",
};

/**
 * Retorna rótulo legível da modalidade de transação.
 * @param modalidade - Valor bruto ("cartao_presente", "cartao_nao_presente").
 * @returns Rótulo em português, ou o valor original se desconhecido.
 */
export function formatarModalidade(modalidade: string): string {
  return ROTULOS_MODALIDADE[modalidade] ?? modalidade;
}

const ROTULOS_RESPOSTA: Record<string, string> = {
  fraude: "Fraude confirmada",
  legitima: "Transação legítima",
};

/**
 * Retorna rótulo legível da resposta do analista.
 * @param resposta - "fraude" ou "legitima".
 * @returns Rótulo em português.
 */
export function formatarResposta(resposta: string): string {
  return ROTULOS_RESPOSTA[resposta] ?? resposta;
}
