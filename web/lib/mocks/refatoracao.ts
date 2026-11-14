/**
 * Dados inventados para as rotas da área do associado e da filial (ESPECIFICACAO, seção 17).
 * Usados quando NEXT_PUBLIC_USAR_MOCK=1. Os dados seguem o protótipo (docs/prototipo/index.html)
 * e nunca contêm linhas de data/.
 */

import type {
  CompraExtrato,
  DetalheCompra,
  Perfil,
  RespostaCompra,
  RespostaCompraFilial,
  RespostaContestacao,
  RespostaExtrato,
  RespostaFilaFilial,
  RespostaInicio,
  RespostaMetricasFilial,
  RespostaPerfis,
  Sessao,
} from "@/lib/tipos";
import { mocks } from "@/lib/mocks/index";

const CENTRO = { id_filial: "fil-centro", nome: "Agência Centro" };
const NORTE = { id_filial: "fil-norte", nome: "Agência Norte" };

const perfis: RespostaPerfis = {
  perfis: [
    { id_perfil: "asc-01", nome: "Ana Souza", papel: "associado", filial: CENTRO },
    { id_perfil: "asc-02", nome: "Carlos Lima", papel: "associado", filial: NORTE },
    { id_perfil: "aud-01", nome: "Rafael Moura", papel: "auditor", filial: CENTRO },
    { id_perfil: "aud-03", nome: "Tiago Nunes", papel: "auditor", filial: NORTE },
    { id_perfil: "ger-01", nome: "Helena Castro", papel: "gerente", filial: CENTRO },
    { id_perfil: "ger-02", nome: "Marcos Viana", papel: "gerente", filial: NORTE },
  ],
};

function sessaoDe(idPerfil: string): Sessao {
  const perfil = perfis.perfis.find((p) => p.id_perfil === idPerfil) as Perfil;
  return { token: `token-mock-${idPerfil}`, perfil };
}

const compraBase = {
  id_notificacao: null,
  simulada: false,
} as const;

const extratoItens: CompraExtrato[] = [
  {
    ...compraBase,
    id_compra: "cmp-000006",
    estabelecimento: "Mercado Bom Preço",
    data_hora: "2025-03-14T18:42:00",
    valor: 86.4,
    tipo_transacao: "debito",
    modalidade_transacao: "cartao_presente",
    final_cartao: "1111",
    situacao: "APROVADA",
  },
  {
    ...compraBase,
    id_compra: "cmp-000005",
    estabelecimento: "Eletrônicos Web",
    data_hora: "2025-03-13T02:47:00",
    valor: 2340.0,
    tipo_transacao: "credito",
    modalidade_transacao: "cartao_nao_presente",
    final_cartao: "4821",
    situacao: "BLOQUEADA",
    id_notificacao: "not-mock-002",
  },
  {
    ...compraBase,
    id_compra: "cmp-000004",
    estabelecimento: "Loja online",
    data_hora: "2025-03-12T03:10:00",
    valor: 980.0,
    tipo_transacao: "credito",
    modalidade_transacao: "cartao_nao_presente",
    final_cartao: "4821",
    situacao: "AGUARDANDO",
    id_notificacao: "not-mock-001",
  },
  {
    ...compraBase,
    id_compra: "cmp-000003",
    estabelecimento: "Posto Avenida",
    data_hora: "2025-03-11T08:15:00",
    valor: 150.0,
    tipo_transacao: "debito",
    modalidade_transacao: "cartao_presente",
    final_cartao: "1111",
    situacao: "APROVADA",
  },
  {
    ...compraBase,
    id_compra: "cmp-000002",
    estabelecimento: "Farmácia Vida",
    data_hora: "2025-03-10T19:02:00",
    valor: 42.9,
    tipo_transacao: "debito",
    modalidade_transacao: "cartao_presente",
    final_cartao: "1111",
    situacao: "APROVADA",
  },
  {
    ...compraBase,
    id_compra: "cmp-000001",
    estabelecimento: "Restaurante Sabor",
    data_hora: "2025-03-09T12:30:00",
    valor: 68.0,
    tipo_transacao: "credito",
    modalidade_transacao: "cartao_presente",
    final_cartao: "4821",
    situacao: "APROVADA",
  },
];

const extrato: RespostaExtrato = { total: extratoItens.length, itens: extratoItens };

const inicio: RespostaInicio = {
  associado: { nome: "Ana Souza", filial: "Agência Centro" },
  saldo: 4820.35,
  limite_total: 3000.0,
  limite_disponivel: 2150.0,
  cartoes: [
    { id: "car-01-d", tipo: "debito", final: "1111", bloqueado: false },
    { id: "car-01-c", tipo: "credito", final: "4821", bloqueado: false },
  ],
  pendentes: [
    {
      id_notificacao: "not-mock-001",
      id_compra: "cmp-000004",
      valor: 980.0,
      data_hora: "2025-03-12T03:10:00",
    },
  ],
  ultimas_compras: extratoItens.slice(0, 3),
};

const compraBloqueada: DetalheCompra = {
  ...extratoItens[1],
  bloqueio: {
    por: "Sentinela",
    em: "2025-03-13T02:47:00",
    motivo: "A compra fugiu do seu padrão de uso e foi bloqueada por segurança.",
  },
  resposta_associado: { resposta: "nao", em: "2025-03-13T07:20:00" },
  pode_contestar: false,
};

const compraAprovada: DetalheCompra = {
  ...extratoItens[0],
  bloqueio: null,
  resposta_associado: null,
  pode_contestar: true,
};

const compraSimulada: RespostaCompra = {
  compra: {
    id_compra: "cmp-900001",
    estabelecimento: "Loja online",
    data_hora: "2025-03-31T03:10:00",
    valor: 980.0,
    tipo_transacao: "credito",
    modalidade_transacao: "cartao_nao_presente",
    final_cartao: "4821",
    situacao: "AGUARDANDO",
    id_notificacao: "not-mock-003",
    simulada: true,
  },
  id_notificacao: "not-mock-003",
};

const contestacao: RespostaContestacao = {
  compra: { ...extratoItens[0], situacao: "CONTESTADA" },
  cartao: { id: "car-01-d", tipo: "debito", final: "1111", bloqueado: true },
};

const filaFilial: RespostaFilaFilial = {
  filial: CENTRO,
  total: 6,
  itens: [
    {
      id_compra: "cmp-000005",
      nota: 100.0,
      decisao: "BLOQUEAR",
      associado: "Ana S.",
      final_cartao: "4821",
      data_hora: "2025-03-13T02:47:00",
      valor: 2340.0,
      tipo_transacao: "credito",
      modalidade_transacao: "cartao_nao_presente",
      situacao: "BLOQUEADA",
      veredito_ia: "CONFIRMA",
    },
    {
      id_compra: "cmp-000004",
      nota: 58.0,
      decisao: "PEDIR_CONFIRMACAO",
      associado: "Ana S.",
      final_cartao: "4821",
      data_hora: "2025-03-12T03:10:00",
      valor: 980.0,
      tipo_transacao: "credito",
      modalidade_transacao: "cartao_nao_presente",
      situacao: "AGUARDANDO",
      veredito_ia: "CONFIRMA",
    },
    {
      id_compra: "cmp-000101",
      nota: 97.0,
      decisao: "BLOQUEAR",
      associado: "Bruno T.",
      final_cartao: "0934",
      data_hora: "2025-03-12T01:22:00",
      valor: 1199.9,
      tipo_transacao: "credito",
      modalidade_transacao: "cartao_nao_presente",
      situacao: "BLOQUEADA",
      veredito_ia: "CONFIRMA",
    },
    {
      id_compra: "cmp-000102",
      nota: 52.0,
      decisao: "PEDIR_CONFIRMACAO",
      associado: "Carla M.",
      final_cartao: "7710",
      data_hora: "2025-03-11T23:58:00",
      valor: 415.0,
      tipo_transacao: "credito",
      modalidade_transacao: "cartao_presente",
      situacao: "APROVADA",
      veredito_ia: "INCONCLUSIVO",
    },
    {
      id_compra: "cmp-000103",
      nota: 12.0,
      decisao: "APROVAR",
      associado: "Diego P.",
      final_cartao: "2288",
      data_hora: "2025-03-11T14:05:00",
      valor: 76.3,
      tipo_transacao: "debito",
      modalidade_transacao: "cartao_presente",
      situacao: "CONTESTADA",
      veredito_ia: "DIVERGE",
    },
    {
      id_compra: "cmp-000104",
      nota: 61.0,
      decisao: "PEDIR_CONFIRMACAO",
      associado: "Elisa R.",
      final_cartao: "5163",
      data_hora: "2025-03-10T04:31:00",
      valor: 640.0,
      tipo_transacao: "credito",
      modalidade_transacao: "cartao_nao_presente",
      situacao: "AGUARDANDO",
      veredito_ia: "CONFIRMA",
    },
  ],
};

const compraFilial: RespostaCompraFilial = {
  compra: filaFilial.itens[0],
  analise: { ...mocks.transacao.analise, nota: 100.0 },
  auditoria: mocks.auditoriaConcluida,
  associado: {
    nome_abreviado: "Ana S.",
    final_cartao: "4821",
    historico: { compras_90d: 38, valor_mediano: 72.0, contestacoes: 0 },
  },
  resposta_associado: { resposta: "nao", em: "2025-03-13T07:20:00" },
  bloqueio: {
    por: "Sentinela",
    em: "2025-03-13T02:47:00",
    motivo: mocks.transacao.analise.explicacao,
  },
};

const metricasFilial: RespostaMetricasFilial = {
  filial: CENTRO,
  periodo: "2025-03",
  totais: {
    compras: 6804,
    aprovadas: 6698,
    confirmacoes: 79,
    bloqueadas: 27,
    valor_protegido: 3248.1,
  },
  por_tipo: [
    {
      tipo_transacao: "credito",
      modalidade_transacao: "cartao_nao_presente",
      aprovadas: 1170,
      confirmacoes: 22,
      bloqueadas: 22,
    },
    {
      tipo_transacao: "credito",
      modalidade_transacao: "cartao_presente",
      aprovadas: 1483,
      confirmacoes: 12,
      bloqueadas: 3,
    },
    {
      tipo_transacao: "debito",
      modalidade_transacao: "cartao_nao_presente",
      aprovadas: 880,
      confirmacoes: 20,
      bloqueadas: 2,
    },
    {
      tipo_transacao: "debito",
      modalidade_transacao: "cartao_presente",
      aprovadas: 3165,
      confirmacoes: 25,
      bloqueadas: 0,
    },
  ],
  acerto_modelo: {
    alertas_certos: 61,
    alertas_desnecessarios: 9,
    sem_resposta: 36,
    taxa: 87.1,
  },
  fraudes_aprovadas: {
    total: 2,
    itens: [
      {
        associado: "Diego P.",
        final_cartao: "2288",
        data_hora: "2025-03-11T14:05:00",
        valor: 76.3,
      },
      {
        associado: "Marta V.",
        final_cartao: "6402",
        data_hora: "2025-03-08T21:40:00",
        valor: 129.0,
      },
    ],
  },
  tempo_resposta_mediano_s: 240.0,
};

export const mocksRefatoracao = {
  perfis,
  sessaoDe,
  inicio,
  extrato,
  compraBloqueada,
  compraAprovada,
  compraSimulada,
  contestacao,
  filaFilial,
  compraFilial,
  metricasFilial,
};
