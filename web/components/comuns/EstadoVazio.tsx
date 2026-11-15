"use client";

/**
 * Estado vazio: exibe mensagem quando não há itens para mostrar.
 */

import { VAZIO_PADRAO } from "@/lib/textos";

interface PropsEstadoVazio {
  mensagem?: string;
}

export default function EstadoVazio({
  mensagem = VAZIO_PADRAO,
}: PropsEstadoVazio) {
  return (
    <div
      role="status"
      aria-live="polite"
      style={{
        padding: "32px",
        textAlign: "center",
        color: "#525252",
      }}
    >
      <p>{mensagem}</p>
    </div>
  );
}
