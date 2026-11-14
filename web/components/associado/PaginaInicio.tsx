"use client";

/**
 * Início do app do associado (Issue #93): saldo, limite, cartões, atalhos, avisos pendentes
 * e as últimas compras. Tela 2 do protótipo.
 */

import Link from "next/link";
import { useRouter } from "next/navigation";
import { Chat, Growth, Receipt, ShoppingCart, Money } from "@carbon/react/icons";
import { obterInicio } from "@/lib/api";
import { sair } from "@/lib/sessao";
import { useCarregar } from "@/lib/useCarregar";
import ItemCompra from "@/components/associado/ItemCompra";
import EstadoErro from "@/components/comuns/EstadoErro";
import { formatarDiaHora, formatarMoeda, formatarTipo } from "@/lib/formatacao";
import {
  ALT_LOGO,
  ATALHO_CHAT,
  ATALHO_EM_BREVE,
  ATALHO_EXTRATO,
  ATALHO_INVESTIR,
  ATALHO_SIMULAR,
  CARREGANDO,
  CARTAO_BLOQUEADO,
  CARTAO_DESCRICAO,
  LIMITE_DE,
  LIMITE_DISPONIVEL,
  MEUS_CARTOES,
  OLA,
  PENDENTE_BOTAO,
  PENDENTE_DETALHE,
  PENDENTE_TITULO,
  ROTULO_ATALHOS,
  ROTULO_LIMITE,
  SAIR,
  SALDO_EM_CONTA,
  ULTIMAS_COMPRAS,
  VER_EXTRATO,
} from "@/lib/textos";

export default function PaginaInicio() {
  const router = useRouter();
  const { dados, erro, recarregar: carregar } = useCarregar(obterInicio);

  const usado = dados
    ? Math.round(((dados.limite_total - dados.limite_disponivel) / dados.limite_total) * 100)
    : 0;

  return (
    <>
      <header className="sc-topo-verde">
        <div className="sc-linha">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/logo-sicredi-branco.png" alt={ALT_LOGO} />
          <button
            type="button"
            className="sc-topo-verde__sair"
            onClick={() => {
              sair();
              router.replace("/entrar");
            }}
          >
            {SAIR}
          </button>
        </div>
        {dados && (
          <>
            <h1 className="sc-topo-verde__ola" style={{ color: "#fff" }}>
              {OLA(dados.associado.nome)}
            </h1>
            <small>{dados.associado.filial}</small>
          </>
        )}
      </header>

      {erro && <EstadoErro mensagem={erro} aoTentarNovamente={carregar} />}
      {!dados && !erro && <p className="sc-carregando">{CARREGANDO}</p>}

      {dados && (
        <>
          <section className="sc-cartao sc-sobe" aria-label={SALDO_EM_CONTA}>
            <div className="sc-rotulo">{SALDO_EM_CONTA}</div>
            <div className="sc-saldo sc-num">{formatarMoeda(dados.saldo)}</div>
            <div className="sc-rotulo">{LIMITE_DISPONIVEL}</div>
            <div>
              <b className="sc-num">{formatarMoeda(dados.limite_disponivel)}</b>{" "}
              <span className="sc-apoio sc-num">{LIMITE_DE(formatarMoeda(dados.limite_total))}</span>
            </div>
            <div
              className="sc-barra"
              role="img"
              aria-label={ROTULO_LIMITE(usado)}
            >
              <i style={{ width: `${100 - usado}%` }} />
            </div>
          </section>

          <nav className="sc-atalhos" aria-label={ROTULO_ATALHOS}>
            <Link href="/associado/comprar" className="sc-atalho sc-atalho--principal">
              <b aria-hidden="true"><ShoppingCart size={18} /></b>
              {ATALHO_SIMULAR}
            </Link>
            <Link href="/associado/extrato" className="sc-atalho">
              <b aria-hidden="true"><Receipt size={18} /></b>
              {ATALHO_EXTRATO}
            </Link>
            <Link href="/associado/chat" className="sc-atalho">
              <b aria-hidden="true"><Chat size={18} /></b>
              {ATALHO_CHAT}
            </Link>
            <button type="button" className="sc-atalho" disabled title={ATALHO_EM_BREVE}>
              <b aria-hidden="true"><Growth size={18} /></b>
              {ATALHO_INVESTIR}
            </button>
          </nav>

          {dados.pendentes.map((p) => (
            <div key={p.id_notificacao} className="sc-aviso sc-aviso--espera" role="status" style={{ marginBottom: 12 }}>
              <b>{PENDENTE_TITULO}</b>
              <br />
              {PENDENTE_DETALHE(formatarMoeda(p.valor), formatarDiaHora(p.data_hora))}
              <br />
              <Link
                href={`/associado/avisos/${p.id_notificacao}`}
                className="sc-botao sc-botao--pequeno"
                style={{ marginTop: 8 }}
              >
                {PENDENTE_BOTAO}
              </Link>
            </div>
          ))}

          <h2 className="sc-subtitulo">{MEUS_CARTOES}</h2>
          <ul className="sc-cartoes">
            {dados.cartoes.map((c) => (
              <li key={c.id} className="sc-cartao sc-cartao-pagamento">
                <Money size={20} aria-hidden="true" />
                <span>{CARTAO_DESCRICAO(formatarTipo(c.tipo), c.final)}</span>
                {c.bloqueado && <span className="sc-etiqueta sc-etiqueta--bloqueio">{CARTAO_BLOQUEADO}</span>}
              </li>
            ))}
          </ul>

          <div className="sc-linha">
            <h2 className="sc-subtitulo">{ULTIMAS_COMPRAS}</h2>
            <Link href="/associado/extrato" className="sc-link">
              {VER_EXTRATO}
            </Link>
          </div>
          <ul className="sc-cartao sc-lista-compras">
            {dados.ultimas_compras.map((c) => (
              <ItemCompra key={c.id_compra} compra={c} />
            ))}
          </ul>
        </>
      )}
    </>
  );
}
