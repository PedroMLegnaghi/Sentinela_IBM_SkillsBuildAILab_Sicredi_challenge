"use client";

/**
 * Botões de resposta do analista, de mesmo peso visual, e a resposta atual (vale a última).
 */

import { useState } from "react";
import { Button, InlineNotification } from "@carbon/react";
import { registrarResposta } from "@/lib/api";
import { formatarDataHora, formatarResposta } from "@/lib/formatacao";
import {
  BOTAO_FRAUDE,
  BOTAO_LEGITIMA,
  ERRO_GRAVAR,
  RESPOSTA_ATUAL,
  SEM_RESPOSTA,
  TITULO_RESPOSTA,
} from "@/lib/textos";
import type { Resposta } from "@/lib/tipos";

interface PropsRespostaAnalista {
  idTransacao: number;
  respostaInicial: Resposta | null;
}

export default function RespostaAnalista({
  idTransacao,
  respostaInicial,
}: PropsRespostaAnalista) {
  const [resposta, setResposta] = useState<Resposta | null>(respostaInicial);
  const [gravando, setGravando] = useState(false);
  const [erro, setErro] = useState(false);

  async function responder(valor: "fraude" | "legitima") {
    setGravando(true);
    setErro(false);
    try {
      setResposta(
        await registrarResposta({ id_transacao: idTransacao, resposta: valor }),
      );
    } catch {
      setErro(true);
    } finally {
      setGravando(false);
    }
  }

  return (
    <section aria-labelledby="titulo-resposta" className="sentinela-bloco">
      <h3 id="titulo-resposta" className="sentinela-subtitulo">
        {TITULO_RESPOSTA}
      </h3>
      <div className="sentinela-botoes">
        <Button
          kind="tertiary"
          size="md"
          disabled={gravando}
          onClick={() => responder("fraude")}
        >
          {BOTAO_FRAUDE}
        </Button>
        <Button
          kind="tertiary"
          size="md"
          disabled={gravando}
          onClick={() => responder("legitima")}
        >
          {BOTAO_LEGITIMA}
        </Button>
      </div>
      {erro && (
        <InlineNotification
          kind="error"
          title=""
          subtitle={ERRO_GRAVAR}
          hideCloseButton
        />
      )}
      <p className="sentinela-legenda" role="status">
        {resposta
          ? RESPOSTA_ATUAL(
              formatarResposta(resposta.resposta),
              formatarDataHora(resposta.registrado_em),
            )
          : SEM_RESPOSTA}
      </p>
    </section>
  );
}
