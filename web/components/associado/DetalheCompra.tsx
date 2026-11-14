"use client";

/**
 * Detalhe de uma compra do associado (Issue #93): valor, quando, cartão, situação, quem
 * bloqueou e por quê (motivo genérico), e a resposta do associado. Tela 6 do protótipo.
 * O botão "Não reconheço esta compra" entra na Issue #95 (prop `acoes`).
 */

import { useCarregar } from "@/lib/useCarregar";
import Link from "next/link";
import { ChevronLeft } from "@carbon/react/icons";
import { obterCompra } from "@/lib/api";
import type { DetalheCompra as Detalhe } from "@/lib/tipos";
import EtiquetaSituacao from "@/components/associado/EtiquetaSituacao";
import EstadoErro from "@/components/comuns/EstadoErro";
import { formatarDiaHora, formatarMoeda, formatarTipo } from "@/lib/formatacao";
import {
  CARREGANDO,
  CARTAO_DESCRICAO,
  COMPRA_SIMULADA,
  DETALHE_BLOQUEADA_POR,
  DETALHE_CARTAO,
  DETALHE_EM,
  DETALHE_MOTIVO,
  DETALHE_QUANDO,
  RESPOSTA_NAO,
  RESPOSTA_REGISTRADA,
  RESPOSTA_SIM,
  VALOR_NAO_COBRADO,
  VOLTAR,
} from "@/lib/textos";

interface PropsDetalhe {
  idCompra: string;
  acoes?: (compra: Detalhe, recarregar: () => void) => React.ReactNode;
}

export default function DetalheCompra({ idCompra, acoes }: PropsDetalhe) {
  const { dados: compra, erro, recarregar: carregar } = useCarregar(
    () => obterCompra(idCompra),
    idCompra,
  );

  const naoCobrada = compra && (compra.situacao === "BLOQUEADA" || compra.situacao === "CONTESTADA");

  return (
    <>
      <div className="sc-cabecalho-tela">
        <Link href="/associado/extrato" aria-label={VOLTAR}>
          <ChevronLeft size={24} aria-hidden="true" />
        </Link>
        <h1>{compra?.estabelecimento ?? ""}</h1>
      </div>

      {erro && <EstadoErro mensagem={erro} aoTentarNovamente={carregar} />}
      {!compra && !erro && <p className="sc-carregando">{CARREGANDO}</p>}

      {compra && (
        <>
          <section className="sc-cartao">
            <div className="sc-linha" style={{ justifyContent: "flex-start", gap: 6 }}>
              <EtiquetaSituacao situacao={compra.situacao} />
              {compra.simulada && <span className="sc-etiqueta sc-etiqueta--neutra">{COMPRA_SIMULADA}</span>}
            </div>
            <div className={`sc-saldo sc-num${naoCobrada ? " sc-riscado" : ""}`} style={{ color: "var(--sc-texto)" }}>
              {formatarMoeda(compra.valor)}
            </div>
            <dl className="sc-dados">
              <div className="sc-linha">
                <dt className="sc-rotulo">{DETALHE_QUANDO}</dt>
                <dd className="sc-num">{formatarDiaHora(compra.data_hora)}</dd>
              </div>
              <div className="sc-linha">
                <dt className="sc-rotulo">{DETALHE_CARTAO}</dt>
                <dd>{CARTAO_DESCRICAO(formatarTipo(compra.tipo_transacao), compra.final_cartao)}</dd>
              </div>
            </dl>
            {compra.bloqueio && (
              <>
                <hr className="sc-separador" />
                <dl className="sc-dados">
                  <div className="sc-linha">
                    <dt className="sc-rotulo">{DETALHE_BLOQUEADA_POR}</dt>
                    <dd>{compra.bloqueio.por}</dd>
                  </div>
                  <div className="sc-linha">
                    <dt className="sc-rotulo">{DETALHE_EM}</dt>
                    <dd className="sc-num">{formatarDiaHora(compra.bloqueio.em)}</dd>
                  </div>
                  <div>
                    <dt className="sc-rotulo">{DETALHE_MOTIVO}</dt>
                    <dd style={{ marginTop: 2 }}>{compra.bloqueio.motivo}</dd>
                  </div>
                </dl>
              </>
            )}
          </section>

          {compra.resposta_associado && (
            <div className="sc-aviso sc-aviso--ok" style={{ marginTop: 12 }}>
              {RESPOSTA_REGISTRADA(
                compra.resposta_associado.resposta === "sim" ? RESPOSTA_SIM : RESPOSTA_NAO,
                formatarDiaHora(compra.resposta_associado.em),
              )}
              {naoCobrada && <> {VALOR_NAO_COBRADO}</>}
            </div>
          )}

          {acoes?.(compra, carregar)}
        </>
      )}
    </>
  );
}
