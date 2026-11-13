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
export const ERRO_API = "Não foi possível carregar os dados. Verifique se a API está em execução (python -m uvicorn src.api.app:app --port 8000) e tente de novo.";
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
// (textos da fila de alertas e painel da transação serão adicionados aqui)

// --- Issue #44 ---
// (textos das páginas Desempenho e Como funciona serão adicionados aqui)

// --- Issue #45 ---
// (textos do simulador e da página de respostas serão adicionados aqui)

// --- Issue #48 ---
// (textos de acessibilidade e correções serão adicionados aqui)
