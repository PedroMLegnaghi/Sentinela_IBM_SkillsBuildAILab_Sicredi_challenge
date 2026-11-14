"use client";

/**
 * Card de uma notificação no app do associado.
 * Mostra mensagem, hora, status, origem da mensagem e botões de resposta quando aguardando.
 */

import { useEffect, useRef, useState } from "react";
import { Button, InlineNotification, Tag, Tile } from "@carbon/react";
import { obterNotificacao, responderNotificacao } from "@/lib/api";
import { formatarDataHora } from "@/lib/formatacao";
import {
  BOTAO_NAO_FUI_EU,
  BOTAO_SIM_FUI_EU,
  CRIADA_EM,
  ERRO_RESPOSTA_409,
  ETIQUETA_MENSAGEM_PADRAO,
  ETIQUETA_REDIGIDA_GRANITE,
  RESPONDIDA_EM,
  ROTULOS_STATUS_NOTIFICACAO,
  ROTULOS_TIPO_NOTIFICACAO,
} from "@/lib/textos";
import type { Notificacao } from "@/lib/tipos";

interface PropsItemNotificacao {
  notificacao: Notificacao;
  aoResponder: (atualizada: Notificacao) => void;
}

function corStatus(status: string): "green" | "red" | "gray" {
  if (status === "confirmada") return "green";
  if (status === "negada") return "red";
  return "gray";
}

const INTERVALO_POLLING_MS = 5_000;
const TEMPO_MAXIMO_POLLING_MS = 30_000;

export default function ItemNotificacao({
  notificacao,
  aoResponder,
}: PropsItemNotificacao) {
  const [respondendo, setRespondendo] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const tempoDecorrido = useRef(0);

  // Enquanto o aviso está aguardando com mensagem do modelo fixo, busca atualizações
  // a cada 5 segundos por até 30 segundos, para capturar quando o Granite substituir.
  useEffect(() => {
    const devePollar =
      notificacao.status === "aguardando" &&
      notificacao.fonte_mensagem === "modelo";
    if (!devePollar) return;

    tempoDecorrido.current = 0;
    const intervalo = setInterval(async () => {
      tempoDecorrido.current += INTERVALO_POLLING_MS;
      if (tempoDecorrido.current >= TEMPO_MAXIMO_POLLING_MS) {
        clearInterval(intervalo);
        return;
      }
      try {
        const atualizada = await obterNotificacao(notificacao.id_notificacao);
        if (atualizada.fonte_mensagem === "watsonx") {
          clearInterval(intervalo);
          aoResponder(atualizada);
        }
      } catch {
        // falha silenciosa: a etiqueta continua como "Mensagem padrão"
      }
    }, INTERVALO_POLLING_MS);

    return () => clearInterval(intervalo);
  }, [notificacao.id_notificacao, notificacao.status, notificacao.fonte_mensagem, aoResponder]);

  async function responder(resposta: "sim" | "nao") {
    setRespondendo(true);
    setErro(null);
    try {
      const atualizada = await responderNotificacao(
        notificacao.id_notificacao,
        { resposta },
      );
      aoResponder(atualizada);
    } catch (e) {
      const msg = (e as Error).message;
      if (msg.includes("409")) {
        setErro(ERRO_RESPOSTA_409);
      } else {
        setErro(msg);
      }
    } finally {
      setRespondendo(false);
    }
  }

  const textoEtiquetaFonte =
    notificacao.fonte_mensagem === "watsonx"
      ? ETIQUETA_REDIGIDA_GRANITE
      : ETIQUETA_MENSAGEM_PADRAO;

  return (
    <Tile className="sentinela-bloco">
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          gap: "8px",
          flexWrap: "wrap",
        }}
      >
        <span style={{ fontSize: "0.75rem", color: "#525252" }}>
          {ROTULOS_TIPO_NOTIFICACAO[notificacao.tipo] ??
            notificacao.tipo}
        </span>
        <Tag type={corStatus(notificacao.status)}>
          {ROTULOS_STATUS_NOTIFICACAO[notificacao.status] ??
            notificacao.status}
        </Tag>
      </div>
      <p style={{ margin: "8px 0" }}>{notificacao.mensagem}</p>
      <Tag size="sm" type="blue" style={{ marginBottom: "4px" }}>
        {textoEtiquetaFonte}
      </Tag>
      <p
        style={{
          fontSize: "0.75rem",
          color: "#525252",
          margin: "4px 0",
        }}
      >
        {CRIADA_EM(formatarDataHora(notificacao.criada_em))}
      </p>
      {notificacao.respondida_em && (
        <p style={{ fontSize: "0.75rem", color: "#525252", margin: "4px 0" }}>
          {RESPONDIDA_EM(formatarDataHora(notificacao.respondida_em))}
        </p>
      )}
      {notificacao.resultado && (
        <p style={{ marginTop: "8px", fontWeight: 600 }}>
          {notificacao.resultado}
        </p>
      )}
      {erro && (
        <InlineNotification
          kind="error"
          title={erro}
          lowContrast
          style={{ marginTop: "8px" }}
        />
      )}
      {notificacao.status === "aguardando" && (
        <div
          style={{
            display: "flex",
            gap: "8px",
            marginTop: "16px",
            flexWrap: "wrap",
          }}
        >
          <Button
            size="sm"
            kind="primary"
            onClick={() => responder("sim")}
            disabled={respondendo}
          >
            {BOTAO_SIM_FUI_EU}
          </Button>
          <Button
            size="sm"
            kind="secondary"
            onClick={() => responder("nao")}
            disabled={respondendo}
          >
            {BOTAO_NAO_FUI_EU}
          </Button>
        </div>
      )}
    </Tile>
  );
}
