"use client";

/**
 * Barra de progresso para exibir a nota de risco (0 a 100).
 * Mostra valor numérico e barra visual.
 */

import { formatarNota } from "@/lib/formatacao";

interface PropsBarraNota {
  nota: number;
}

export default function BarraNota({ nota }: PropsBarraNota) {
  const percentual = Math.min(100, Math.max(0, nota));
  const notaTexto = formatarNota(nota);

  return (
    <div
      role="meter"
      aria-valuenow={percentual}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={`Nota de risco: ${notaTexto} de 100`}
      style={{ width: "100%" }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          marginBottom: "4px",
          fontSize: "0.875rem",
        }}
      >
        <span>Nota de risco</span>
        <span>
          <strong>{notaTexto}</strong> de 100
        </span>
      </div>
      <div
        style={{
          height: "8px",
          backgroundColor: "#e0e0e0",
          borderRadius: "4px",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            height: "100%",
            width: `${percentual}%`,
            backgroundColor:
              percentual >= 80
                ? "#da1e28"
                : percentual >= 50
                  ? "#f1c21b"
                  : "#24a148",
            borderRadius: "4px",
            transition: "width 0.3s ease",
          }}
        />
      </div>
    </div>
  );
}
