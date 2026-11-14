"use client";

/**
 * Painel da transação selecionada: decisão do modelo na hora e, ao lado, a auditoria da IA.
 */

import { useEffect, useState } from "react";
import { Tile } from "@carbon/react";
import BarraNota from "@/components/comuns/BarraNota";
import EstadoCarregando from "@/components/comuns/EstadoCarregando";
import EstadoErro from "@/components/comuns/EstadoErro";
import FaixaDecisao from "@/components/comuns/FaixaDecisao";
import CartaoAssociado from "@/components/associado/CartaoAssociado";
import CartaoAuditoria from "@/components/painel/CartaoAuditoria";
import GraficoContribuicoes from "@/components/painel/GraficoContribuicoes";
import HistoricoCartao from "@/components/painel/HistoricoCartao";
import RespostaAnalista from "@/components/painel/RespostaAnalista";
import { obterTransacao } from "@/lib/api";
import {
  formatarDataHora,
  formatarDecimal,
  formatarModalidade,
  formatarMoeda,
  formatarTipo,
} from "@/lib/formatacao";
import {
  LEGENDA_LATENCIA,
  SEM_SINAIS,
  TITULO_DECISAO_MODELO,
  TITULO_EXPLICACAO,
  TITULO_PAINEL,
  TITULO_SINAIS,
} from "@/lib/textos";
import type { RespostaTransacao } from "@/lib/tipos";

type Estado =
  | { tipo: "carregando" }
  | { tipo: "pronto"; dados: RespostaTransacao }
  | { tipo: "erro"; mensagem: string };

interface PropsPainelTransacao {
  idTransacao: number;
}

export default function PainelTransacao({ idTransacao }: PropsPainelTransacao) {
  const [estado, setEstado] = useState<Estado>({ tipo: "carregando" });
  const [tentativa, setTentativa] = useState(0);

  useEffect(() => {
    let cancelado = false;
    obterTransacao(idTransacao)
      .then((dados) => !cancelado && setEstado({ tipo: "pronto", dados }))
      .catch(
        (erro: Error) =>
          !cancelado && setEstado({ tipo: "erro", mensagem: erro.message }),
      );
    return () => {
      cancelado = true;
    };
  }, [idTransacao, tentativa]);

  if (estado.tipo === "carregando") return <EstadoCarregando />;
  if (estado.tipo === "erro") {
    const tentarDeNovo = () => {
      setEstado({ tipo: "carregando" });
      setTentativa((t) => t + 1);
    };
    return (
      <EstadoErro mensagem={estado.mensagem} aoTentarNovamente={tentarDeNovo} />
    );
  }

  const { transacao, analise, historico, resposta_analista, notificacao } =
    estado.dados;
  const resumo = [
    formatarDataHora(transacao.data_hora),
    formatarTipo(transacao.tipo_transacao),
    formatarModalidade(transacao.modalidade_transacao),
    formatarMoeda(transacao.valor),
  ].join(" · ");

  return (
    <div className="sentinela-painel">
      <header>
        <h2 className="sentinela-titulo-painel">
          {TITULO_PAINEL(transacao.id_transacao)}
        </h2>
        <p className="sentinela-legenda">{resumo}</p>
      </header>
      <Tile className="sentinela-bloco">
        <h3 className="sentinela-subtitulo">{TITULO_DECISAO_MODELO}</h3>
        <FaixaDecisao
          decisao={analise.decisao}
          decisaoLegivel={analise.decisao_legivel}
        />
        <BarraNota nota={analise.nota} />
        <p className="sentinela-legenda">
          {LEGENDA_LATENCIA(formatarDecimal(analise.latencia_ms, 1))}
        </p>
        <h3 className="sentinela-subtitulo">
          {TITULO_SINAIS(analise.sinais.length)}
        </h3>
        {analise.sinais.length === 0 ? (
          <p>{SEM_SINAIS}</p>
        ) : (
          <ul className="sentinela-lista">
            {analise.sinais.map((sinal) => (
              <li key={sinal.id}>{sinal.descricao}</li>
            ))}
          </ul>
        )}
        <GraficoContribuicoes contribuicoes={analise.contribuicoes} />
        <h3 className="sentinela-subtitulo">{TITULO_EXPLICACAO}</h3>
        <p>{analise.explicacao}</p>
      </Tile>
      <CartaoAssociado
        idTransacao={transacao.id_transacao}
        decisao={analise.decisao}
        notificacaoInicial={notificacao ?? null}
      />
      <CartaoAuditoria idTransacao={transacao.id_transacao} />
      <RespostaAnalista
        key={transacao.id_transacao}
        idTransacao={transacao.id_transacao}
        respostaInicial={resposta_analista}
      />
      <HistoricoCartao historico={historico} />
    </div>
  );
}
