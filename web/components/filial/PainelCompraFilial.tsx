"use client";

/**
 * Painel de uma compra na filial (Issue #97): o detalhe técnico que o associado não vê
 * (sinais, o que pesou, explicação e parecer da IA), a resposta do associado e o histórico
 * agregado. Pela LGPD, nada de saldo, extrato ou nome completo.
 */

import { obterCompraFilial } from "@/lib/api";
import { useCarregar } from "@/lib/useCarregar";
import CartaoAuditoria from "@/components/painel/CartaoAuditoria";
import GraficoContribuicoes from "@/components/painel/GraficoContribuicoes";
import EstadoErro from "@/components/comuns/EstadoErro";
import EtiquetaSituacaoFilial from "@/components/filial/EtiquetaSituacaoFilial";
import NotaRisco from "@/components/filial/NotaRisco";
import {
  formatarDiaHora,
  formatarInteiro,
  formatarMoeda,
  formatarTipo,
} from "@/lib/formatacao";
import {
  ASSOCIADO_E_CARTAO,
  BLOQUEIO_POR,
  CARREGANDO,
  COMPRA_EM_ANALISE,
  DECISAO_DO_MODELO,
  DETALHE_QUANDO,
  DETALHE_VALOR,
  EXPLICACAO_DO_MODELO,
  HISTORICO_AGREGADO,
  LEITURA_RESPOSTA,
  RESPOSTA_DO_ASSOCIADO,
  RESPOSTA_NAO,
  RESPOSTA_SIM,
  RESUMO_HISTORICO,
  ROTULO_NOTA,
  SEM_RESPOSTA_ASSOCIADO,
  SEM_SINAIS,
  TITULO_ASSOCIADO_FILIAL,
  TITULO_BLOQUEIO,
  TITULO_SINAIS_FILIAL,
} from "@/lib/textos";

export default function PainelCompraFilial({ idCompra }: { idCompra: string }) {
  const { dados, erro, recarregar } = useCarregar(() => obterCompraFilial(idCompra), idCompra);

  if (erro) return <EstadoErro mensagem={erro} aoTentarNovamente={recarregar} />;
  if (!dados) return <p className="sc-carregando">{CARREGANDO}</p>;

  const { compra, analise, auditoria, associado, resposta_associado, bloqueio } = dados;

  return (
    <article className="sc-painel" aria-label={COMPRA_EM_ANALISE}>
      <div className="sc-linha" style={{ alignItems: "flex-start" }}>
        <div>
          <div className="sc-rotulo">{COMPRA_EM_ANALISE}</div>
          <h2 className="sc-painel__titulo">
            {ASSOCIADO_E_CARTAO(associado.nome_abreviado, associado.final_cartao)}
          </h2>
          <span className="sc-apoio">{formatarTipo(compra.tipo_transacao)}</span>
        </div>
        <EtiquetaSituacaoFilial situacao={compra.situacao} />
      </div>

      <dl className="sc-painel__numeros">
        <div>
          <dt className="sc-rotulo">{DETALHE_VALOR}</dt>
          <dd className="sc-num">{formatarMoeda(compra.valor)}</dd>
        </div>
        <div>
          <dt className="sc-rotulo">{ROTULO_NOTA}</dt>
          <dd>
            <NotaRisco nota={analise.nota} />
          </dd>
        </div>
        <div>
          <dt className="sc-rotulo">{DETALHE_QUANDO}</dt>
          <dd className="sc-num">{formatarDiaHora(compra.data_hora)}</dd>
        </div>
      </dl>

      <hr className="sc-separador" />
      <div className="sc-rotulo">{DECISAO_DO_MODELO}</div>
      <p style={{ fontWeight: 700, marginTop: 2 }}>{analise.decisao_legivel}</p>

      <hr className="sc-separador" />
      <h3 className="sc-painel__subtitulo">{TITULO_SINAIS_FILIAL(analise.sinais.length)}</h3>
      {analise.sinais.length === 0 ? (
        <p className="sc-apoio">{SEM_SINAIS}</p>
      ) : (
        <ul className="sc-sinais">
          {analise.sinais.map((s) => (
            <li key={s.id}>{s.descricao}</li>
          ))}
        </ul>
      )}

      <hr className="sc-separador" />
      <GraficoContribuicoes contribuicoes={analise.contribuicoes} />

      <hr className="sc-separador" />
      <h3 className="sc-painel__subtitulo">{EXPLICACAO_DO_MODELO}</h3>
      <p style={{ fontSize: "0.875rem" }}>{analise.explicacao}</p>

      {auditoria && (
        <>
          <hr className="sc-separador" />
          <CartaoAuditoria key={auditoria.id_auditoria} idAuditoria={auditoria.id_auditoria} />
        </>
      )}

      {bloqueio && (
        <>
          <hr className="sc-separador" />
          <h3 className="sc-painel__subtitulo">{TITULO_BLOQUEIO}</h3>
          <p style={{ fontSize: "0.875rem" }}>
            {BLOQUEIO_POR(bloqueio.por, formatarDiaHora(bloqueio.em))}
          </p>
          <p className="sc-apoio" style={{ marginTop: 4 }}>
            {bloqueio.motivo}
          </p>
        </>
      )}

      <hr className="sc-separador" />
      <h3 className="sc-painel__subtitulo">{TITULO_ASSOCIADO_FILIAL}</h3>
      {resposta_associado ? (
        <div className={`sc-aviso ${resposta_associado.resposta === "nao" ? "sc-aviso--bloqueio" : "sc-aviso--ok"}`}>
          {RESPOSTA_DO_ASSOCIADO(
            resposta_associado.resposta === "sim" ? RESPOSTA_SIM : RESPOSTA_NAO,
            formatarDiaHora(resposta_associado.em),
          )}{" "}
          <b>{LEITURA_RESPOSTA[resposta_associado.resposta]}</b>
        </div>
      ) : (
        <p className="sc-apoio">{SEM_RESPOSTA_ASSOCIADO}</p>
      )}
      <div className="sc-rotulo" style={{ marginTop: 12 }}>
        {HISTORICO_AGREGADO}
      </div>
      <p style={{ fontSize: "0.875rem", marginTop: 2 }}>
        {RESUMO_HISTORICO(
          formatarInteiro(associado.historico.compras_90d),
          formatarMoeda(associado.historico.valor_mediano),
          formatarInteiro(associado.historico.contestacoes),
        )}
      </p>
    </article>
  );
}
