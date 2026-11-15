"use client";

/**
 * "Não reconheço esta compra" (Issue #95): pede confirmação antes de contestar, porque a
 * contestação bloqueia o cartão e avisa a agência.
 */

import { useState } from "react";
import { contestarCompra } from "@/lib/api";
import {
  CANCELAR,
  CONTESTADA_OK,
  CONTESTAR,
  CONTESTAR_CONFIRMAR,
  CONTESTAR_EXPLICACAO,
} from "@/lib/textos";

interface PropsBotaoContestar {
  idCompra: string;
  aoContestar: () => void;
}

export default function BotaoContestar({ idCompra, aoContestar }: PropsBotaoContestar) {
  const [confirmando, setConfirmando] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const [feito, setFeito] = useState(false);

  async function contestar() {
    setEnviando(true);
    setErro(null);
    try {
      await contestarCompra(idCompra);
      setFeito(true);
      aoContestar();
    } catch (e) {
      setErro((e as Error).message);
    } finally {
      setEnviando(false);
    }
  }

  if (feito) {
    return (
      <div className="sc-aviso sc-aviso--ok" role="status" style={{ marginTop: 16 }}>
        {CONTESTADA_OK}
      </div>
    );
  }

  return (
    <div style={{ marginTop: 16 }}>
      {!confirmando ? (
        <>
          <button type="button" className="sc-botao sc-botao--perigo" onClick={() => setConfirmando(true)}>
            {CONTESTAR}
          </button>
          <p className="sc-apoio" style={{ marginTop: 8 }}>
            {CONTESTAR_EXPLICACAO}
          </p>
        </>
      ) : (
        <div className="sc-aviso sc-aviso--bloqueio" role="alertdialog" aria-label={CONTESTAR}>
          <p style={{ marginBottom: 10 }}>{CONTESTAR_EXPLICACAO}</p>
          <div style={{ display: "grid", gap: 8 }}>
            <button type="button" className="sc-botao sc-botao--perigo" disabled={enviando} onClick={contestar}>
              {CONTESTAR_CONFIRMAR}
            </button>
            <button type="button" className="sc-botao sc-botao--secundario" onClick={() => setConfirmando(false)}>
              {CANCELAR}
            </button>
          </div>
          {erro && <p role="alert" style={{ marginTop: 8 }}>{erro}</p>}
        </div>
      )}
    </div>
  );
}
