"use client";

/**
 * Painel do gerente (Issue #99): indicadores da agência, decisões por tipo de compra, acerto do
 * modelo pela resposta dos associados e fraudes que o modelo aprovou. Tela "Filial: gerente".
 */

import { obterMetricasFilial } from "@/lib/api";
import { useCarregar } from "@/lib/useCarregar";
import type { RespostaMetricasFilial } from "@/lib/tipos";
import EstadoErro from "@/components/comuns/EstadoErro";
import {
  formatarDecimal,
  formatarDiaHora,
  formatarInteiro,
  formatarMoeda,
  formatarTempoCurto,
  formatarTipo,
} from "@/lib/formatacao";
import {
  ALERTAS_CERTOS,
  ALERTAS_DESNECESSARIOS,
  ALERTAS_SEM_RESPOSTA,
  ASSOCIADO_E_CARTAO,
  CARREGANDO,
  CARTAO_BLOQUEADO_ETIQUETA,
  DAS_COMPRAS,
  DESCRICAO_BARRA_TIPO,
  DESCRICAO_ROSCA,
  DOS_ALERTAS_RESPONDIDOS,
  EXPLICA_ACERTO,
  EXPLICA_FRAUDES_APROVADAS,
  KPI_APROVADAS,
  KPI_BLOQUEADAS,
  KPI_CONFIRMACOES,
  KPI_TEMPO_RESPOSTA,
  LEGENDA_APROVADAS,
  LEGENDA_BLOQUEADAS,
  LEGENDA_CONFIRMACOES,
  LEGENDA_PAINEL_AGENCIA,
  MEDIANA,
  MODALIDADE_CURTA,
  NENHUMA_FRAUDE_APROVADA,
  PERIODOS,
  PROTEGIDOS,
  SEM_RESPOSTAS_AINDA,
  TIPO_E_MODALIDADE,
  TITULO_ACERTO_MODELO,
  TITULO_DECISOES_TIPO,
  TITULO_FRAUDES_APROVADAS,
  TITULO_PAINEL_AGENCIA,
} from "@/lib/textos";

const pct = (parte: number, todo: number) =>
  todo > 0 ? `${formatarDecimal((parte / todo) * 100, 1)}%` : "—";

function Indicadores({ m }: { m: RespostaMetricasFilial }) {
  const t = m.totais;
  return (
    <div className="sc-kpis">
      <div className="sc-cartao sc-kpi">
        <div className="sc-rotulo">{KPI_APROVADAS}</div>
        <b className="sc-num">{formatarInteiro(t.aprovadas)}</b>
        <small>{DAS_COMPRAS(pct(t.aprovadas, t.compras))}</small>
      </div>
      <div className="sc-cartao sc-kpi sc-kpi--espera">
        <div className="sc-rotulo">{KPI_CONFIRMACOES}</div>
        <b className="sc-num">{formatarInteiro(t.confirmacoes)}</b>
        <small>{DAS_COMPRAS(pct(t.confirmacoes, t.compras))}</small>
      </div>
      <div className="sc-cartao sc-kpi sc-kpi--bloqueio">
        <div className="sc-rotulo">{KPI_BLOQUEADAS}</div>
        <b className="sc-num">{formatarInteiro(t.bloqueadas)}</b>
        <small>{PROTEGIDOS(formatarMoeda(t.valor_protegido))}</small>
      </div>
      <div className="sc-cartao sc-kpi">
        <div className="sc-rotulo">{KPI_TEMPO_RESPOSTA}</div>
        <b className="sc-num">{formatarTempoCurto(m.tempo_resposta_mediano_s)}</b>
        <small>{m.tempo_resposta_mediano_s === null ? SEM_RESPOSTAS_AINDA : MEDIANA}</small>
      </div>
    </div>
  );
}

function DecisoesPorTipo({ m }: { m: RespostaMetricasFilial }) {
  return (
    <section className="sc-cartao" aria-labelledby="titulo-decisoes-tipo">
      <h2 id="titulo-decisoes-tipo" className="sc-painel__subtitulo">
        {TITULO_DECISOES_TIPO}
      </h2>
      <ul className="sc-barras">
        {m.por_tipo.map((linha) => {
          const total = linha.aprovadas + linha.confirmacoes + linha.bloqueadas;
          const rotulo = TIPO_E_MODALIDADE(
            formatarTipo(linha.tipo_transacao),
            MODALIDADE_CURTA[linha.modalidade_transacao] ?? linha.modalidade_transacao,
          );
          const largura = (n: number) => `${total > 0 ? (n / total) * 100 : 0}%`;
          return (
            <li key={`${linha.tipo_transacao}-${linha.modalidade_transacao}`} className="sc-barra-linha">
              <span>{rotulo}</span>
              <span
                className="sc-empilhada"
                role="img"
                aria-label={DESCRICAO_BARRA_TIPO(
                  rotulo,
                  formatarInteiro(linha.aprovadas),
                  formatarInteiro(linha.confirmacoes),
                  formatarInteiro(linha.bloqueadas),
                )}
              >
                <i className="sc-cor-ok" style={{ width: largura(linha.aprovadas) }} />
                <i className="sc-cor-espera" style={{ width: largura(linha.confirmacoes) }} />
                <i className="sc-cor-bloqueio" style={{ width: largura(linha.bloqueadas) }} />
              </span>
              <b className="sc-num">{formatarInteiro(total)}</b>
            </li>
          );
        })}
      </ul>
      <div className="sc-legenda-cores">
        <span><i className="sc-cor-ok" />{LEGENDA_APROVADAS}</span>
        <span><i className="sc-cor-espera" />{LEGENDA_CONFIRMACOES}</span>
        <span><i className="sc-cor-bloqueio" />{LEGENDA_BLOQUEADAS}</span>
      </div>
    </section>
  );
}

function AcertoModelo({ m }: { m: RespostaMetricasFilial }) {
  const a = m.acerto_modelo;
  const taxa = a.taxa === null ? null : `${formatarDecimal(a.taxa, 0)}%`;
  return (
    <section className="sc-cartao" aria-labelledby="titulo-acerto">
      <h2 id="titulo-acerto" className="sc-painel__subtitulo">
        {TITULO_ACERTO_MODELO}
      </h2>
      <div className="sc-acerto">
        {taxa === null ? (
          <p className="sc-apoio">{SEM_RESPOSTAS_AINDA}</p>
        ) : (
          <div
            className="sc-rosca"
            role="img"
            aria-label={DESCRICAO_ROSCA(taxa)}
            style={{ "--sc-taxa": `${a.taxa}%` } as React.CSSProperties}
          >
            <div>
              <b className="sc-num">{taxa}</b>
              <small>{DOS_ALERTAS_RESPONDIDOS}</small>
            </div>
          </div>
        )}
        <ul className="sc-acerto__frases">
          <li>{ALERTAS_CERTOS(formatarInteiro(a.alertas_certos))}</li>
          <li>{ALERTAS_DESNECESSARIOS(formatarInteiro(a.alertas_desnecessarios))}</li>
          <li className="sc-apoio">{ALERTAS_SEM_RESPOSTA(formatarInteiro(a.sem_resposta))}</li>
        </ul>
      </div>
      <p className="sc-apoio" style={{ marginTop: 12 }}>
        {EXPLICA_ACERTO}
      </p>
    </section>
  );
}

function FraudesAprovadas({ m }: { m: RespostaMetricasFilial }) {
  const f = m.fraudes_aprovadas;
  return (
    <section className="sc-cartao" aria-labelledby="titulo-fraudes-aprovadas">
      <h2 id="titulo-fraudes-aprovadas" className="sc-painel__subtitulo">
        {TITULO_FRAUDES_APROVADAS}
      </h2>
      <b className="sc-numero-grande sc-num">{formatarInteiro(f.total)}</b>
      <p style={{ fontSize: "0.875rem", marginTop: 4 }}>{EXPLICA_FRAUDES_APROVADAS}</p>
      <hr className="sc-separador" />
      {f.itens.length === 0 ? (
        <p className="sc-apoio">{NENHUMA_FRAUDE_APROVADA}</p>
      ) : (
        <ul className="sc-lista-simples">
          {f.itens.map((item, i) => (
            <li key={`${item.final_cartao}-${item.data_hora}-${i}`} className="sc-linha">
              <span>
                <b>{ASSOCIADO_E_CARTAO(item.associado, item.final_cartao)}</b>
                <br />
                <small className="sc-apoio sc-num">
                  {formatarDiaHora(item.data_hora)} · {formatarMoeda(item.valor)}
                </small>
              </span>
              <span className="sc-etiqueta sc-etiqueta--bloqueio">{CARTAO_BLOQUEADO_ETIQUETA}</span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

export default function PaginaPainelAgencia() {
  const { dados, erro, recarregar } = useCarregar(obterMetricasFilial);

  return (
    <>
      <h1>{TITULO_PAINEL_AGENCIA}</h1>
      {dados && (
        <p className="sc-filial__descricao">
          {LEGENDA_PAINEL_AGENCIA(
            PERIODOS[dados.periodo] ?? dados.periodo,
            formatarInteiro(dados.totais.compras),
            dados.filial.nome,
          )}
        </p>
      )}
      {erro && <EstadoErro mensagem={erro} aoTentarNovamente={recarregar} />}
      {!dados && !erro && <p className="sc-carregando">{CARREGANDO}</p>}
      {dados && (
        <>
          <Indicadores m={dados} />
          <div className="sc-grade-gerente">
            <DecisoesPorTipo m={dados} />
            <AcertoModelo m={dados} />
            <FraudesAprovadas m={dados} />
          </div>
        </>
      )}
    </>
  );
}
