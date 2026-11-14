/**
 * Página /associado — simulação do app do associado.
 * Moldura de celular com a lista de notificações.
 */

import { Heading } from "@carbon/react";
import ListaNotificacoes from "@/components/associado/ListaNotificacoes";
import { TITULO_APP_ASSOCIADO } from "@/lib/textos";

export const metadata = {
  title: "App do associado — Sentinela",
};

export default function PaginaAssociado() {
  return (
    <div className="sentinela-pagina">
      <Heading>{TITULO_APP_ASSOCIADO}</Heading>
      {/* Moldura de celular */}
      <div
        style={{
          maxWidth: "390px",
          margin: "24px auto 0",
          border: "12px solid #161616",
          borderRadius: "36px",
          padding: "24px 16px",
          backgroundColor: "#f4f4f4",
          minHeight: "600px",
          boxShadow: "0 4px 24px rgba(0,0,0,0.18)",
        }}
        aria-label="Simulação de celular do associado"
      >
        {/* Barra de status simulada */}
        <div
          style={{
            textAlign: "center",
            fontSize: "0.7rem",
            color: "#525252",
            marginBottom: "12px",
          }}
          aria-hidden="true"
        >
          Sicredi · App
        </div>
        <ListaNotificacoes />
      </div>
    </div>
  );
}
