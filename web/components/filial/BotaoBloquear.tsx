"use client";

/**
 * "Bloquear compra" do auditor (Issue #103): só para compra que aguarda o associado.
 * Pede confirmação e uma nota opcional; o nome do auditor fica registrado, mas o associado
 * vê apenas "Analista da agência".
 */

import { useState } from "react";
import { bloquearCompra } from "@/lib/api";
import type { RespostaCompraFilial } from "@/lib/tipos";
import {
  BLOQUEANDO,
  BLOQUEAR_AVISO_ASSOCIADO,
  BLOQUEAR_COMPRA,
  BLOQUEAR_EXPLICACAO,
  CANCELAR,
  CONFIRMAR_BLOQUEIO,
  ERRO_BLOQUEIO_409,
  LIBERACAO_AUTOMATICA,
  NOTA_DO_AUDITOR,
} from "@/lib/textos";

export const LIMITE_NOTA = 300;

interface PropsBotaoBloquear {
  idCompra: string;
  aoBloquear: (atualizada: RespostaCompraFilial) => void;
}

export default function BotaoBloquear({ idCompra, aoBloquear }: PropsBotaoBloquear) {
  const [aberto, setAberto] = useState(false);
  const [nota, setNota] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);

  async function bloquear() {
    setEnviando(true);
    setErro(null);
    try {
      aoBloquear(await bloquearCompra(idCompra, nota.trim() || null));
    } catch (e) {
      const mensagem = (e as Error).message;
      setErro(mensagem.includes("(409)") ? ERRO_BLOQUEIO_409 : mensagem);
      setEnviando(false);
    }
  }

  if (!aberto) {
    return (
      <div className="sc-acao-auditor">
        <button type="button" className="sc-botao sc-botao--pequeno" onClick={() => setAberto(true)}>
          {BLOQUEAR_COMPRA}
        </button>
        <p className="sc-apoio">{BLOQUEAR_EXPLICACAO}</p>
      </div>
    );
  }

  return (
    <div className="sc-aviso sc-aviso--espera sc-acao-auditor" role="alertdialog" aria-label={BLOQUEAR_COMPRA}>
      <p>{BLOQUEAR_AVISO_ASSOCIADO}</p>
      <p style={{ marginTop: 4 }}>{LIBERACAO_AUTOMATICA}</p>
      <label className="sc-campo" style={{ marginTop: 10 }}>
        <span>{NOTA_DO_AUDITOR}</span>
        <textarea
          rows={3}
          maxLength={LIMITE_NOTA}
          value={nota}
          onChange={(e) => setNota(e.target.value)}
        />
      </label>
      <div className="sc-linha" style={{ justifyContent: "flex-start", marginTop: 10 }}>
        <button type="button" className="sc-botao sc-botao--pequeno" disabled={enviando} onClick={bloquear}>
          {enviando ? BLOQUEANDO : CONFIRMAR_BLOQUEIO}
        </button>
        <button
          type="button"
          className="sc-botao sc-botao--pequeno sc-botao--secundario"
          disabled={enviando}
          onClick={() => setAberto(false)}
        >
          {CANCELAR}
        </button>
      </div>
      {erro && (
        <p role="alert" style={{ marginTop: 8 }}>
          {erro}
        </p>
      )}
    </div>
  );
}
