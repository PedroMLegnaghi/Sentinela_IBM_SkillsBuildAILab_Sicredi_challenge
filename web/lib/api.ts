/**
 * Cliente da API do Sentinela (ESPECIFICACAO, seção 12).
 * Uma função por rota. Com NEXT_PUBLIC_USAR_MOCK=1, usa dados inventados de web/lib/mocks/.
 * Erros da API são relançados em português com mensagem sobre o que fazer.
 */

import type {
  RespostaFila,
  RespostaTransacao,
  RespostaAnalisar,
  RespostaAuditoriaIniciada,
  Auditoria,
  EntradaAnalisar,
  EntradaResposta,
  Resposta,
  RespostaRespostas,
  RespostaMetricas,
  RespostaSaude,
} from "@/lib/tipos";

const URL_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const USAR_MOCK =
  process.env.NEXT_PUBLIC_USAR_MOCK === "1";

/** Erro amigável quando a API não responde. */
class ErroAPI extends Error {
  constructor(mensagem: string) {
    super(mensagem);
    this.name = "ErroAPI";
  }
}

async function buscar<T>(
  caminho: string,
  opcoes?: RequestInit,
): Promise<T> {
  let resp: Response;
  try {
    resp = await fetch(`${URL_BASE}${caminho}`, opcoes);
  } catch {
    throw new ErroAPI(
      "Não foi possível conectar à API. Verifique se ela está em execução " +
        "(uvicorn src.api.app:app --port 8000) e tente de novo.",
    );
  }
  if (!resp.ok) {
    let detalhe = "";
    try {
      const corpo = (await resp.json()) as { detail?: string };
      detalhe = corpo.detail ?? "";
    } catch {
      detalhe = resp.statusText;
    }
    throw new ErroAPI(
      `A API retornou um erro (${resp.status}): ${detalhe}`,
    );
  }
  return resp.json() as Promise<T>;
}

// Import dinâmico dos mocks (carregado apenas quando USAR_MOCK=1)
async function obterMocks() {
  const { mocks } = await import("@/lib/mocks/index");
  return mocks;
}

/**
 * GET /api/saude
 */
export async function obterSaude(): Promise<RespostaSaude> {
  if (USAR_MOCK) {
    const m = await obterMocks();
    return m.saude;
  }
  return buscar<RespostaSaude>("/api/saude");
}

/**
 * GET /api/fila
 */
export async function obterFila(
  decisoes?: string,
): Promise<RespostaFila> {
  if (USAR_MOCK) {
    const m = await obterMocks();
    return m.fila;
  }
  const params = decisoes ? `?decisoes=${encodeURIComponent(decisoes)}` : "";
  return buscar<RespostaFila>(`/api/fila${params}`);
}

/**
 * GET /api/transacoes/{id_transacao}
 */
export async function obterTransacao(
  idTransacao: number,
): Promise<RespostaTransacao> {
  if (USAR_MOCK) {
    const m = await obterMocks();
    return m.transacao;
  }
  return buscar<RespostaTransacao>(`/api/transacoes/${idTransacao}`);
}

/**
 * POST /api/analisar
 */
export async function analisar(
  entrada: EntradaAnalisar,
): Promise<RespostaAnalisar> {
  if (USAR_MOCK) {
    const m = await obterMocks();
    return m.analisar;
  }
  return buscar<RespostaAnalisar>("/api/analisar", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(entrada),
  });
}

/**
 * POST /api/transacoes/{id_transacao}/auditoria
 */
export async function iniciarAuditoria(
  idTransacao: number,
): Promise<RespostaAuditoriaIniciada> {
  if (USAR_MOCK) {
    const m = await obterMocks();
    return m.auditoriaIniciada;
  }
  return buscar<RespostaAuditoriaIniciada>(
    `/api/transacoes/${idTransacao}/auditoria`,
    { method: "POST" },
  );
}

/**
 * GET /api/auditorias/{id_auditoria}
 */
export async function obterAuditoria(
  idAuditoria: string,
): Promise<Auditoria> {
  if (USAR_MOCK) {
    const m = await obterMocks();
    // Simula transição pendente → concluida na segunda chamada
    return m.auditoriaConcluida;
  }
  return buscar<Auditoria>(`/api/auditorias/${idAuditoria}`);
}

/**
 * POST /api/respostas
 */
export async function registrarResposta(
  entrada: EntradaResposta,
): Promise<Resposta> {
  if (USAR_MOCK) {
    await obterMocks();
    return {
      id_transacao: entrada.id_transacao,
      resposta: entrada.resposta,
      registrado_em: new Date().toISOString(),
    };
  }
  return buscar<Resposta>("/api/respostas", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(entrada),
  });
}

/**
 * GET /api/respostas
 */
export async function obterRespostas(): Promise<RespostaRespostas> {
  if (USAR_MOCK) {
    const m = await obterMocks();
    return m.respostas;
  }
  return buscar<RespostaRespostas>("/api/respostas");
}

/**
 * GET /api/metricas
 */
export async function obterMetricas(): Promise<RespostaMetricas> {
  if (USAR_MOCK) {
    const m = await obterMocks();
    return m.metricas;
  }
  return buscar<RespostaMetricas>("/api/metricas");
}
