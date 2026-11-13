"use client";

/**
 * Estado de erro: exibe mensagem de erro e botão opcional para tentar de novo.
 */

import { InlineNotification, Button } from "@carbon/react";
import { ERRO_API, TENTAR_NOVAMENTE } from "@/lib/textos";

interface PropsEstadoErro {
  mensagem?: string;
  aoTentarNovamente?: () => void;
}

export default function EstadoErro({
  mensagem = ERRO_API,
  aoTentarNovamente,
}: PropsEstadoErro) {
  return (
    <div role="alert" style={{ padding: "16px 0" }}>
      <InlineNotification
        kind="error"
        title="Erro"
        subtitle={mensagem}
        hideCloseButton
      />
      {aoTentarNovamente && (
        <Button
          kind="ghost"
          size="sm"
          onClick={aoTentarNovamente}
          style={{ marginTop: "8px" }}
        >
          {TENTAR_NOVAMENTE}
        </Button>
      )}
    </div>
  );
}
