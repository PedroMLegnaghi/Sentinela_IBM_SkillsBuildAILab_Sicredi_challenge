"use client";

/**
 * Estado de carregamento: exibe spinner de texto enquanto dados são buscados.
 */

import { Loading } from "@carbon/react";
import { CARREGANDO } from "@/lib/textos";

interface PropsEstadoCarregando {
  mensagem?: string;
}

export default function EstadoCarregando({
  mensagem = CARREGANDO,
}: PropsEstadoCarregando) {
  return (
    <div
      role="status"
      aria-live="polite"
      aria-label={mensagem}
      style={{
        display: "flex",
        alignItems: "center",
        gap: "12px",
        padding: "32px 0",
      }}
    >
      <Loading small withOverlay={false} description={mensagem} />
      <span>{mensagem}</span>
    </div>
  );
}
