"use client";

/**
 * Aviso "Foi você?" (Issue #95): a mensagem do Sicredi e os botões "Fui eu" e "Não fui eu".
 * Depois da resposta, volta ao detalhe da compra. Tela 5 do protótipo.
 */

import { useState } from "react";
import { useRouter } from "next/navigation";
import { obterCompra, obterNotificacao, responderNotificacao } from "@/lib/api";
import { useCarregar } from "@/lib/useCarregar";
import EstadoErro from "@/components/comuns/EstadoErro";
import { formatarDiaHora, formatarMoeda, formatarTipo } from "@/lib/formatacao";
import {
  AVISO_JA_RESPONDIDO,
  CARREGANDO,
  CARTAO_DESCRICAO,
  DETALHE_CARTAO,
  DETALHE_QUANDO,
  DETALHE_VALOR,
  ERRO_RESPOSTA_409,
  MENSAGEM_DO_SICREDI,
  RESPOSTA_NAO,
  RESPOSTA_SIM,
  RODAPE_SEGURANCA,
  TITULO_AVISO,
} from "@/lib/textos";

interface PropsConfirmar {
  idNotificacao: string;
  idCompra?: string;
}

export default function ConfirmarCompra({ idNotificacao, idCompra }: PropsConfirmar) {
  const router = useRouter();
  const aviso = useCarregar(() => obterNotificacao(idNotificacao), idNotificacao);
  const compra = useCarregar(
    () => (idCompra ? obterCompra(idCompra) : Promise.resolve(null)),
    idCompra ?? "",
  );
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);

  async function responder(resposta: "sim" | "nao") {
    setEnviando(true);
    setErro(null);
    try {
      await responderNotificacao(idNotificacao, { resposta });
      router.push(idCompra ? `/associado/compras/${idCompra}` : "/associado/extrato");
    } catch (e) {
      const mensagem = (e as Error).message;
      setErro(mensagem.includes("(409)") ? ERRO_RESPOSTA_409 : mensagem);
      setEnviando(false);
    }
  }

  const notificacao = aviso.dados;
  const detalhe = compra.dados;

  return (
    <>
      <div className="sc-cabecalho-tela">
        <h1>{TITULO_AVISO}</h1>
      </div>

      {aviso.erro && <EstadoErro mensagem={aviso.erro} aoTentarNovamente={aviso.recarregar} />}
      {!notificacao && !aviso.erro && <p className="sc-carregando">{CARREGANDO}</p>}

      {notificacao && (
        <>
          <section className="sc-cartao">
            <div className="sc-rotulo">{MENSAGEM_DO_SICREDI}</div>
            <p style={{ margin: "6px 0 0", fontWeight: 700 }}>{notificacao.mensagem}</p>
            {detalhe && (
              <>
                <hr className="sc-separador" />
                <dl className="sc-dados">
                  <div className="sc-linha">
                    <dt className="sc-rotulo">{DETALHE_VALOR}</dt>
                    <dd className="sc-num">{formatarMoeda(detalhe.valor)}</dd>
                  </div>
                  <div className="sc-linha">
                    <dt className="sc-rotulo">{DETALHE_QUANDO}</dt>
                    <dd className="sc-num">{formatarDiaHora(detalhe.data_hora)}</dd>
                  </div>
                  <div className="sc-linha">
                    <dt className="sc-rotulo">{DETALHE_CARTAO}</dt>
                    <dd>{CARTAO_DESCRICAO(formatarTipo(detalhe.tipo_transacao), detalhe.final_cartao)}</dd>
                  </div>
                </dl>
              </>
            )}
          </section>

          {notificacao.status === "aguardando" ? (
            <div style={{ display: "grid", gap: 10, marginTop: 16 }}>
              <button type="button" className="sc-botao" disabled={enviando} onClick={() => responder("sim")}>
                {RESPOSTA_SIM}
              </button>
              <button
                type="button"
                className="sc-botao sc-botao--perigo"
                disabled={enviando}
                onClick={() => responder("nao")}
              >
                {RESPOSTA_NAO}
              </button>
            </div>
          ) : (
            <div className="sc-aviso sc-aviso--ok" style={{ marginTop: 16 }}>
              {AVISO_JA_RESPONDIDO} {notificacao.resultado}
            </div>
          )}

          {erro && (
            <div className="sc-aviso sc-aviso--bloqueio" role="alert" style={{ marginTop: 12 }}>
              {erro}
            </div>
          )}
          <p className="sc-apoio" style={{ marginTop: 14 }}>
            {RODAPE_SEGURANCA}
          </p>
        </>
      )}
    </>
  );
}
