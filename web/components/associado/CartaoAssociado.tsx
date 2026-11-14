"use client";

/**
 * Bloco "Associado" no painel da transação.
 * Mostra o status da notificação e, quando não houver, o botão "Avisar o associado"
 * (apenas quando a decisão não for APROVAR).
 */

import { useState } from "react";
import { Button, InlineNotification, Tag, Tile } from "@carbon/react";
import { notificarAssociado } from "@/lib/api";
import { formatarDataHora } from "@/lib/formatacao";
import {
  AVISO_ASSOCIADO_ENVIADO,
  BOTAO_AVISAR_ASSOCIADO,
  ERRO_NOTIFICACAO_409,
  ERRO_NOTIFICACAO_422,
  RESPONDIDA_EM,
  ROTULOS_STATUS_NOTIFICACAO,
  TITULO_BLOCO_ASSOCIADO,
} from "@/lib/textos";
import type { Decisao, Notificacao } from "@/lib/tipos";

function corStatus(status: string): "green" | "red" | "gray" {
  if (status === "confirmada") return "green";
  if (status === "negada") return "red";
  return "gray";
}

interface PropsCartaoAssociado {
  idTransacao: number;
  decisao: Decisao;
  notificacaoInicial: Notificacao | null;
}

export default function CartaoAssociado({
  idTransacao,
  decisao,
  notificacaoInicial,
}: PropsCartaoAssociado) {
  const [notificacao, setNotificacao] = useState<Notificacao | null>(
    notificacaoInicial,
  );
  const [avisando, setAvisando] = useState(false);
  const [sucesso, setSucesso] = useState(false);
  const [erro, setErro] = useState<string | null>(null);

  if (decisao === "APROVAR") return null;

  async function avisar() {
    setAvisando(true);
    setErro(null);
    setSucesso(false);
    try {
      const nova = await notificarAssociado(idTransacao);
      setNotificacao(nova);
      setSucesso(true);
    } catch (e) {
      const msg = (e as Error).message;
      if (msg.includes("409")) {
        setErro(ERRO_NOTIFICACAO_409);
      } else if (msg.includes("422")) {
        setErro(ERRO_NOTIFICACAO_422);
      } else {
        setErro(msg);
      }
    } finally {
      setAvisando(false);
    }
  }

  return (
    <Tile className="sentinela-bloco">
      <h3 className="sentinela-subtitulo">{TITULO_BLOCO_ASSOCIADO}</h3>
      {notificacao ? (
        <>
          <Tag type={corStatus(notificacao.status)}>
            {ROTULOS_STATUS_NOTIFICACAO[notificacao.status] ??
              notificacao.status}
          </Tag>
          {notificacao.resultado && (
            <p style={{ marginTop: "8px" }}>{notificacao.resultado}</p>
          )}
          {notificacao.respondida_em && (
            <p style={{ fontSize: "0.75rem", color: "#525252", marginTop: "4px" }}>
              {RESPONDIDA_EM(formatarDataHora(notificacao.respondida_em))}
            </p>
          )}
        </>
      ) : (
        <>
          {sucesso && (
            <InlineNotification
              kind="success"
              title={AVISO_ASSOCIADO_ENVIADO}
              lowContrast
              style={{ marginBottom: "8px" }}
            />
          )}
          {erro && (
            <InlineNotification
              kind="error"
              title={erro}
              lowContrast
              style={{ marginBottom: "8px" }}
            />
          )}
          <Button
            size="sm"
            kind="secondary"
            onClick={avisar}
            disabled={avisando}
          >
            {BOTAO_AVISAR_ASSOCIADO}
          </Button>
        </>
      )}
    </Tile>
  );
}
