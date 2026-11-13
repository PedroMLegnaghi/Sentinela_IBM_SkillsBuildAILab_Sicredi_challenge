/**
 * Textos de tela do site Sentinela.
 * Todos os textos visíveis ao usuário ficam aqui; nenhum texto literal nos componentes.
 * Cada Issue acrescenta textos dentro do próprio bloco; merges não conflitam.
 */

// --- Aplicação ---
export const TITULO_APP = "Sentinela";
export const SUBTITULO_APP = "Agente antifraude · Desafio Sicredi";
export const RODAPE_DADOS =
  "Sentinela · agente antifraude do Desafio Sicredi. Dados 100% sintéticos fornecidos pela Sicredi. Protótipo do IBM SkillsBuild AI Lab.";

// --- Navegação ---
export const NAV_FILA = "Fila de alertas";
export const NAV_DESEMPENHO = "Desempenho";
export const NAV_COMO_FUNCIONA = "Como funciona";
export const NAV_SIMULADOR = "Simulador";
export const NAV_RESPOSTAS = "Respostas";

// --- Estados comuns ---
export const CARREGANDO = "Carregando…";
export const VAZIO_PADRAO = "Nenhum item encontrado.";
export const ERRO_API =
  "Não foi possível carregar os dados. Verifique se a API está em execução (python -m uvicorn src.api.app:app --port 8000) e tente de novo.";
export const TENTAR_NOVAMENTE = "Tentar de novo";

// --- Decisões ---
export const ROTULOS_DECISAO: Record<string, string> = {
  BLOQUEAR: "Bloquear e enviar ao analista",
  PEDIR_CONFIRMACAO: "Pedir confirmação ao cliente",
  APROVAR: "Aprovar",
};

export const ROTULOS_CURTOS_DECISAO: Record<string, string> = {
  BLOQUEAR: "Bloquear",
  PEDIR_CONFIRMACAO: "Pedir confirmação",
  APROVAR: "Aprovar",
};

// --- Issue #43 ---
export const LEGENDA_FILA =
  "Transações de março de 2025, da mais arriscada para a menos arriscada. O modelo decide na hora; a IA audita em seguida.";
export const INDICADOR_NA_FILA = "Na fila";
export const FILTRO_DECISOES = "Mostrar decisões";
export const FILTRO_VAZIO =
  "Nenhuma transação com os filtros escolhidos. Marque ao menos uma decisão.";
export const MOSTRANDO = (mostradas: string, total: string) =>
  `Mostrando ${mostradas} de ${total} transações.`;
export const COLUNAS_FILA = {
  id: "ID",
  nota: "Nota",
  decisao: "Decisão",
  valor: "Valor",
  dataHora: "Data e hora",
  tipo: "Tipo",
  sinais: "Sinais",
};
export const ROTULO_TABELA_FILA =
  "Fila de alertas: clique numa linha para analisar";
export const ABRIR_TRANSACAO = (id: number) => `Abrir a transação ${id}`;
export const ITENS_POR_PAGINA = "Itens por página";
export const PAGINACAO = {
  intervaloItens: (min: number, max: number, total: number) =>
    `${min.toLocaleString("pt-BR")}–${max.toLocaleString("pt-BR")} de ${total.toLocaleString("pt-BR")}`,
  intervaloPaginas: (_atual: number, total: number) => `de ${total} páginas`,
  anterior: "Página anterior",
  proxima: "Próxima página",
  pagina: "Página",
};
export const SELECIONE_TRANSACAO =
  "Selecione uma transação na fila para ver a análise.";
export const TITULO_PAINEL = (id: number) => `Transação ${id}`;
export const TITULO_DECISAO_MODELO = "Decisão do modelo";
export const LEGENDA_LATENCIA = (ms: string) =>
  `Decidido em ${ms} ms, na hora da compra.`;
export const TITULO_SINAIS = (n: number) => `Sinais de alerta (${n})`;
export const SEM_SINAIS =
  "Nenhum sinal de alerta: a transação segue o padrão das compras legítimas.";
export const TITULO_CONTRIBUICOES = "O que pesou na nota";
export const LEGENDA_CONTRIBUICOES =
  "Barras para a direita aumentaram o risco; para a esquerda, diminuíram.";
export const SEM_CONTRIBUICOES =
  "As contribuições de cada variável ainda não estão disponíveis.";
export const TITULO_EXPLICACAO = "Explicação do modelo";
export const TITULO_AUDITORIA = "Auditoria da IA";
export const AUDITORIA_PENDENTE = "A IA está auditando esta decisão…";
export const AUDITORIA_DEMOROU =
  "A auditoria demorou mais que o esperado. A decisão do modelo continua válida.";
export const ROTULOS_PARECER: Record<string, string> = {
  CONFIRMA: "A IA confirma a decisão do modelo",
  DIVERGE: "A IA diverge do modelo: analise com atenção",
  INCONCLUSIVO: "A IA não chegou a uma conclusão",
};
export const ROTULOS_RISCO_IA: Record<string, string> = {
  BAIXO: "baixo",
  SUSPEITO: "suspeito",
  ALTO: "alto",
};
export const ROTULOS_CONFIANCA: Record<string, string> = {
  BAIXA: "baixa",
  MEDIA: "média",
  ALTA: "alta",
};
export const RISCO_E_CONFIANCA = (risco: string, confianca: string) =>
  `Risco segundo a IA: ${risco} · confiança ${confianca}`;
export const RISCO_INDEFINIDO = "indefinido";
export const EVIDENCIAS_A_FAVOR = "Evidências de risco";
export const EVIDENCIAS_CONTRA = "Evidências contra o risco";
export const DADOS_AUSENTES = "Dados que faltaram";
export const FERRAMENTAS_USADAS = "Ferramentas que a IA usou, na ordem";
export const FONTE_AUDITORIA = (fonte: string, modelo: string, ms: string) =>
  fonte === "watsonx"
    ? `Auditado pelo IBM watsonx.ai (${modelo}) em ${ms} ms.`
    : `Auditado em modo local por regras (watsonx.ai indisponível) em ${ms} ms.`;
export const NOMES_FERRAMENTAS: Record<string, string> = {
  sinais_da_transacao: "Sinais da transação",
  contribuicoes_da_nota: "O que pesou na nota",
  historico_do_cartao: "Histórico do cartão",
  perfil_do_cliente: "Perfil do cliente",
  perfil_do_estabelecimento: "Perfil do estabelecimento",
};
export const TITULO_RESPOSTA = "Sua avaliação";
export const BOTAO_FRAUDE = "Confirmar fraude";
export const BOTAO_LEGITIMA = "Marcar como legítima";
export const RESPOSTA_ATUAL = (resposta: string, quando: string) =>
  `Sua resposta: ${resposta} em ${quando}. Você pode mudar; vale a última.`;
export const SEM_RESPOSTA = "Ainda sem resposta para esta transação.";
export const ERRO_GRAVAR = "Não foi possível gravar a resposta. Tente de novo.";
export const TITULO_HISTORICO = (n: number) =>
  `Histórico do cartão (últimas ${n} compras antes desta)`;
export const HISTORICO_VAZIO = "Nenhuma compra anterior deste cartão na base.";
export const COLUNAS_HISTORICO = {
  dataHora: "Data e hora",
  valor: "Valor",
  tipo: "Tipo",
  modalidade: "Modalidade",
  distancia: "Distância do terminal anterior (km)",
};

// --- Issue #44 ---
// (textos das páginas Desempenho e Como funciona serão adicionados aqui)

// --- Issue #45 ---
// (textos do simulador e da página de respostas serão adicionados aqui)

// --- Issue #48 ---
// (textos de acessibilidade e correções serão adicionados aqui)
