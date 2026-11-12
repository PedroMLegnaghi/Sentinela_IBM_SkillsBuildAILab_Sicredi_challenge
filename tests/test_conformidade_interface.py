"""Testes de conformidade da interface (docs/08-design-da-interface.md e ESPECIFICACAO, seção 10).

Arquivo do líder, independente do código do Bob. O IBM Bob nunca altera, apaga, renomeia ou
pula estes testes (AGENTS.md, seção 12). Se um teste falhar, o erro está no código.

Cada grupo só roda depois da Issue que o implementa:
- Issue #3: a partir do momento em que existem os módulos de apoio em src/interface/;
- Issue #4: quando src/interface/pagina_fila.py deixa de ter o texto "Página em construção";
- Issue #5: quando as páginas Desempenho e Como funciona deixam de ter esse texto.
Os testes que abrem a interface precisam de data/ e do modelo; no CI eles são pulados.
"""

from __future__ import annotations

import ast
import csv
import importlib
import re
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest
import requests
from streamlit.testing.v1 import AppTest

RAIZ = Path(__file__).resolve().parents[1]
INTERFACE = RAIZ / "src" / "interface"
DESIGN = RAIZ / "docs" / "08-design-da-interface.md"
CAMINHO_FEEDBACK = RAIZ / "data" / "feedback.csv"
MODULOS_DE_APOIO = ["tema", "textos", "formatacao", "dados", "feedback"]
EM_CONSTRUCAO = "Página em construção"


def _pagina_pronta(nome: str) -> bool:
    caminho = INTERFACE / f"{nome}.py"
    return caminho.exists() and EM_CONSTRUCAO not in caminho.read_text(encoding="utf-8")


issue3 = pytest.mark.skipif(
    not any((INTERFACE / f"{nome}.py").exists() for nome in MODULOS_DE_APOIO),
    reason="Issue #3 ainda não implementada",
)
issue4 = pytest.mark.skipif(
    not _pagina_pronta("pagina_fila"), reason="Issue #4 ainda não implementada"
)
issue5 = pytest.mark.skipif(
    not (_pagina_pronta("pagina_desempenho") and _pagina_pronta("pagina_como_funciona")),
    reason="Issue #5 ainda não implementada",
)
precisa_dados_e_modelo = pytest.mark.skipif(
    not (
        (RAIZ / "data" / "transacoes_preparadas.parquet").exists()
        and (RAIZ / "modelos" / "sentinela.joblib").exists()
    ),
    reason="sem data/transacoes_preparadas.parquet ou modelos/sentinela.joblib",
)


def _importar(nome: str):
    try:
        return importlib.import_module(nome)
    except Exception as erro:  # noqa: BLE001 - qualquer falha de importação é não conformidade
        pytest.fail(f"Não foi possível importar {nome}: {type(erro).__name__}: {erro}")


def _textos_do_design() -> dict:
    """Lê os nomes e valores exatos do bloco de código da seção 11 do design."""
    if not DESIGN.exists():
        return {}
    secao = DESIGN.read_text(encoding="utf-8").split("## 11. Textos", 1)[-1].split("## 12.", 1)[0]
    bloco = re.search(r"```python\n(.*?)```", secao, re.DOTALL)
    if bloco is None:
        return {}
    arvore = ast.parse(bloco.group(1))
    return {
        no.targets[0].id: ast.literal_eval(no.value)
        for no in arvore.body
        if isinstance(no, ast.Assign) and isinstance(no.targets[0], ast.Name)
    }


TEXTOS_DO_DESIGN = _textos_do_design()


def _rede_desligada(_sessao, method, url, **kwargs):
    """Faz toda chamada HTTP falhar, como se o Ollama estivesse parado."""
    raise requests.ConnectionError(f"rede desligada no teste: {method} {url}")


@pytest.fixture(scope="module")
def sem_rede():
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(requests.sessions.Session, "request", _rede_desligada)
        yield


@pytest.fixture
def feedback_preservado():
    """Guarda o data/feedback.csv da pessoa e o devolve intacto depois do teste."""
    original = CAMINHO_FEEDBACK.read_bytes() if CAMINHO_FEEDBACK.exists() else None
    CAMINHO_FEEDBACK.unlink(missing_ok=True)
    yield CAMINHO_FEEDBACK
    if original is None:
        CAMINHO_FEEDBACK.unlink(missing_ok=True)
    else:
        CAMINHO_FEEDBACK.write_bytes(original)


def _abrir_app(sem_rede):
    app = AppTest.from_file(str(RAIZ / "app.py"), default_timeout=180)
    app.run()
    return app


def _abrir_pagina(nome: str):
    def executar(modulo: str) -> None:
        import importlib as importador  # noqa: PLC0415 - o AppTest roda só o corpo da função

        importador.import_module(f"src.interface.{modulo}").renderizar()

    app = AppTest.from_function(executar, args=(nome,), default_timeout=180)
    app.run()
    return app


# --------------------------------------------------------------------------------------------
# Issue #3 — tema, textos, formatação, feedback, dados e app.py
# --------------------------------------------------------------------------------------------


@issue3
def test_interface_antiga_da_etapa_4_foi_removida():
    restos = [p.name for p in (RAIZ / "pages",) if p.exists()]
    restos += [p.name for p in RAIZ.glob("*.py") if p.name not in {"app.py", "conftest.py"}]

    assert not restos, f"Apague a interface antiga (backlog, Issue #3): {restos}"


@issue3
def test_tema_define_o_estilo_de_cada_decisao():
    tema = _importar("src.interface.tema")
    esperado = {
        "BLOQUEAR": ("Bloquear", "⛔", ":material/block:", "error"),
        "PEDIR_CONFIRMACAO": ("Pedir confirmação", "⚠️", ":material/phone_in_talk:", "warning"),
        "APROVAR": ("Aprovar", "✅", ":material/check_circle:", "success"),
    }

    obtido = {
        chave: (e.rotulo_curto, e.emoji, e.icone, e.tipo_alerta)
        for chave, e in tema.DECISOES.items()
    }

    assert obtido == esperado, "Design, seção 5.2"
    assert tema.ORDEM_DECISOES == ["BLOQUEAR", "PEDIR_CONFIRMACAO", "APROVAR"]


TOKENS = {
    "ICONE_FILA": ":material/list_alt:",
    "ICONE_DESEMPENHO": ":material/monitoring:",
    "ICONE_COMO_FUNCIONA": ":material/help:",
    "ICONE_FRAUDE": ":material/gpp_bad:",
    "ICONE_LEGITIMA": ":material/verified_user:",
    "ICONE_ERRO": ":material/error:",
    "ICONE_GRANITE_ON": ":material/check_circle:",
    "ICONE_GRANITE_OFF": ":material/cloud_off:",
    "PROPORCAO_COLUNAS": (3, 2),
    "ALTURA_TABELA_PX": 560,
    "LINHAS_HISTORICO": 10,
}


@issue3
@pytest.mark.parametrize(("nome", "esperado"), list(TOKENS.items()))
def test_tema_define_o_token_do_design(nome, esperado):
    tema = _importar("src.interface.tema")

    assert getattr(tema, nome, None) == esperado, f"tema.{nome}: design, seções 3 e 5.2"


def test_design_tem_o_bloco_de_textos_da_secao_11():
    assert len(TEXTOS_DO_DESIGN) > 50, "docs/08, seção 11, deve ter o bloco de textos"


@issue3
@pytest.mark.parametrize("nome", sorted(TEXTOS_DO_DESIGN))
def test_textos_tem_o_texto_do_design_com_o_valor_exato(nome):
    textos = _importar("src.interface.textos")

    assert hasattr(textos, nome), f"textos.py não define {nome} (design, seção 11)"
    assert getattr(textos, nome) == TEXTOS_DO_DESIGN[nome], f"{nome} difere do design"


FORMATACOES = [
    ("formatar_moeda", (1234.5,), "R$ 1.234,50"),
    ("formatar_moeda", (None,), "valor indisponível"),
    ("formatar_moeda", (float("nan"),), "valor indisponível"),
    ("formatar_nota", (97.34,), "97,3"),
    ("formatar_nota", (100,), "100,0"),
    ("formatar_inteiro", (2054,), "2.054"),
    ("formatar_decimal", (0.99812, 3), "0,998"),
    ("formatar_percentual", (0.4815,), "48,1%"),
    ("formatar_percentual", (0.0117,), "1,2%"),
    ("formatar_data_hora", (pd.Timestamp("2025-03-15 03:12:40"),), "15/03/2025 03:12"),
    ("formatar_data_hora", (pd.NaT,), "data indisponível"),
    ("formatar_data_hora", (None,), "data indisponível"),
    ("formatar_tipo", ("credito",), "Crédito"),
    ("formatar_tipo", ("xyz",), "xyz"),
    ("formatar_modalidade", ("cartao_nao_presente",), "Não presente"),
    ("rotulo_resposta", ("legitima",), "Transação legítima"),
    ("escapar_markdown", ("R$ 10 e R$ 20",), "R\\$ 10 e R\\$ 20"),
]


@issue3
@pytest.mark.parametrize(("funcao", "argumentos", "esperado"), FORMATACOES)
def test_formatacao_segue_os_exemplos_do_design(funcao, argumentos, esperado):
    formatacao = _importar("src.interface.formatacao")

    assert getattr(formatacao, funcao)(*argumentos) == esperado, f"Design, seção 12: {funcao}"


def _resposta(feedback, id_transacao: int, resposta: str, segundo: int = 0):
    return feedback.RespostaAnalista(
        id_transacao=id_transacao,
        nota=97.3,
        decisao="BLOQUEAR",
        resposta_analista=resposta,
        registrado_em=datetime(2026, 11, 13, 10, 0, segundo),
    )


@issue3
def test_feedback_define_colunas_e_respostas_validas():
    feedback = _importar("src.interface.feedback")

    assert feedback.COLUNAS_FEEDBACK == [
        "registrado_em",
        "id_transacao",
        "nota",
        "decisao",
        "resposta_analista",
    ]
    assert tuple(feedback.RESPOSTAS_VALIDAS) == ("fraude", "legitima")


@issue3
def test_feedback_grava_e_le_a_resposta_criando_a_pasta(tmp_path):
    feedback = _importar("src.interface.feedback")
    caminho = tmp_path / "nova" / "feedback.csv"

    feedback.registrar_resposta(caminho, _resposta(feedback, 7, "fraude"))
    lida = feedback.ler_ultima_resposta(caminho, 7)

    assert lida is not None
    assert (int(lida.id_transacao), lida.resposta_analista, lida.decisao) == (
        7,
        "fraude",
        "BLOQUEAR",
    )
    assert float(lida.nota) == pytest.approx(97.3)
    assert pd.Timestamp(lida.registrado_em) == pd.Timestamp("2026-11-13 10:00:00")


@issue3
def test_feedback_vale_a_ultima_resposta_e_o_cabecalho_aparece_uma_vez(tmp_path):
    feedback = _importar("src.interface.feedback")
    caminho = tmp_path / "feedback.csv"

    feedback.registrar_resposta(caminho, _resposta(feedback, 7, "fraude", 0))
    feedback.registrar_resposta(caminho, _resposta(feedback, 8, "fraude", 1))
    feedback.registrar_resposta(caminho, _resposta(feedback, 7, "legitima", 2))

    with caminho.open(encoding="utf-8", newline="") as arquivo:
        linhas = list(csv.reader(arquivo))
    assert linhas[0] == feedback.COLUNAS_FEEDBACK
    assert len(linhas) == 4
    assert linhas[1][0] == "2026-11-13T10:00:00", "registrado_em em ISO 8601 com segundos"
    assert feedback.ler_ultima_resposta(caminho, 7).resposta_analista == "legitima"


@issue3
def test_feedback_sem_arquivo_ou_sem_resposta_devolve_none(tmp_path):
    feedback = _importar("src.interface.feedback")
    caminho = tmp_path / "feedback.csv"

    assert feedback.ler_ultima_resposta(caminho, 7) is None
    feedback.registrar_resposta(caminho, _resposta(feedback, 8, "fraude"))
    assert feedback.ler_ultima_resposta(caminho, 7) is None


@issue3
def test_feedback_recusa_resposta_invalida_sem_criar_arquivo(tmp_path):
    feedback = _importar("src.interface.feedback")
    caminho = tmp_path / "feedback.csv"

    with pytest.raises(ValueError):
        feedback.registrar_resposta(caminho, _resposta(feedback, 7, "talvez"))
    assert not caminho.exists()


@issue3
def test_feedback_com_cabecalho_diferente_levanta_value_error(tmp_path):
    feedback = _importar("src.interface.feedback")
    caminho = tmp_path / "feedback.csv"
    caminho.write_text("id,resposta\n7,fraude\n", encoding="utf-8")

    with pytest.raises(ValueError):
        feedback.ler_ultima_resposta(caminho, 7)


@issue3
def test_verificar_arquivos_lista_dados_e_modelo_ausentes_na_ordem(tmp_path):
    dados = _importar("src.interface.dados")
    textos = _importar("src.interface.textos")

    erros = dados.verificar_arquivos(tmp_path / "x.parquet", tmp_path / "y.joblib")

    assert erros == [textos.ERRO_SEM_DADOS, textos.ERRO_SEM_MODELO]


@issue3
def test_verificar_arquivos_nao_acusa_nada_com_os_dois_presentes(tmp_path):
    dados = _importar("src.interface.dados")
    (tmp_path / "x.parquet").touch()
    (tmp_path / "y.joblib").touch()

    assert dados.verificar_arquivos(tmp_path / "x.parquet", tmp_path / "y.joblib") == []


def _base_da_fila() -> pd.DataFrame:
    linhas = []
    for i in range(30):
        mes = "2025-02-10" if i < 10 else "2025-03-10"
        linhas.append(
            {
                "id_transacao": i,
                "data_hora": pd.Timestamp(mes) + pd.Timedelta(hours=i),
                "valor": float(i),
                "fraude": int(i in {3, 12, 25}),
                "decisao_sistema_atual": "approve",
            }
        )
    return pd.DataFrame(linhas)


def _lote_falso(df: pd.DataFrame) -> pd.DataFrame:
    saida = df.copy()
    saida["nota"] = [
        99.0 if f else float(i % 4)
        for i, f in zip(saida["id_transacao"], saida["fraude"], strict=True)
    ]
    saida["n_sinais"] = 0
    saida["decisao"] = ["BLOQUEAR" if f else "APROVAR" for f in saida["fraude"]]
    return saida


@issue3
def test_montar_fila_usa_so_marco_com_todas_as_fraudes_e_a_amostra_de_legitimas():
    dados = _importar("src.interface.dados")

    fila = dados.montar_fila(_base_da_fila(), _lote_falso, tamanho_amostra=5, semente=42)

    assert len(fila) == 7
    assert set(fila["id_transacao"]) >= {12, 25}
    assert fila["id_transacao"].min() >= 10, "Só março entra na fila"
    assert "fraude" not in fila.columns
    assert "decisao_sistema_atual" not in fila.columns
    assert list(fila.index) == list(range(7))


@issue3
def test_montar_fila_e_reproduzivel_e_limita_a_amostra_ao_disponivel():
    dados = _importar("src.interface.dados")
    base = _base_da_fila()

    primeira = dados.montar_fila(base, _lote_falso, tamanho_amostra=5, semente=42)
    segunda = dados.montar_fila(base, _lote_falso, tamanho_amostra=5, semente=42)
    tudo = dados.montar_fila(base, _lote_falso, tamanho_amostra=500, semente=42)

    assert primeira["id_transacao"].tolist() == segunda["id_transacao"].tolist()
    assert len(tudo) == 20


@issue3
def test_montar_fila_ordena_por_nota_decrescente_e_id_crescente():
    dados = _importar("src.interface.dados")

    fila = dados.montar_fila(_base_da_fila(), _lote_falso, tamanho_amostra=500, semente=42)

    esperado = fila.sort_values(["nota", "id_transacao"], ascending=[False, True])
    assert fila["id_transacao"].tolist() == esperado["id_transacao"].tolist()


@issue3
def test_contar_por_decisao_devolve_zero_para_decisao_ausente():
    dados = _importar("src.interface.dados")
    fila = pd.DataFrame({"decisao": ["BLOQUEAR", "BLOQUEAR", "APROVAR"]})

    contagem = dados.contar_por_decisao(fila)

    assert contagem == {"BLOQUEAR": 2, "PEDIR_CONFIRMACAO": 0, "APROVAR": 1}


@issue3
@precisa_dados_e_modelo
def test_app_abre_na_fila_com_interruptor_e_estado_do_granite(sem_rede):
    textos = _importar("src.interface.textos")

    app = _abrir_app(sem_rede)

    assert not app.exception, app.exception
    assert [t.value for t in app.title][:1] == [textos.TITULO_FILA]
    assert [t.label for t in app.sidebar.toggle] == [textos.ROTULO_TOGGLE_GRANITE]
    legendas = [c.value for c in app.sidebar.caption]
    assert textos.STATUS_GRANITE_OFF in legendas, "Granite fora do ar deve aparecer na lateral"
    assert textos.RODAPE_DADOS in legendas


# --------------------------------------------------------------------------------------------
# Issue #4 — Fila de alertas e painel da transação (design, seção 7)
# --------------------------------------------------------------------------------------------


@pytest.fixture(scope="module")
def fila_aberta(sem_rede):
    return _abrir_app(sem_rede)


def _numero(texto: str) -> int:
    return int(str(texto).replace(".", ""))


COLUNAS_TABELA = [
    "ID",
    "Nota",
    "Decisão",
    "Valor (R$)",
    "Data e hora",
    "Tipo",
    "Modalidade",
    "Sinais",
]


@issue4
@precisa_dados_e_modelo
def test_fila_abre_sem_erro_com_os_quatro_indicadores_somando_2054(fila_aberta):
    indicadores = {m.label: m.value for m in fila_aberta.metric}

    assert not fila_aberta.exception, fila_aberta.exception
    assert list(indicadores)[:4] == ["Na fila", "Bloquear", "Pedir confirmação", "Aprovar"]
    assert indicadores["Na fila"] == "2.054"
    soma = sum(_numero(indicadores[r]) for r in ("Bloquear", "Pedir confirmação", "Aprovar"))
    assert soma == 2054
    assert _numero(indicadores["Bloquear"]) == 54


@issue4
@precisa_dados_e_modelo
def test_tabela_abre_com_bloquear_e_pedir_confirmacao_ordenada_pela_nota(fila_aberta):
    indicadores = {m.label: m.value for m in fila_aberta.metric}
    tabela = fila_aberta.dataframe[0].value

    assert list(tabela.columns) == COLUNAS_TABELA, "Design, seção 7.3"
    esperadas = _numero(indicadores["Bloquear"]) + _numero(indicadores["Pedir confirmação"])
    assert len(tabela) == esperadas
    assert tabela["Nota"].is_monotonic_decreasing


@issue4
@precisa_dados_e_modelo
def test_painel_abre_a_primeira_transacao_com_faixa_e_fonte_da_explicacao(fila_aberta):
    textos = _importar("src.interface.textos")
    primeiro_id = int(fila_aberta.dataframe[0].value["ID"].iloc[0])
    legendas = [c.value for c in fila_aberta.caption]

    assert textos.TITULO_PAINEL.format(id=primeiro_id) in [h.value for h in fila_aberta.header]
    assert any("Bloquear e enviar ao analista" in e.value for e in fila_aberta.error)
    assert textos.FONTE_REGRAS_INDISPONIVEL in legendas, "Granite fora do ar: design, 7.5"
    assert any(p.proto.text.startswith("Nota de risco:") for p in fila_aberta.get("progress"))


@issue4
@precisa_dados_e_modelo
def test_botoes_de_resposta_tem_o_mesmo_peso_visual(fila_aberta):
    textos = _importar("src.interface.textos")
    botoes = {b.label: b for b in fila_aberta.button}

    assert textos.BOTAO_FRAUDE in botoes
    assert textos.BOTAO_LEGITIMA in botoes
    assert botoes[textos.BOTAO_FRAUDE].proto.type != "primary"
    assert botoes[textos.BOTAO_LEGITIMA].proto.type != "primary"


@issue4
@precisa_dados_e_modelo
def test_confirmar_fraude_grava_a_resposta_e_mostra_a_resposta_atual(sem_rede, feedback_preservado):
    textos = _importar("src.interface.textos")
    app = _abrir_app(sem_rede)
    primeiro_id = int(app.dataframe[0].value["ID"].iloc[0])

    app.button(key=f"fraude_{primeiro_id}").click().run()

    assert not app.exception, app.exception
    with feedback_preservado.open(encoding="utf-8", newline="") as arquivo:
        linhas = list(csv.DictReader(arquivo))
    assert linhas[-1]["id_transacao"] == str(primeiro_id)
    assert linhas[-1]["resposta_analista"] == "fraude"
    prefixo = textos.RESPOSTA_ATUAL.split("{resposta}")[0] + "Fraude confirmada"
    assert any(c.value.startswith(prefixo) for c in app.caption)


@issue4
@precisa_dados_e_modelo
def test_desmarcar_todas_as_decisoes_mostra_o_aviso_de_filtro_vazio(sem_rede):
    textos = _importar("src.interface.textos")
    app = _abrir_app(sem_rede)

    app.pills[0].set_value([]).run()

    assert not app.exception, app.exception
    assert textos.VAZIO_FILTRO in [i.value for i in app.info]
    assert len(app.dataframe) == 0


# --------------------------------------------------------------------------------------------
# Issue #5 — Desempenho e Como funciona (design, seções 8 e 9)
# --------------------------------------------------------------------------------------------


@issue5
@precisa_dados_e_modelo
def test_desempenho_mostra_os_cinco_indicadores_da_avaliacao():
    textos = _importar("src.interface.textos")

    app = _abrir_pagina("pagina_desempenho")
    indicadores = {m.label: (m.value, m.delta) for m in app.metric}

    assert not app.exception, app.exception
    assert [t.value for t in app.title] == [textos.TITULO_DESEMPENHO]
    assert indicadores["Fraudes em março"][0] == "54"
    assert indicadores["Bloqueadas pelo Sentinela"][0] == "54 de 54"
    assert indicadores["Bloqueadas pelo Sentinela"][1] == "+28 em relação ao sistema atual"
    assert indicadores["Bloqueadas pelo sistema atual"][0] == "26 de 54"
    assert indicadores["Compras legítimas bloqueadas"][0] == "0"
    assert abs(_numero(indicadores["Pedidos de confirmação"][0]) - 159) <= 5
    assert textos.AVISO_SINTETICO in [i.value for i in app.info]


@issue5
@precisa_dados_e_modelo
def test_como_funciona_mostra_os_nove_sinais_com_os_limiares_de_config():
    textos = _importar("src.interface.textos")

    app = _abrir_pagina("pagina_como_funciona")
    tabelas = [t.value for t in app.table]

    assert not app.exception, app.exception
    assert [t.value for t in app.title] == [textos.TITULO_COMO]
    assert any(len(t) == 9 for t in tabelas), "Tabela dos 9 sinais (design, seção 9)"
    conteudo = " ".join(str(v) for t in tabelas for v in t.to_numpy().ravel())
    assert "Cartão usado 10 vezes ou mais em terminais na última hora" in conteudo
    assert "{" not in conteudo, "Formate os textos com as constantes de config"
