"use client";

/**
 * Painel da matriz (ESPECIFICACAO, seção 17.8): o consolidado da cooperativa, o modelo em toda
 * a base de teste, a comparação entre agências e os blocos do gerente somados.
 */

import { obterMetricasMatriz } from "@/lib/api";
import { useCarregar } from "@/lib/useCarregar";
import type {
  RespostaMetricasFilial,
  RespostaMetricasMatriz,
} from "@/lib/tipos";
import EstadoErro from "@/components/comuns/EstadoErro";
import {
  AcertoModelo,
  BloqueiosEquipe,
  DecisoesPorTipo,
  FraudesAprovadas,
  Indicadores,
} from "@/components/gerente/PaginaPainelAgencia";
import {
  formatarDecimal,
  formatarInteiro,
  formatarMoeda,
  formatarTempoCurto,
} from "@/lib/formatacao";
import {
  CARREGANDO,
  COLUNAS_AGENCIAS,
  DE_N,
  FRAUDES_BLOQUEADAS_ATUAL,
  FRAUDES_BLOQUEADAS_SENTINELA,
  FRAUDES_QUE_PASSARAM,
  LEGENDA_MODELO_BASE,
  LEGENDA_PAINEL_MATRIZ,
  LEGITIMAS_BLOQUEADAS,
  PEDIDOS_CONFIRMACAO,
  PERIODOS,
  ROTULO_TABELA_AGENCIAS,
  SEPARACAO_MODELO,
  TITULO_COMPARACAO_AGENCIAS,
  TITULO_CONSOLIDADO,
  TITULO_MODELO_BASE,
  TITULO_PAINEL_MATRIZ,
  TOTAL_COOPERATIVA,
} from "@/lib/textos";

const n = (valor: number | null | undefined) =>
  valor === null || valor === undefined ? "—" : formatarInteiro(valor);
const taxa = (valor: number | null) =>
  valor === null ? "—" : `${formatarDecimal(valor, 1)}%`;

/** O consolidado no formato do painel do gerente, para reaproveitar os blocos. */
export function consolidadoComoFilial(
  m: RespostaMetricasMatriz,
): RespostaMetricasFilial {
  return {
    ...m.consolidado,
    filial: { id_filial: "matriz", nome: TITULO_CONSOLIDADO },
    periodo: m.periodo,
  };
}

function ModeloNaBase({ m }: { m: RespostaMetricasMatriz }) {
  const modelo = m.modelo;
  if (!modelo) return null;
  const legitimasBloqueadas =
    modelo.sentinela.bloqueadas !== null &&
    modelo.sentinela.fraudes_bloqueadas !== null
      ? modelo.sentinela.bloqueadas - modelo.sentinela.fraudes_bloqueadas
      : null;
  return (
    <section
      className="sc-cartao"
      aria-labelledby="titulo-modelo-base"
      style={{ marginBottom: 16 }}
    >
      <h2 id="titulo-modelo-base" className="sc-painel__subtitulo">
        {TITULO_MODELO_BASE}
      </h2>
      <p className="sc-apoio">{LEGENDA_MODELO_BASE(n(modelo.transacoes))}</p>
      <div className="sc-kpis" style={{ marginTop: 14, marginBottom: 0 }}>
        <div className="sc-kpi">
          <div className="sc-rotulo">{FRAUDES_BLOQUEADAS_SENTINELA}</div>
          <b className="sc-num">
            {DE_N(n(modelo.sentinela.fraudes_bloqueadas), n(modelo.fraudes))}
          </b>
          <small>
            {modelo.pr_auc !== null && modelo.roc_auc !== null
              ? SEPARACAO_MODELO(
                  formatarDecimal(modelo.pr_auc, 2),
                  formatarDecimal(modelo.roc_auc, 2),
                )
              : ""}
          </small>
        </div>
        <div className="sc-kpi sc-kpi--bloqueio">
          <div className="sc-rotulo">{FRAUDES_BLOQUEADAS_ATUAL}</div>
          <b className="sc-num">
            {DE_N(
              n(modelo.sistema_atual.fraudes_bloqueadas),
              n(modelo.fraudes),
            )}
          </b>
          <small>
            {FRAUDES_QUE_PASSARAM(
              n(modelo.sistema_atual.fraudes_nao_bloqueadas),
            )}
          </small>
        </div>
        <div className="sc-kpi">
          <div className="sc-rotulo">{LEGITIMAS_BLOQUEADAS}</div>
          <b className="sc-num">{n(legitimasBloqueadas)}</b>
        </div>
        <div className="sc-kpi sc-kpi--espera">
          <div className="sc-rotulo">{PEDIDOS_CONFIRMACAO}</div>
          <b className="sc-num">{n(modelo.sentinela.confirmacoes)}</b>
        </div>
      </div>
    </section>
  );
}

function ComparacaoAgencias({ m }: { m: RespostaMetricasMatriz }) {
  const linhas = [
    ...m.por_filial.map((f) => ({ nome: f.filial.nome, total: false, d: f })),
    { nome: TOTAL_COOPERATIVA, total: true, d: consolidadoComoFilial(m) },
  ];
  return (
    <section
      className="sc-cartao"
      aria-labelledby="titulo-agencias"
      style={{ marginBottom: 16 }}
    >
      <h2 id="titulo-agencias" className="sc-painel__subtitulo">
        {TITULO_COMPARACAO_AGENCIAS}
      </h2>
      <div className="sc-tabela-rolagem">
        <table
          className="sc-tabela sc-tabela--estatica"
          aria-label={ROTULO_TABELA_AGENCIAS}
        >
          <thead>
            <tr>
              <th scope="col">{COLUNAS_AGENCIAS.agencia}</th>
              <th scope="col" className="sc-direita">
                {COLUNAS_AGENCIAS.compras}
              </th>
              <th scope="col" className="sc-direita">
                {COLUNAS_AGENCIAS.aprovadas}
              </th>
              <th scope="col" className="sc-direita">
                {COLUNAS_AGENCIAS.confirmacoes}
              </th>
              <th scope="col" className="sc-direita">
                {COLUNAS_AGENCIAS.bloqueadas}
              </th>
              <th scope="col" className="sc-direita">
                {COLUNAS_AGENCIAS.protegido}
              </th>
              <th scope="col" className="sc-direita">
                {COLUNAS_AGENCIAS.acerto}
              </th>
              <th scope="col" className="sc-direita">
                {COLUNAS_AGENCIAS.fraudesAprovadas}
              </th>
              <th scope="col" className="sc-direita">
                {COLUNAS_AGENCIAS.tempo}
              </th>
            </tr>
          </thead>
          <tbody>
            {linhas.map(({ nome, total, d }) => (
              <tr key={nome} className={total ? "sc-linha-total" : undefined}>
                <th scope="row">{nome}</th>
                <td className="sc-direita sc-num">{n(d.totais.compras)}</td>
                <td className="sc-direita sc-num">{n(d.totais.aprovadas)}</td>
                <td className="sc-direita sc-num">
                  {n(d.totais.confirmacoes)}
                </td>
                <td className="sc-direita sc-num">{n(d.totais.bloqueadas)}</td>
                <td className="sc-direita sc-num">
                  {formatarMoeda(d.totais.valor_protegido)}
                </td>
                <td className="sc-direita sc-num">
                  {taxa(d.acerto_modelo.taxa)}
                </td>
                <td className="sc-direita sc-num">
                  {n(d.fraudes_aprovadas.total)}
                </td>
                <td className="sc-direita sc-num">
                  {formatarTempoCurto(d.tempo_resposta_mediano_s)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export default function PaginaPainelMatriz() {
  const { dados, erro, recarregar } = useCarregar(obterMetricasMatriz);
  const consolidado = dados ? consolidadoComoFilial(dados) : null;

  return (
    <>
      <h1>{TITULO_PAINEL_MATRIZ}</h1>
      {dados && (
        <p className="sc-filial__descricao">
          {LEGENDA_PAINEL_MATRIZ(
            PERIODOS[dados.periodo] ?? dados.periodo,
            formatarInteiro(dados.consolidado.totais.compras),
            dados.por_filial.length,
          )}
        </p>
      )}
      {erro && <EstadoErro mensagem={erro} aoTentarNovamente={recarregar} />}
      {!dados && !erro && <p className="sc-carregando">{CARREGANDO}</p>}
      {dados && consolidado && (
        <>
          <Indicadores m={consolidado} />
          <ModeloNaBase m={dados} />
          <ComparacaoAgencias m={dados} />
          <div className="sc-grade-gerente">
            <DecisoesPorTipo m={consolidado} />
            <AcertoModelo m={consolidado} />
            <FraudesAprovadas m={consolidado} />
            <BloqueiosEquipe m={consolidado} />
          </div>
        </>
      )}
    </>
  );
}
