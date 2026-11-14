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
  Notificacao,
  RespostaNotificacoes,
  EntradaRespostaNotificacao,
  RespostaPerfis,
  Sessao,
  RespostaInicio,
  RespostaExtrato,
  SituacaoCompra,
  DetalheCompra,
  EntradaCompra,
  RespostaCompra,
  RespostaContestacao,
  RespostaFilaFilial,
  RespostaCompraFilial,
  RespostaMetricasFilial,
} from "@/lib/tipos";
import { obterSessao } from "@/lib/sessao";

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

/**
 * POST /api/transacoes/{id_transacao}/notificacao
 */
export async function notificarAssociado(
  idTransacao: number,
): Promise<Notificacao> {
  if (USAR_MOCK) {
    const m = await obterMocks();
    return m.notificacaoAguardando;
  }
  return buscar<Notificacao>(`/api/transacoes/${idTransacao}/notificacao`, {
    method: "POST",
  });
}

/**
 * GET /api/notificacoes
 */
export async function obterNotificacoes(): Promise<RespostaNotificacoes> {
  if (USAR_MOCK) {
    const m = await obterMocks();
    return m.notificacoes;
  }
  return buscar<RespostaNotificacoes>("/api/notificacoes");
}

/**
 * GET /api/notificacoes/{id_notificacao}
 */
export async function obterNotificacao(
  idNotificacao: string,
): Promise<Notificacao> {
  if (USAR_MOCK) {
    const m = await obterMocks();
    return m.notificacaoAguardando;
  }
  return buscar<Notificacao>(`/api/notificacoes/${idNotificacao}`);
}

/**
 * POST /api/notificacoes/{id_notificacao}/resposta
 */
export async function responderNotificacao(
  idNotificacao: string,
  entrada: EntradaRespostaNotificacao,
): Promise<Notificacao> {
  if (USAR_MOCK) {
    const m = await obterMocks();
    const resultado =
      entrada.resposta === "nao"
        ? "Compra bloqueada e cartão protegido. O caso foi para o analista."
        : "Compra liberada pelo associado.";
    return {
      ...m.notificacaoAguardando,
      status: entrada.resposta === "nao" ? "negada" : "confirmada",
      respondida_em: new Date().toISOString(),
      resultado,
    };
  }
  return buscar<Notificacao>(
    `/api/notificacoes/${idNotificacao}/resposta`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(entrada),
    },
  );
}

// --- Seção 17: área do associado e da filial (Issues #91 a #99) ---

/** Cabeçalho da sessão simulada (ESPECIFICACAO, seção 17.1). */
function comSessao(opcoes: RequestInit = {}): RequestInit {
  const token = obterSessao()?.token ?? "";
  return {
    ...opcoes,
    headers: { ...(opcoes.headers ?? {}), "X-Sessao": token },
  };
}

async function obterMocksRefatoracao() {
  const { mocksRefatoracao } = await import("@/lib/mocks/refatoracao");
  return mocksRefatoracao;
}

const comoJson = (corpo: unknown): RequestInit => ({
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(corpo),
});

/** GET /api/sessao/perfis */
export async function obterPerfis(): Promise<RespostaPerfis> {
  if (USAR_MOCK) return (await obterMocksRefatoracao()).perfis;
  return buscar<RespostaPerfis>("/api/sessao/perfis");
}

/** POST /api/sessao */
export async function entrar(idPerfil: string): Promise<Sessao> {
  if (USAR_MOCK) return (await obterMocksRefatoracao()).sessaoDe(idPerfil);
  return buscar<Sessao>("/api/sessao", comoJson({ id_perfil: idPerfil }));
}

/** GET /api/associado/inicio */
export async function obterInicio(): Promise<RespostaInicio> {
  if (USAR_MOCK) return (await obterMocksRefatoracao()).inicio;
  return buscar<RespostaInicio>("/api/associado/inicio", comSessao());
}

/** GET /api/associado/extrato */
export async function obterExtrato(situacoes?: SituacaoCompra[]): Promise<RespostaExtrato> {
  if (USAR_MOCK) {
    const extrato = (await obterMocksRefatoracao()).extrato;
    if (!situacoes?.length) return extrato;
    const itens = extrato.itens.filter((c) => situacoes.includes(c.situacao));
    return { total: itens.length, itens };
  }
  const filtro = situacoes?.length ? `?situacao=${situacoes.join(",")}` : "";
  return buscar<RespostaExtrato>(`/api/associado/extrato${filtro}`, comSessao());
}

/** GET /api/associado/compras/{id_compra} */
export async function obterCompra(idCompra: string): Promise<DetalheCompra> {
  if (USAR_MOCK) {
    const m = await obterMocksRefatoracao();
    if (idCompra === m.compraBloqueada.id_compra) return m.compraBloqueada;
    const item = m.extrato.itens.find((c) => c.id_compra === idCompra);
    return {
      ...(item ?? m.compraAprovada),
      bloqueio: null,
      resposta_associado: null,
      pode_contestar: (item?.situacao ?? "APROVADA") === "APROVADA",
    };
  }
  return buscar<DetalheCompra>(`/api/associado/compras/${idCompra}`, comSessao());
}

/** POST /api/associado/compras */
export async function simularCompra(entrada: EntradaCompra): Promise<RespostaCompra> {
  if (USAR_MOCK) return (await obterMocksRefatoracao()).compraSimulada;
  return buscar<RespostaCompra>("/api/associado/compras", comSessao(comoJson(entrada)));
}

/** POST /api/associado/compras/{id_compra}/contestacao */
export async function contestarCompra(idCompra: string): Promise<RespostaContestacao> {
  if (USAR_MOCK) return (await obterMocksRefatoracao()).contestacao;
  return buscar<RespostaContestacao>(
    `/api/associado/compras/${idCompra}/contestacao`,
    comSessao({ method: "POST" }),
  );
}

/** GET /api/filial/fila */
export async function obterFilaFilial(
  situacoes?: SituacaoCompra[],
): Promise<RespostaFilaFilial> {
  if (USAR_MOCK) {
    const fila = (await obterMocksRefatoracao()).filaFilial;
    if (!situacoes?.length) return fila;
    const itens = fila.itens.filter((i) => situacoes.includes(i.situacao));
    return { ...fila, total: itens.length, itens };
  }
  const filtro = situacoes?.length ? `?situacao=${situacoes.join(",")}` : "";
  return buscar<RespostaFilaFilial>(`/api/filial/fila${filtro}`, comSessao());
}

/** GET /api/filial/compras/{id_compra} */
export async function obterCompraFilial(idCompra: string): Promise<RespostaCompraFilial> {
  if (USAR_MOCK) {
    const m = await obterMocksRefatoracao();
    const item = m.filaFilial.itens.find((i) => i.id_compra === idCompra);
    return { ...m.compraFilial, compra: item ?? m.compraFilial.compra };
  }
  return buscar<RespostaCompraFilial>(`/api/filial/compras/${idCompra}`, comSessao());
}

/** GET /api/filial/metricas */
export async function obterMetricasFilial(): Promise<RespostaMetricasFilial> {
  if (USAR_MOCK) return (await obterMocksRefatoracao()).metricasFilial;
  return buscar<RespostaMetricasFilial>("/api/filial/metricas", comSessao());
}
