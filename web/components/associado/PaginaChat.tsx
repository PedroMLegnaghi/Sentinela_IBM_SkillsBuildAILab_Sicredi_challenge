"use client";

/**
 * Chat do associado (Issue #106; ESPECIFICACAO, seção 17.6). A IA só informa sobre os gastos e
 * as compras do próprio associado. "Conversar com gerente" continua na mesma conversa, com o
 * resumo da sessão como primeira mensagem do gerente (simulado). A conversa não é guardada.
 */

import { useEffect, useRef, useState } from "react";
import { chamarGerente, perguntarAoChat } from "@/lib/api";
import type { MensagemChat } from "@/lib/tipos";
import {
  ASSISTENTE,
  AVISO_GERENTE_SIMULADO,
  BOAS_VINDAS_CHAT,
  CAMPO_CHAT,
  CHAMANDO_GERENTE,
  CONVERSAR_COM_GERENTE,
  DIGITANDO,
  ENVIAR,
  ERRO_CHAT,
  FONTE_CHAT,
  GERENTE_DA_AGENCIA,
  ROTULO_CONVERSA,
  ROTULO_SUGESTOES,
  SUBTITULO_CHAT,
  SUGESTOES_CHAT,
  TITULO_CHAT,
  VOCE,
} from "@/lib/textos";

/** Mensagem na tela: a do contrato mais quem falou e a fonte. */
export interface MensagemTela {
  autor: "associado" | "ia" | "gerente";
  texto: string;
  fonte?: string;
}

/** Limite de itens do histórico enviado à API (ESPECIFICACAO, 17.6). */
export const LIMITE_HISTORICO = 20;

/** Histórico no formato do contrato: só associado e IA, os 20 mais recentes. */
export function historicoParaApi(mensagens: MensagemTela[]): MensagemChat[] {
  return mensagens
    .filter((m): m is MensagemTela & { autor: "associado" | "ia" } => m.autor !== "gerente")
    .map(({ autor, texto }) => ({ autor, texto }))
    .slice(-LIMITE_HISTORICO);
}

export default function PaginaChat() {
  const [mensagens, setMensagens] = useState<MensagemTela[]>([]);
  const [texto, setTexto] = useState("");
  const [esperando, setEsperando] = useState<"ia" | "gerente" | null>(null);
  const [gerente, setGerente] = useState<string | null>(null);
  const fim = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fim.current?.scrollIntoView?.({ block: "end" });
  }, [mensagens, esperando]);

  async function perguntar(pergunta: string) {
    const limpa = pergunta.trim();
    if (!limpa || esperando || gerente) return;
    const historico = historicoParaApi(mensagens);
    setMensagens((m) => [...m, { autor: "associado", texto: limpa }]);
    setTexto("");
    setEsperando("ia");
    try {
      const r = await perguntarAoChat({ mensagem: limpa.slice(0, 500), historico });
      setMensagens((m) => [...m, { autor: "ia", texto: r.resposta, fonte: r.fonte }]);
    } catch {
      setMensagens((m) => [...m, { autor: "ia", texto: ERRO_CHAT }]);
    } finally {
      setEsperando(null);
    }
  }

  async function falarComGerente() {
    setEsperando("gerente");
    try {
      const r = await chamarGerente(historicoParaApi(mensagens));
      setGerente(r.gerente.nome);
      setMensagens((m) => [...m, { autor: "gerente", texto: r.resumo, fonte: "gerente" }]);
    } catch {
      setMensagens((m) => [...m, { autor: "ia", texto: ERRO_CHAT }]);
    } finally {
      setEsperando(null);
    }
  }

  const nomeDoAutor = (m: MensagemTela) =>
    m.autor === "associado" ? VOCE : m.autor === "gerente" ? gerente ?? "" : ASSISTENTE;

  return (
    <div className="sc-chat">
      <div className="sc-cabecalho-tela" style={{ flexDirection: "column", alignItems: "flex-start", gap: 2 }}>
        <h1>{gerente ? GERENTE_DA_AGENCIA(gerente) : TITULO_CHAT}</h1>
        <span className="sc-apoio">{gerente ? AVISO_GERENTE_SIMULADO : SUBTITULO_CHAT}</span>
      </div>

      <div className="sc-chat__conversa" role="log" aria-label={ROTULO_CONVERSA} aria-live="polite">
        <div className="sc-balao sc-balao--ia">
          <b>{ASSISTENTE}</b>
          {BOAS_VINDAS_CHAT}
        </div>
        {mensagens.map((m, i) => (
          <div key={i} className={`sc-balao sc-balao--${m.autor}`}>
            <b>{nomeDoAutor(m)}</b>
            {m.texto}
            {m.fonte && <small>{FONTE_CHAT[m.fonte] ?? m.fonte}</small>}
          </div>
        ))}
        {esperando && (
          <div className="sc-balao sc-balao--ia sc-balao--digitando" aria-busy="true">
            {esperando === "gerente" ? CHAMANDO_GERENTE : DIGITANDO}
          </div>
        )}
        <div ref={fim} />
      </div>

      {!gerente && (
        <>
          {mensagens.length === 0 && (
            <div className="sc-chips" role="group" aria-label={ROTULO_SUGESTOES} style={{ margin: "10px 0" }}>
              {SUGESTOES_CHAT.map((s) => (
                <button key={s} type="button" className="sc-chip" onClick={() => perguntar(s)}>
                  {s}
                </button>
              ))}
            </div>
          )}
          <form
            className="sc-chat__campo"
            onSubmit={(e) => {
              e.preventDefault();
              perguntar(texto);
            }}
          >
            <label className="sc-oculto" htmlFor="campo-chat">
              {CAMPO_CHAT}
            </label>
            <input
              id="campo-chat"
              value={texto}
              maxLength={500}
              placeholder={CAMPO_CHAT}
              onChange={(e) => setTexto(e.target.value)}
              disabled={esperando !== null}
            />
            <button type="submit" className="sc-botao sc-botao--pequeno" disabled={!texto.trim() || esperando !== null}>
              {ENVIAR}
            </button>
          </form>
          <button
            type="button"
            className="sc-botao sc-botao--secundario"
            style={{ marginTop: 10 }}
            disabled={esperando !== null}
            onClick={falarComGerente}
          >
            {CONVERSAR_COM_GERENTE}
          </button>
        </>
      )}
    </div>
  );
}
