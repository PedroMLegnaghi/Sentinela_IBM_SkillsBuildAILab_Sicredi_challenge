"use client";

/**
 * Lista de notificações do app do associado.
 * Busca todas as notificações, exibe mais recente primeiro.
 */

import { useEffect, useState } from "react";
import EstadoCarregando from "@/components/comuns/EstadoCarregando";
import EstadoErro from "@/components/comuns/EstadoErro";
import ItemNotificacao from "@/components/associado/ItemNotificacao";
import { obterNotificacoes } from "@/lib/api";
import { LEGENDA_APP_ASSOCIADO, SEM_NOTIFICACOES } from "@/lib/textos";
import type { Notificacao } from "@/lib/tipos";

export default function ListaNotificacoes() {
  const [itens, setItens] = useState<Notificacao[] | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [tentativa, setTentativa] = useState(0);

  useEffect(() => {
    let cancelado = false;
    obterNotificacoes()
      .then((resp) => !cancelado && setItens(resp.itens))
      .catch((e: Error) => !cancelado && setErro(e.message));
    return () => {
      cancelado = true;
    };
  }, [tentativa]);

  function atualizar(atualizada: Notificacao) {
    setItens((prev) =>
      prev
        ? prev.map((n) =>
            n.id_notificacao === atualizada.id_notificacao ? atualizada : n,
          )
        : prev,
    );
  }

  if (erro) {
    return (
      <EstadoErro
        mensagem={erro}
        aoTentarNovamente={() => {
          setErro(null);
          setTentativa((t) => t + 1);
        }}
      />
    );
  }

  if (!itens) return <EstadoCarregando />;

  return (
    <div>
      <p className="sentinela-legenda" style={{ marginBottom: "16px" }}>
        {LEGENDA_APP_ASSOCIADO}
      </p>
      {itens.length === 0 ? (
        <p>{SEM_NOTIFICACOES}</p>
      ) : (
        <div
          style={{ display: "flex", flexDirection: "column", gap: "12px" }}
        >
          {itens.map((n) => (
            <ItemNotificacao
              key={n.id_notificacao}
              notificacao={n}
              aoResponder={atualizar}
            />
          ))}
        </div>
      )}
    </div>
  );
}
