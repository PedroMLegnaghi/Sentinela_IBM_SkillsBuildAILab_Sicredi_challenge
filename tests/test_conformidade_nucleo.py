"""Testes de conformidade do núcleo do Sentinela (dados, modelo e agente).

Arquivo do líder, escrito a partir da ESPECIFICACAO.md e independente do código do Bob.
O IBM Bob nunca altera, apaga, renomeia ou pula estes testes (AGENTS.md, seção 1). Se um
teste falhar, o erro está no código: a mensagem diz qual seção da ESPECIFICACAO corrigir.

Grupos e quando rodam:
- estrutura, configuração, sinais e decisão: sempre;
- agente com o modelo salvo e JSON versionados: quando modelos/ existe (também no CI);
- dados preparados e reprodutibilidade: só na máquina com data/transacoes_preparadas.parquet.
  Na máquina de quem executa uma Issue, nenhum teste deste arquivo pode ser pulado.
"""

from __future__ import annotations

import importlib
import json
import math
import re
import shutil
import subprocess
from pathlib import Path

import joblib
import pandas as pd
import pytest
import requests
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import StandardScaler

RAIZ = Path(__file__).resolve().parents[1]
CAMINHO_MODELO = RAIZ / "modelos" / "sentinela.joblib"
CAMINHO_METRICAS = RAIZ / "modelos" / "metricas.json"
CAMINHO_AVALIACAO = RAIZ / "modelos" / "avaliacao_agente.json"
CAMINHO_PREPARADO = RAIZ / "data" / "transacoes_preparadas.parquet"

precisa_modelo = pytest.mark.skipif(
    not CAMINHO_MODELO.exists(), reason="sem modelos/sentinela.joblib"
)
precisa_dados = pytest.mark.skipif(
    not CAMINHO_PREPARADO.exists(),
    reason="sem data/transacoes_preparadas.parquet: rode python -m src.preparar_dados",
)

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

COLUNAS_PREPARADAS = [
    "id_transacao",
    "data_hora",
    "id_cartao",
    "id_cliente",
    "id_estabelecimento",
    "valor",
    "tipo_transacao",
    "modalidade_transacao",
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
    "mcc",
    "decisao_sistema_atual",
    "fraude",
]

FRAUDE = {
    "valor": 400.0,
    "hora": 3,
    "madrugada": 1,
    "credito": 1,
    "nao_presente": 1,
    "ip_pais_desconhecido": 0,
    "vel_cartao_terminal_1h": 45,
    "qtd_transacoes_cartao_1min": 20,
    "qtd_token_carteira_3m": 80,
    "dist_terminal_anterior_km": 300.0,
    "risco_estabelecimento": 45,
    "tipo_transacao": "credito",
    "modalidade_transacao": "cartao_nao_presente",
}

LEGITIMA = {
    "valor": 30.0,
    "hora": 14,
    "madrugada": 0,
    "credito": 0,
    "nao_presente": 0,
    "ip_pais_desconhecido": 0,
    "vel_cartao_terminal_1h": 2,
    "qtd_transacoes_cartao_1min": 1,
    "qtd_token_carteira_3m": 7,
    "dist_terminal_anterior_km": 10.0,
    "risco_estabelecimento": 18,
    "tipo_transacao": "debito",
    "modalidade_transacao": "cartao_presente",
}

DESCRICOES_FRAUDE = [
    ("velocidade_terminal", "Cartão usado 45 vezes em terminais na última hora (normal: até 5)."),
    ("rajada_1min", "20 transações do cartão no último minuto (normal: 1 ou 2)."),
    ("token_carteira", "Token de carteira digital usado 80 vezes em 3 meses (normal: até 14)."),
    ("salto_geografico", "Terminal a 300 km do anterior em menos de uma hora."),
    ("madrugada", "Compra feita de madrugada, às 3h."),
    ("valor_alto", "Valor de R$ 400.00, acima do padrão (mediana das compras: R$ 35)."),
    ("credito_nao_presente", "Compra no crédito sem cartão presente (online)."),
    ("estabelecimento_risco", "Estabelecimento com risco 45 (normal: abaixo de 37)."),
]

ROTULOS_DECISAO = {
    "BLOQUEAR": "Bloquear e enviar ao analista",
    "PEDIR_CONFIRMACAO": "Pedir confirmação ao cliente",
    "APROVAR": "Aprovar",
}

CHAVES_ANALISE = {
    "nota",
    "sinais",
    "decisao",
    "decisao_legivel",
    "explicacao",
    "fonte_explicacao",
}


# --------------------------------------------------------------------------------------------
# Apoio
# --------------------------------------------------------------------------------------------


def _importar(nome: str):
    try:
        return importlib.import_module(nome)
    except Exception as erro:  # noqa: BLE001 - qualquer falha de importação é não conformidade
        pytest.fail(f"Não foi possível importar {nome}: {type(erro).__name__}: {erro}")


def _sinal(identificador: str) -> dict:
    return {"id": identificador, "descricao": f"Sinal {identificador}."}


def _resposta(status: int, corpo: bytes) -> requests.Response:
    resposta = requests.Response()
    resposta.status_code = status
    resposta._content = corpo
    resposta.encoding = "utf-8"
    return resposta


class _OllamaFalso:
    """Substitui a rede: responde ao GET /api/tags e ao POST /api/generate sem Ollama."""

    def __init__(self, tags=None, generate=None):
        self.tags = tags
        self.generate = generate
        self.chamadas: list[dict] = []

    def __call__(self, method, url, **kwargs):
        self.chamadas.append({"metodo": method.upper(), "url": url, **kwargs})
        alvo = self.tags if url.endswith("/api/tags") else self.generate
        if alvo is None:
            raise requests.ConnectionError("rede desligada no teste")
        if isinstance(alvo, Exception):
            raise alvo
        return alvo


@pytest.fixture
def ollama(monkeypatch):
    def instalar(tags=None, generate=None) -> _OllamaFalso:
        falso = _OllamaFalso(tags=tags, generate=generate)

        def requisitar(_sessao, method, url, **kwargs):
            return falso(method, url, **kwargs)

        monkeypatch.setattr(requests.sessions.Session, "request", requisitar)
        return falso

    return instalar


@pytest.fixture(scope="module")
def config():
    return _importar("src.config")


@pytest.fixture(scope="module")
def modulo_agente():
    return _importar("src.agente")


@pytest.fixture(scope="module")
def agente(modulo_agente):
    return modulo_agente.AgenteSentinela()


@pytest.fixture(scope="module")
def base():
    return pd.read_parquet(CAMINHO_PREPARADO)


@pytest.fixture(scope="module")
def marco(base):
    return base[(base["data_hora"] >= "2025-03-01") & (base["data_hora"] < "2025-04-01")]


def _ler_json(caminho: Path) -> dict:
    assert caminho.exists(), f"{caminho.name} não existe. ESPECIFICACAO, seções 7 e 8.6."
    return json.loads(caminho.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------------------------
# Estrutura e configuração (ESPECIFICACAO, seções 2, 3 e 8.1)
# --------------------------------------------------------------------------------------------

ARQUIVOS_DO_NUCLEO = [
    "AGENTS.md",
    "ESPECIFICACAO.md",
    "requirements.txt",
    "requirements-dev.txt",
    "pyproject.toml",
    ".gitignore",
    ".bobignore",
    "conftest.py",
    "src/__init__.py",
    "src/config.py",
    "src/preparar_dados.py",
    "src/treinar_modelo.py",
    "src/agente.py",
    "src/avaliar_agente.py",
    "tests/test_agente.py",
    "modelos/sentinela.joblib",
    "modelos/metricas.json",
    "modelos/avaliacao_agente.json",
]


@pytest.mark.parametrize("relativo", ARQUIVOS_DO_NUCLEO)
def test_arquivo_obrigatorio_do_nucleo_existe(relativo):
    assert (RAIZ / relativo).exists(), f"Falta {relativo}. ESPECIFICACAO, seção 3."


def _linhas_de_requisitos(nome: str) -> list[str]:
    caminho = RAIZ / nome
    assert caminho.exists(), f"Falta {nome}. ESPECIFICACAO, seção 2."
    linhas = caminho.read_text(encoding="utf-8").splitlines()
    return [linha.strip() for linha in linhas if linha.strip() and not linha.startswith("#")]


def test_requirements_tem_so_bibliotecas_permitidas_e_versoes_fixadas():
    permitidas = {
        "pandas",
        "numpy",
        "pyarrow",
        "scikit-learn",
        "joblib",
        "requests",
        "pytest",
        "fastapi",
        "uvicorn",
        "httpx",
    }
    obrigatorias = permitidas - {"numpy"}

    linhas = _linhas_de_requisitos("requirements.txt")
    nomes = {re.split(r"[=<>~!\[ ]", linha)[0].lower() for linha in linhas}
    sem_versao = [linha for linha in linhas if not re.fullmatch(r"[A-Za-z0-9_.\-]+==[\w.]+", linha)]

    assert nomes <= permitidas, f"Bibliotecas não permitidas: {sorted(nomes - permitidas)}"
    assert obrigatorias <= nomes, f"Faltam bibliotecas: {sorted(obrigatorias - nomes)}"
    assert not sem_versao, f"Versão não fixada com ==: {sem_versao}. ESPECIFICACAO, seção 2."


def test_requirements_dev_tem_black_e_ruff_com_versao_fixada():
    linhas = _linhas_de_requisitos("requirements-dev.txt")
    nomes = {linha.split("==")[0].lower() for linha in linhas}

    assert nomes == {"black", "ruff"}, f"requirements-dev.txt deve ter só black e ruff: {nomes}"
    assert all("==" in linha for linha in linhas), "Fixe as versões de black e ruff com =="


def test_nenhum_arquivo_de_dados_esta_versionado():
    git = shutil.which("git")
    if git is None or not (RAIZ / ".git").exists():
        pytest.skip("repositório git não encontrado")
    saida = subprocess.run(  # noqa: S603 - comando fixo, sem entrada externa
        [git, "ls-files"], cwd=RAIZ, capture_output=True, text=True, check=True
    ).stdout.splitlines()

    proibidos = [
        caminho
        for caminho in saida
        if caminho.startswith(("data/", ".venv/")) or caminho.endswith((".csv", ".parquet"))
    ]

    assert not proibidos, f"Arquivos de dados no Git (remova com git rm --cached): {proibidos[:5]}"


def test_gitignore_ignora_a_pasta_de_dados():
    linhas = (RAIZ / ".gitignore").read_text(encoding="utf-8").splitlines()

    assert any(linha.strip() in {"data/", "/data/", "data", "/data"} for linha in linhas)


CONSTANTES = {
    "NOTA_CONFIRMAR": 30,
    "NOTA_BLOQUEAR": 70,
    "MIN_SINAIS_CONFIRMAR": 3,
    "OLLAMA_URL": "http://localhost:11434",
    "OLLAMA_MODELO": "granite4:micro",
    "OLLAMA_TIMEOUT_S": 60,
    "OLLAMA_TIMEOUT_DISPONIBILIDADE_S": 2,
    "SEMENTE": 42,
    "INICIO_TREINO": "2025-01-01",
    "INICIO_TESTE": "2025-03-01",
    "FIM_TESTE": "2025-04-01",
    "HORA_FIM_MADRUGADA": 5,
    "LIMIAR_VELOCIDADE_TERMINAL": 10,
    "LIMIAR_RAJADA_1MIN": 5,
    "LIMIAR_TOKEN_CARTEIRA": 30,
    "LIMIAR_DISTANCIA_KM": 100,
    "LIMIAR_VALOR_ALTO": 150,
    "LIMIAR_RISCO_ESTABELECIMENTO": 40,
    "TAMANHO_AMOSTRA_LEGITIMAS": 2000,
    "ROTULOS_DECISAO": ROTULOS_DECISAO,
    "VARIAVEIS_MODELO": VARIAVEIS_MODELO,
}


@pytest.mark.parametrize(("nome", "esperado"), list(CONSTANTES.items()))
def test_constante_de_config_tem_o_valor_da_especificacao(config, nome, esperado):
    assert hasattr(config, nome), f"src/config.py não define {nome}. ESPECIFICACAO, seção 8.1."

    obtido = getattr(config, nome)

    assert obtido == esperado, f"{nome} = {obtido!r}; esperado {esperado!r}. Seção 8.1."


CAMINHOS = {
    "CAMINHO_CSV": "data/case_transacoes_cartoes_sintetico_900k.csv",
    "CAMINHO_PREPARADO": "data/transacoes_preparadas.parquet",
    "CAMINHO_FEEDBACK": "data/feedback.csv",
    "CAMINHO_MODELO": "modelos/sentinela.joblib",
    "CAMINHO_METRICAS": "modelos/metricas.json",
    "CAMINHO_AVALIACAO": "modelos/avaliacao_agente.json",
}


def test_raiz_de_config_e_a_raiz_do_repositorio(config):
    assert Path(config.RAIZ).resolve() == RAIZ, "RAIZ deve ser a pasta do ESPECIFICACAO.md"


@pytest.mark.parametrize(("nome", "relativo"), list(CAMINHOS.items()))
def test_caminho_de_config_aponta_para_o_arquivo_da_especificacao(config, nome, relativo):
    assert hasattr(config, nome), f"src/config.py não define {nome}. ESPECIFICACAO, seção 8.1."

    obtido = getattr(config, nome)

    assert isinstance(obtido, Path), f"{nome} deve ser pathlib.Path"
    assert obtido.resolve() == (RAIZ / relativo).resolve(), f"{nome} = {obtido}"


# --------------------------------------------------------------------------------------------
# Sinais e decisão (ESPECIFICACAO, seções 8.2 e 8.3)
# --------------------------------------------------------------------------------------------


def test_transacao_fraude_de_exemplo_dispara_oito_sinais_na_ordem_fixa(modulo_agente):
    sinais = modulo_agente.calcular_sinais(dict(FRAUDE))

    assert [s["id"] for s in sinais] == [identificador for identificador, _ in DESCRICOES_FRAUDE]


@pytest.mark.parametrize(("identificador", "descricao"), DESCRICOES_FRAUDE)
def test_descricao_do_sinal_segue_o_texto_da_especificacao(modulo_agente, identificador, descricao):
    sinais = {s["id"]: s for s in modulo_agente.calcular_sinais(dict(FRAUDE))}

    assert identificador in sinais, f"O sinal {identificador} não disparou"
    assert sinais[identificador] == {"id": identificador, "descricao": descricao}


def test_transacao_legitima_de_exemplo_nao_dispara_sinal(modulo_agente):
    assert modulo_agente.calcular_sinais(dict(LEGITIMA)) == []


@pytest.mark.parametrize("vazio", [None, float("nan")], ids=["None", "NaN"])
def test_campos_vazios_nunca_disparam_sinal_nem_geram_erro(modulo_agente, vazio):
    transacao = dict.fromkeys(FRAUDE, vazio)

    assert modulo_agente.calcular_sinais(transacao) == []


LIMITES = [
    ({"vel_cartao_terminal_1h": 10}, ["velocidade_terminal"]),
    ({"vel_cartao_terminal_1h": 9.9}, []),
    ({"qtd_transacoes_cartao_1min": 5}, ["rajada_1min"]),
    ({"qtd_transacoes_cartao_1min": 4}, []),
    ({"qtd_token_carteira_3m": 30}, ["token_carteira"]),
    ({"qtd_token_carteira_3m": 29}, []),
    ({"dist_terminal_anterior_km": 100.0}, []),
    ({"dist_terminal_anterior_km": 100.5}, ["salto_geografico"]),
    ({"madrugada": 1, "hora": 4}, ["madrugada"]),
    ({"valor": 150.0}, []),
    ({"valor": 150.01}, ["valor_alto"]),
    ({"credito": 1, "nao_presente": 1}, ["credito_nao_presente"]),
    ({"credito": 1, "nao_presente": 0}, []),
    ({"ip_pais_desconhecido": 1}, ["ip_desconhecido"]),
    ({"risco_estabelecimento": 40}, ["estabelecimento_risco"]),
    ({"risco_estabelecimento": 39.9}, []),
]


@pytest.mark.parametrize(("mudanca", "esperado"), LIMITES, ids=str)
def test_limiar_de_cada_sinal_segue_a_especificacao(modulo_agente, mudanca, esperado):
    transacao = {**LEGITIMA, **mudanca}

    sinais = modulo_agente.calcular_sinais(transacao)

    assert [s["id"] for s in sinais] == esperado, f"Seção 8.2, entrada {mudanca}"


DECISOES = [
    (10, [], "APROVAR"),
    (29.9, [], "APROVAR"),
    (29.9, ["a", "b"], "APROVAR"),
    (30, [], "PEDIR_CONFIRMACAO"),
    (50, [], "PEDIR_CONFIRMACAO"),
    (69.9, [], "PEDIR_CONFIRMACAO"),
    (0, ["a", "b", "c"], "PEDIR_CONFIRMACAO"),
    (69.9, ["a", "b", "c", "d", "e", "f", "g", "h"], "PEDIR_CONFIRMACAO"),
    (70, [], "BLOQUEAR"),
    (90, [], "BLOQUEAR"),
    (5, ["ip_desconhecido"], "BLOQUEAR"),
]


@pytest.mark.parametrize(("nota", "ids", "esperado"), DECISOES)
def test_decidir_segue_a_ordem_das_regras(modulo_agente, nota, ids, esperado):
    sinais = [_sinal(identificador) for identificador in ids]

    assert modulo_agente.decidir(nota, sinais) == esperado, f"Seção 8.3: nota {nota}, sinais {ids}"


# --------------------------------------------------------------------------------------------
# Disponibilidade do IBM Granite (ESPECIFICACAO, seção 8.5)
# --------------------------------------------------------------------------------------------


def test_granite_disponivel_devolve_falso_quando_a_conexao_falha(modulo_agente, ollama):
    ollama()

    assert modulo_agente.granite_disponivel() is False


def test_granite_disponivel_devolve_falso_com_status_diferente_de_200(modulo_agente, ollama):
    ollama(tags=_resposta(500, b"{}"))

    assert modulo_agente.granite_disponivel() is False


def test_granite_disponivel_consulta_api_tags_e_devolve_verdadeiro(modulo_agente, ollama):
    falso = ollama(tags=_resposta(200, b'{"models": []}'))

    disponivel = modulo_agente.granite_disponivel()

    assert disponivel is True
    assert falso.chamadas[0]["metodo"] == "GET"
    assert falso.chamadas[0]["url"] == "http://localhost:11434/api/tags"
    assert falso.chamadas[0].get("timeout") == 2


# --------------------------------------------------------------------------------------------
# Agente com o modelo salvo (ESPECIFICACAO, seções 7, 8.4 e 8.5)
# --------------------------------------------------------------------------------------------


def test_agente_sem_modelo_levanta_erro_com_a_mensagem_da_especificacao(modulo_agente, tmp_path):
    mensagem = "Modelo não encontrado. Rode: python -m src.treinar_modelo"

    with pytest.raises(FileNotFoundError, match=re.escape(mensagem)):
        modulo_agente.AgenteSentinela(caminho_modelo=tmp_path / "inexistente.joblib")


@precisa_modelo
def test_pipeline_salvo_tem_os_tres_passos_da_especificacao():

    modelo = joblib.load(CAMINHO_MODELO)

    assert isinstance(modelo, Pipeline), "O modelo salvo deve ser um sklearn Pipeline (seção 7)"
    passos = [passo for _, passo in modelo.steps]
    assert [type(p) for p in passos] == [SimpleImputer, StandardScaler, LogisticRegression]
    assert passos[0].strategy == "median"
    assert passos[0].add_indicator is True
    assert passos[2].class_weight == "balanced"
    assert passos[2].max_iter == 2000
    assert passos[2].random_state == 42


@precisa_modelo
def test_pipeline_salvo_usa_somente_as_variaveis_do_modelo():

    modelo = joblib.load(CAMINHO_MODELO)

    assert hasattr(modelo, "feature_names_in_"), "Treine com DataFrame de VARIAVEIS_MODELO"
    assert list(modelo.feature_names_in_) == VARIAVEIS_MODELO, "Seção 7: entrada do modelo"


@precisa_modelo
def test_tres_coeficientes_mais_fortes_sao_distancia_rajada_e_velocidade():

    modelo = joblib.load(CAMINHO_MODELO)
    coeficientes = pd.Series(modelo.steps[-1][1].coef_[0][: len(VARIAVEIS_MODELO)])
    coeficientes.index = VARIAVEIS_MODELO

    mais_fortes = set(coeficientes.abs().nlargest(3).index)

    assert mais_fortes == {
        "dist_terminal_anterior_km",
        "qtd_transacoes_cartao_1min",
        "vel_cartao_terminal_1h",
    }


@precisa_modelo
def test_pontuar_da_nota_perto_de_100_para_a_fraude_de_exemplo(agente):
    nota = agente.pontuar(dict(FRAUDE))

    assert isinstance(nota, float)
    assert nota >= 95


@precisa_modelo
def test_pontuar_da_nota_perto_de_0_para_a_legitima_de_exemplo(agente):
    assert agente.pontuar(dict(LEGITIMA)) <= 5


@precisa_modelo
def test_pontuar_arredonda_a_nota_com_uma_casa(agente):
    transacao = {**LEGITIMA, "valor": 151.37, "qtd_token_carteira_3m": 22}

    nota = agente.pontuar(transacao)

    assert nota == round(nota, 1)
    assert 0 <= nota <= 100


@precisa_modelo
@pytest.mark.parametrize("transacao", [{}, dict.fromkeys(VARIAVEIS_MODELO)], ids=["vazia", "None"])
def test_pontuar_aceita_chave_ausente_ou_none(agente, transacao):
    nota = agente.pontuar(transacao)

    assert 0 <= nota <= 100


@precisa_modelo
def test_analisar_devolve_exatamente_as_seis_chaves(agente):
    resultado = agente.analisar(dict(LEGITIMA), usar_llm=False)

    assert set(resultado) == CHAVES_ANALISE


@precisa_modelo
@pytest.mark.parametrize(
    ("transacao", "decisao"), [(FRAUDE, "BLOQUEAR"), (LEGITIMA, "APROVAR")], ids=["fraude", "legit"]
)
def test_analisar_sem_llm_decide_e_explica_por_regras(agente, transacao, decisao):
    resultado = agente.analisar(dict(transacao), usar_llm=False)

    assert resultado["decisao"] == decisao
    assert resultado["decisao_legivel"] == ROTULOS_DECISAO[decisao]
    assert resultado["fonte_explicacao"] == "regras"


@precisa_modelo
def test_texto_de_reserva_com_sinais_segue_a_especificacao(agente, modulo_agente):
    sinais = modulo_agente.calcular_sinais(dict(FRAUDE))
    motivos = " ".join(s["descricao"] for s in sinais)
    esperado = f"Decisão: Bloquear e enviar ao analista (nota 99.5/100). Motivos: {motivos}"

    texto, fonte = agente.explicar(dict(FRAUDE), 99.5, sinais, "BLOQUEAR", usar_llm=False)

    assert (texto, fonte) == (esperado, "regras")


@precisa_modelo
def test_texto_de_reserva_sem_sinais_segue_a_especificacao(agente):
    esperado = (
        "Decisão: Aprovar (nota 0.3/100). Nenhum sinal de alerta foi encontrado; "
        "a transação segue o padrão de compras legítimas."
    )

    texto, fonte = agente.explicar(dict(LEGITIMA), 0.3, [], "APROVAR", usar_llm=False)

    assert (texto, fonte) == (esperado, "regras")


FALHAS_DO_GRANITE = {
    "ollama_fora_do_ar": {},
    "generate_estoura_tempo": {
        "tags": _resposta(200, b"{}"),
        "generate": requests.Timeout("tempo esgotado"),
    },
    "generate_status_500": {"tags": _resposta(200, b"{}"), "generate": _resposta(500, b"{}")},
    "generate_json_invalido": {
        "tags": _resposta(200, b"{}"),
        "generate": _resposta(200, b"isto nao e json"),
    },
    "generate_sem_campo_response": {
        "tags": _resposta(200, b"{}"),
        "generate": _resposta(200, b'{"done": true}'),
    },
    "generate_resposta_vazia": {
        "tags": _resposta(200, b"{}"),
        "generate": _resposta(200, b'{"response": ""}'),
    },
}


@precisa_modelo
@pytest.mark.parametrize("cenario", list(FALHAS_DO_GRANITE))
def test_explicar_usa_texto_de_reserva_quando_o_granite_falha(agente, ollama, cenario):
    ollama(**FALHAS_DO_GRANITE[cenario])
    reserva, _ = agente.explicar(dict(LEGITIMA), 0.3, [], "APROVAR", usar_llm=False)

    texto, fonte = agente.explicar(dict(LEGITIMA), 0.3, [], "APROVAR", usar_llm=True)

    assert (texto, fonte) == (reserva, "regras"), f"Seção 8.5, cenário {cenario}"


@precisa_modelo
def test_explicar_usa_o_texto_do_granite_quando_a_resposta_e_valida(agente, ollama, modulo_agente):
    corpo = json.dumps({"response": "Texto do Granite."}).encode("utf-8")
    falso = ollama(tags=_resposta(200, b"{}"), generate=_resposta(200, corpo))
    sinais = modulo_agente.calcular_sinais(dict(FRAUDE))

    texto, fonte = agente.explicar(dict(FRAUDE), 99.5, sinais, "BLOQUEAR", usar_llm=True)

    assert (texto, fonte) == ("Texto do Granite.", "granite")
    pedido = falso.chamadas[-1]
    assert pedido["metodo"] == "POST"
    assert pedido["url"] == "http://localhost:11434/api/generate"
    assert pedido["timeout"] == 60
    corpo_enviado = pedido["json"]
    assert corpo_enviado["model"] == "granite4:micro"
    assert corpo_enviado["stream"] is False
    assert corpo_enviado["options"] == {"temperature": 0.2, "num_predict": 200}
    prompt = corpo_enviado["prompt"]
    assert prompt.startswith("Você é um assistente de prevenção a fraudes de uma cooperativa")
    assert "Decisão: Bloquear e enviar ao analista" in prompt
    assert "Nota de risco: 99.5/100" in prompt
    assert "Sinais de alerta:" in prompt
    assert all(f"- {s['descricao']}" in prompt for s in sinais)


@precisa_modelo
def test_analisar_lote_coincide_com_analisar_e_nao_altera_a_entrada(agente):
    entrada = pd.DataFrame([FRAUDE, LEGITIMA, {**LEGITIMA, "qtd_token_carteira_3m": 31}])
    colunas_antes = list(entrada.columns)

    lote = agente.analisar_lote(entrada)

    assert list(entrada.columns) == colunas_antes, "analisar_lote deve devolver uma cópia"
    assert (lote["nota"] == lote["nota"].round(1)).all(), "Nota do lote com 1 casa (seção 8.4)"
    for posicao, transacao in enumerate(entrada.to_dict("records")):
        individual = agente.analisar(transacao, usar_llm=False)
        assert lote["nota"].iloc[posicao] == pytest.approx(individual["nota"], abs=0.05)
        assert lote["decisao"].iloc[posicao] == individual["decisao"]
        assert int(lote["n_sinais"].iloc[posicao]) == len(individual["sinais"])


def _base_falsa() -> pd.DataFrame:
    datas = pd.date_range("2025-02-01 10:00", periods=12, freq="D")
    linhas = [
        {"id_transacao": i, "id_cartao": "cartao-a", "data_hora": data, "valor": 10.0 + i}
        for i, data in enumerate(datas)
    ]
    linhas.append(
        {"id_transacao": 99, "id_cartao": "cartao-b", "data_hora": datas[5], "valor": 5.0}
    )
    return pd.DataFrame(linhas)


@precisa_modelo
def test_historico_traz_as_ultimas_n_da_mais_recente_para_a_mais_antiga(modulo_agente):
    agente = modulo_agente.AgenteSentinela(base=_base_falsa())

    historico = agente.historico_cartao("cartao-a", n=10)

    assert list(historico["id_transacao"]) == list(range(11, 1, -1))


@precisa_modelo
def test_historico_considera_so_transacoes_anteriores_ao_momento(modulo_agente):
    agente = modulo_agente.AgenteSentinela(base=_base_falsa())

    historico = agente.historico_cartao("cartao-a", antes_de=pd.Timestamp("2025-02-04"), n=10)

    assert list(historico["id_transacao"]) == [2, 1, 0]


@precisa_modelo
@pytest.mark.parametrize(
    ("base_falsa", "cartao"),
    [(False, "cartao-a"), (True, ""), (True, None), (True, "cartao-inexistente")],
    ids=["sem_base", "cartao_vazio", "cartao_none", "cartao_sem_transacoes"],
)
def test_historico_devolve_tabela_vazia_quando_nao_ha_o_que_mostrar(
    modulo_agente, base_falsa, cartao
):
    agente = modulo_agente.AgenteSentinela(base=_base_falsa() if base_falsa else None)

    historico = agente.historico_cartao(cartao)

    assert isinstance(historico, pd.DataFrame)
    assert historico.empty


# --------------------------------------------------------------------------------------------
# JSON versionados em modelos/ (ESPECIFICACAO, seções 7, 8.6 e 11)
# --------------------------------------------------------------------------------------------


def test_metricas_tem_exatamente_as_chaves_e_os_numeros_da_especificacao():
    metricas = _ler_json(CAMINHO_METRICAS)

    assert set(metricas) == {
        "modelo",
        "treino",
        "teste",
        "pr_auc",
        "roc_auc",
        "limiares",
        "comparacao_hgb",
        "sistema_atual",
    }
    assert metricas["modelo"] == "regressao_logistica"
    assert metricas["treino"] == {"linhas": 25923, "fraudes": 92}
    assert metricas["teste"] == {"linhas": 13608, "fraudes": 54}
    assert metricas["pr_auc"] >= 0.99
    assert metricas["roc_auc"] >= 0.99
    assert set(metricas["comparacao_hgb"]) == {"pr_auc", "roc_auc"}
    assert metricas["sistema_atual"] == {
        "bloqueadas": 26,
        "fraudes_bloqueadas": 26,
        "fraudes_total": 54,
    }


def test_metricas_tem_os_quatro_cortes_e_os_tres_primeiros_pegam_as_54_fraudes():
    limiares = _ler_json(CAMINHO_METRICAS)["limiares"]

    assert [item["limiar"] for item in limiares] == [30, 50, 70, 90]
    for item in limiares:
        assert set(item) == {"limiar", "alertas", "fraudes_detectadas", "precisao", "recall"}
    for item in limiares[:3]:
        assert (item["alertas"], item["fraudes_detectadas"]) == (54, 54), item
        assert item["precisao"] == pytest.approx(1.0)
        assert item["recall"] == pytest.approx(1.0)


def test_avaliacao_do_agente_tem_os_numeros_da_especificacao():
    avaliacao = _ler_json(CAMINHO_AVALIACAO)
    sentinela = avaliacao.get("sentinela", {})

    assert set(avaliacao) == {
        "periodo",
        "transacoes",
        "fraudes_total",
        "sentinela",
        "sistema_atual",
    }
    assert avaliacao["periodo"] == "2025-03"
    assert (avaliacao["transacoes"], avaliacao["fraudes_total"]) == (13608, 54)
    assert (sentinela["bloqueadas"], sentinela["fraudes_bloqueadas"]) == (54, 54)
    assert sentinela["fraudes_em_confirmacao"] == 0
    assert sentinela["fraudes_aprovadas"] == 0
    assert abs(sentinela["confirmacoes"] - 159) <= 5
    total = sentinela["bloqueadas"] + sentinela["confirmacoes"] + sentinela["aprovadas"]
    assert total == 13608
    assert avaliacao["sistema_atual"] == {
        "bloqueadas": 26,
        "fraudes_bloqueadas": 26,
        "fraudes_nao_bloqueadas": 28,
    }


# --------------------------------------------------------------------------------------------
# Dados preparados (ESPECIFICACAO, seções 6 e 11) - só com data/ presente
# --------------------------------------------------------------------------------------------


@precisa_dados
def test_parquet_tem_as_21_colunas_na_ordem_e_todas_as_linhas(base):
    assert list(base.columns) == COLUNAS_PREPARADAS, "Seção 6: colunas e ordem"
    assert len(base) == 160000
    assert base["id_transacao"].tolist() == list(range(160000)), "id = linha do CSV, desde 0"


@precisa_dados
def test_parquet_tem_os_tipos_da_especificacao(base):
    inteiros = ["id_transacao", "madrugada", "credito", "nao_presente", "ip_pais_desconhecido"]
    inteiros.append("fraude")
    decimais = ["valor", "hora", *VARIAVEIS_MODELO[6:], "mcc"]

    errados = [c for c in inteiros if str(base[c].dtype) != "int64"]
    errados += [c for c in decimais if str(base[c].dtype) != "float64"]

    assert not errados, f"Tipos errados (seção 6): {errados}"
    assert pd.api.types.is_datetime64_any_dtype(base["data_hora"])


@precisa_dados
def test_parquet_tem_146_fraudes_so_entre_janeiro_e_marco(base):
    fraudes = base[base["fraude"] == 1]

    por_mes = fraudes["data_hora"].dt.month.value_counts().to_dict()

    assert len(fraudes) == 146, "Rótulo é feedback_label, não fraud (seção 5)"
    assert por_mes == {1: 52, 2: 40, 3: 54}


@precisa_dados
def test_parquet_tem_as_contagens_de_tipo_vazios_e_ip_desconhecido(base):
    sem_data = base["data_hora"].isna()
    ip_zz = base["ip_pais_desconhecido"] == 1

    assert base["tipo_transacao"].value_counts().to_dict() == {"debito": 96287, "credito": 63713}
    assert int(sem_data.sum()) == 311
    assert int(base.loc[sem_data, "fraude"].sum()) == 0
    assert int(ip_zz.sum()) == 38
    assert int(base.loc[ip_zz, "fraude"].sum()) == 38


@precisa_dados
def test_parquet_nao_preenche_vazios_das_variaveis_comportamentais(base):
    fracoes = base[VARIAVEIS_MODELO[6:]].isna().mean()

    fora = fracoes[(fracoes < 0.07) | (fracoes > 0.09)]

    assert fora.empty, f"Cerca de 8% de vazios esperado (seção 6): {fora.round(3).to_dict()}"


@precisa_dados
def test_parquet_deriva_as_colunas_binarias_corretamente(base):
    madrugada = (base["hora"] < 5).astype("int64")
    credito = (base["tipo_transacao"] == "credito").astype("int64")
    nao_presente = (base["modalidade_transacao"] == "cartao_nao_presente").astype("int64")

    assert (base["madrugada"] == madrugada).all()
    assert (base["credito"] == credito).all()
    assert (base["nao_presente"] == nao_presente).all()
    assert set(base["decisao_sistema_atual"].dropna().unique()) <= {"approve", "deny"}


# --------------------------------------------------------------------------------------------
# Reprodutibilidade: os arquivos de modelos/ saem do código atual (seções 7 e 8.6)
# --------------------------------------------------------------------------------------------


@precisa_dados
@precisa_modelo
def test_modelo_salvo_e_o_que_a_especificacao_treina_com_os_dados_atuais(base, marco):

    treino = base[(base["data_hora"] >= "2025-01-01") & (base["data_hora"] < "2025-03-01")]
    referencia = make_pipeline(
        SimpleImputer(strategy="median", add_indicator=True),
        StandardScaler(),
        LogisticRegression(class_weight="balanced", max_iter=2000, random_state=42),
    ).fit(treino[VARIAVEIS_MODELO], treino["fraude"])
    salvo = joblib.load(CAMINHO_MODELO)

    diferenca = abs(
        salvo.predict_proba(marco[VARIAVEIS_MODELO])[:, 1]
        - referencia.predict_proba(marco[VARIAVEIS_MODELO])[:, 1]
    ).max()

    assert diferenca * 100 < 0.01, "Rode de novo python -m src.treinar_modelo (seção 7)"


@precisa_dados
@precisa_modelo
def test_avaliacao_salva_bate_com_o_agente_atual(agente, marco):
    lote = agente.analisar_lote(marco)
    fraude = lote["fraude"] == 1
    negada = lote["decisao_sistema_atual"] == "deny"

    def contar(decisao: str) -> tuple[int, int]:
        escolhidas = lote["decisao"] == decisao
        return int(escolhidas.sum()), int((escolhidas & fraude).sum())

    bloqueadas, confirmacoes, aprovadas = (
        contar(d) for d in ("BLOQUEAR", "PEDIR_CONFIRMACAO", "APROVAR")
    )
    esperado = {
        "periodo": "2025-03",
        "transacoes": len(lote),
        "fraudes_total": int(fraude.sum()),
        "sentinela": {
            "bloqueadas": bloqueadas[0],
            "fraudes_bloqueadas": bloqueadas[1],
            "confirmacoes": confirmacoes[0],
            "fraudes_em_confirmacao": confirmacoes[1],
            "aprovadas": aprovadas[0],
            "fraudes_aprovadas": aprovadas[1],
        },
        "sistema_atual": {
            "bloqueadas": int(negada.sum()),
            "fraudes_bloqueadas": int((negada & fraude).sum()),
            "fraudes_nao_bloqueadas": int((~negada & fraude).sum()),
        },
    }

    assert _ler_json(CAMINHO_AVALIACAO) == esperado, "Rode de novo python -m src.avaliar_agente"


@precisa_dados
@precisa_modelo
def test_analisar_lote_coincide_com_analisar_em_transacoes_reais(agente, marco):
    amostra = pd.concat(
        [marco[marco["fraude"] == 1], marco[marco["fraude"] == 0].sample(250, random_state=42)]
    )
    lote = agente.analisar_lote(amostra)

    divergencias = 0
    for posicao, transacao in enumerate(amostra.to_dict("records")):
        individual = agente.analisar(transacao, usar_llm=False)
        mesma_nota = math.isclose(lote["nota"].iloc[posicao], individual["nota"], abs_tol=0.05)
        mesma_decisao = lote["decisao"].iloc[posicao] == individual["decisao"]
        mesmos_sinais = int(lote["n_sinais"].iloc[posicao]) == len(individual["sinais"])
        divergencias += not (mesma_nota and mesma_decisao and mesmos_sinais)

    assert divergencias == 0, f"{divergencias} transações com resultado diferente (seção 8.4)"
