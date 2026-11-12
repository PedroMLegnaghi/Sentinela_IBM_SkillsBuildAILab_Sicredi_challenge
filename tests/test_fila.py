"""Testes de montar_fila, contar_por_decisao e verificar_arquivos (design, seção 13.1).

Usa uma base falsa de fevereiro e março, com e sem fraude,
e uma função analisar_lote falsa que não acessa o modelo.
"""

import pandas as pd

from src.interface import textos
from src.interface.dados import contar_por_decisao, montar_fila, verificar_arquivos


def _base_falsa() -> pd.DataFrame:
    """Base com 10 linhas em fevereiro e 20 em março, fraudes nos ids 3, 12 e 25."""
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


def _analisar_lote_falso(df: pd.DataFrame) -> pd.DataFrame:
    """Simula analisar_lote sem modelo: fraudes ficam com nota 99."""
    saida = df.copy()
    saida["nota"] = [
        99.0 if f else float(i % 4)
        for i, f in zip(saida["id_transacao"], saida["fraude"], strict=True)
    ]
    saida["n_sinais"] = 0
    saida["decisao"] = ["BLOQUEAR" if f else "APROVAR" for f in saida["fraude"]]
    return saida


def test_montar_fila_usa_so_marco():
    """Apenas transações de março entram na fila."""
    fila = montar_fila(_base_falsa(), _analisar_lote_falso, tamanho_amostra=5, semente=42)

    assert fila["id_transacao"].min() >= 10, "Só março (id >= 10) deve entrar na fila"


def test_montar_fila_inclui_todas_as_fraudes():
    """Todas as fraudes de março estão na fila."""
    fila = montar_fila(_base_falsa(), _analisar_lote_falso, tamanho_amostra=5, semente=42)

    assert {12, 25} <= set(fila["id_transacao"])


def test_montar_fila_amostra_de_legitimas_respeita_tamanho_e_semente():
    """A amostra de legítimas respeita o tamanho pedido."""
    fila = montar_fila(_base_falsa(), _analisar_lote_falso, tamanho_amostra=5, semente=42)

    # 2 fraudes de março + 5 legítimas = 7
    assert len(fila) == 7


def test_montar_fila_e_reproduzivel():
    """Mesmo semente produz o mesmo resultado."""
    base = _base_falsa()
    primeira = montar_fila(base, _analisar_lote_falso, tamanho_amostra=5, semente=42)
    segunda = montar_fila(base, _analisar_lote_falso, tamanho_amostra=5, semente=42)

    assert primeira["id_transacao"].tolist() == segunda["id_transacao"].tolist()


def test_montar_fila_ordena_por_nota_decrescente():
    """A fila é ordenada por nota decrescente (depois id crescente)."""
    fila = montar_fila(_base_falsa(), _analisar_lote_falso, tamanho_amostra=500, semente=42)

    esperado = fila.sort_values(["nota", "id_transacao"], ascending=[False, True])
    assert fila["id_transacao"].tolist() == esperado["id_transacao"].tolist()


def test_montar_fila_remove_colunas_sensiveis():
    """As colunas fraude e decisao_sistema_atual não aparecem na fila."""
    fila = montar_fila(_base_falsa(), _analisar_lote_falso, tamanho_amostra=5, semente=42)

    assert "fraude" not in fila.columns
    assert "decisao_sistema_atual" not in fila.columns


def test_montar_fila_reset_index():
    """O índice começa em 0 e é consecutivo."""
    fila = montar_fila(_base_falsa(), _analisar_lote_falso, tamanho_amostra=5, semente=42)

    assert list(fila.index) == list(range(len(fila)))


def test_montar_fila_limita_amostra_ao_disponivel():
    """Quando tamanho_amostra > legítimas disponíveis, usa todas."""
    fila = montar_fila(_base_falsa(), _analisar_lote_falso, tamanho_amostra=500, semente=42)

    assert len(fila) == 20  # 18 legítimas + 2 fraudes em março


def test_contar_por_decisao_com_decisao_ausente():
    """contar_por_decisao devolve zero para decisão ausente."""
    fila = pd.DataFrame({"decisao": ["BLOQUEAR", "BLOQUEAR", "APROVAR"]})

    contagem = contar_por_decisao(fila)

    assert contagem == {"BLOQUEAR": 2, "PEDIR_CONFIRMACAO": 0, "APROVAR": 1}


def test_verificar_arquivos_ambos_ausentes(tmp_path):
    """Quando ambos os arquivos faltam, devolve os dois erros na ordem certa."""
    erros = verificar_arquivos(tmp_path / "x.parquet", tmp_path / "y.joblib")

    assert erros == [textos.ERRO_SEM_DADOS, textos.ERRO_SEM_MODELO]


def test_verificar_arquivos_nenhum_ausente(tmp_path):
    """Quando ambos existem, devolve lista vazia."""
    (tmp_path / "x.parquet").touch()
    (tmp_path / "y.joblib").touch()

    assert verificar_arquivos(tmp_path / "x.parquet", tmp_path / "y.joblib") == []
