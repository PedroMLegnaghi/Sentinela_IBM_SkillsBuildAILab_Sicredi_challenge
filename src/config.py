"""Constantes globais do projeto Sentinela."""

from pathlib import Path

# Raiz do repositório (pasta que contém este pacote)
RAIZ = Path(__file__).resolve().parent.parent

# Caminhos de dados e modelos
CAMINHO_CSV = RAIZ / "data" / "case_transacoes_cartoes_sintetico_900k.csv.gz"
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
