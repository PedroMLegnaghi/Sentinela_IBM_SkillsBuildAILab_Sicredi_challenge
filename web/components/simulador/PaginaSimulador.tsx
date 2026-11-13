"use client";

/**
 * Página "Simulador": escolhe uma transação da fila (os alertas e algumas aprovadas) e
 * simula mudanças nela.
 */

import { useEffect, useState } from "react";
import { Heading, Select, SelectItem } from "@carbon/react";
import EstadoCarregando from "@/components/comuns/EstadoCarregando";
import EstadoErro from "@/components/comuns/EstadoErro";
import SimuladorTransacao from "@/components/simulador/SimuladorTransacao";
import { obterFila } from "@/lib/api";
import { formatarNota } from "@/lib/formatacao";
import {
  ESCOLHA_TRANSACAO,
  LEGENDA_SIMULADOR,
  OPCAO_TRANSACAO,
  ROTULOS_CURTOS_DECISAO,
  TITULO_SIMULADOR,
} from "@/lib/textos";
import type { ItemFila } from "@/lib/tipos";

const APROVADAS_NA_LISTA = 30;

function opcoesDaFila(itens: ItemFila[]): ItemFila[] {
  const alertas = itens.filter((i) => i.decisao !== "APROVAR");
  const aprovadas = itens
    .filter((i) => i.decisao === "APROVAR")
    .slice(0, APROVADAS_NA_LISTA);
  return [...alertas, ...aprovadas];
}

export default function PaginaSimulador() {
  const [opcoes, setOpcoes] = useState<ItemFila[] | null>(null);
  const [selecionado, setSelecionado] = useState<number | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    let cancelado = false;
    obterFila("BLOQUEAR,PEDIR_CONFIRMACAO,APROVAR")
      .then((fila) => !cancelado && setOpcoes(opcoesDaFila(fila.itens)))
      .catch((e: Error) => !cancelado && setErro(e.message));
    return () => {
      cancelado = true;
    };
  }, []);

  const idAtual = selecionado ?? opcoes?.[0]?.id_transacao ?? null;

  return (
    <div className="sentinela-pagina">
      <Heading>{TITULO_SIMULADOR}</Heading>
      <p className="sentinela-legenda">{LEGENDA_SIMULADOR}</p>
      {erro && <EstadoErro mensagem={erro} />}
      {!erro && !opcoes && <EstadoCarregando />}
      {opcoes && idAtual !== null && (
        <>
          <Select
            id="sim-transacao"
            labelText={ESCOLHA_TRANSACAO}
            value={String(idAtual)}
            onChange={(evento) => setSelecionado(Number(evento.target.value))}
          >
            {opcoes.map((item) => (
              <SelectItem
                key={item.id_transacao}
                value={String(item.id_transacao)}
                text={OPCAO_TRANSACAO(
                  item.id_transacao,
                  formatarNota(item.nota),
                  ROTULOS_CURTOS_DECISAO[item.decisao],
                )}
              />
            ))}
          </Select>
          <SimuladorTransacao key={idAtual} idTransacao={idAtual} />
        </>
      )}
    </div>
  );
}
