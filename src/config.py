"""Constantes globais do projeto Sentinela."""

from pathlib import Path

# Raiz do repositório (pasta que contém este pacote)
RAIZ = Path(__file__).resolve().parent.parent

# Caminhos de dados e modelos
CAMINHO_CSV = RAIZ / "data" / "case_transacoes_cartoes_sintetico_900k.csv"
CAMINHO_PREPARADO = RAIZ / "data" / "transacoes_preparadas.parquet"
CAMINHO_FEEDBACK = RAIZ / "data" / "feedback.csv"
CAMINHO_MODELO = RAIZ / "modelos" / "sentinela.joblib"
CAMINHO_METRICAS = RAIZ / "modelos" / "metricas.json"
CAMINHO_AVALIACAO = RAIZ / "modelos" / "avaliacao_agente.json"

# Variáveis de entrada do modelo (ordem exata da seção 7)
VARIAVEIS_MODELO = [
    "valor",
    "hora",
    "madrugada",
    "credito",
    "nao_presente",
    "ip_pais_desconhecido",
    "vel_cartao_terminal_1h",
    "qtd_transacoes_cartao_1min",
    "qtd_token_carteira_3m",
    "dist_terminal_anterior_km",
    "risco_estabelecimento",
]

# Limiares de decisão
NOTA_CONFIRMAR = 30
NOTA_BLOQUEAR = 70
MIN_SINAIS_CONFIRMAR = 3

# Configuração do Ollama
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODELO = "granite4:micro"
OLLAMA_TIMEOUT_S = 60
OLLAMA_TIMEOUT_DISPONIBILIDADE_S = 2

# Semente de aleatoriedade
SEMENTE = 42

# Datas de divisão treino/teste
INICIO_TREINO = "2025-01-01"
INICIO_TESTE = "2025-03-01"
FIM_TESTE = "2025-04-01"

# Hora de corte da madrugada
HORA_FIM_MADRUGADA = 5

# Limiares dos sinais de alerta (seção 8.2)
LIMIAR_VELOCIDADE_TERMINAL = 10
LIMIAR_RAJADA_1MIN = 5
LIMIAR_TOKEN_CARTEIRA = 30
LIMIAR_DISTANCIA_KM = 100
LIMIAR_VALOR_ALTO = 150
LIMIAR_RISCO_ESTABELECIMENTO = 40

# Tamanho da amostra de legítimas na fila de demonstração
TAMANHO_AMOSTRA_LEGITIMAS = 2000

# Rótulos legíveis por decisão (seção 8.3)
ROTULOS_DECISAO = {
    "BLOQUEAR": "Bloquear e enviar ao analista",
    "PEDIR_CONFIRMACAO": "Pedir confirmação ao cliente",
    "APROVAR": "Aprovar",
}

# --- Incrementos ---

# Caminhos dos JSONs gerados pelos scripts dos incrementos
CAMINHO_CUSTOS = RAIZ / "modelos" / "custos.json"
CAMINHO_AVALIACAO_RIGOROSA = RAIZ / "modelos" / "avaliacao_rigorosa.json"
CAMINHO_CENARIO_DIFICIL = RAIZ / "modelos" / "cenario_dificil.json"
CAMINHO_LATENCIA = RAIZ / "modelos" / "latencia.json"
CAMINHO_EDA = RAIZ / "modelos" / "eda.json"
CAMINHO_NOTIFICACOES = RAIZ / "data" / "notificacoes.csv"

# Custo por pedido de confirmação em reais (premissa do time; não é cobrado pelo Sicredi)
CUSTO_PEDIDO_CONFIRMACAO = 1.0

# Repetições do bootstrap para intervalos de confiança (Issue #28)
REPETICOES_BOOTSTRAP = 1000

# Colunas de velocidade usadas na ablação (Issue #28 e #29)
COLUNAS_VELOCIDADE = [
    "vel_cartao_terminal_1h",
    "qtd_transacoes_cartao_1min",
    "qtd_token_carteira_3m",
]
