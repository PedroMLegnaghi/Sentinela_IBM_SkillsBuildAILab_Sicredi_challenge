"use client";

/**
 * Página "Fila de alertas": indicadores, filtro e tabela à esquerda; painel da transação
 * selecionada à direita. Busca a fila inteira uma vez e filtra no navegador.
 */

import { useEffect, useMemo, useState } from "react";
import { Heading } from "@carbon/react";
import EstadoCarregando from "@/components/comuns/EstadoCarregando";
import EstadoErro from "@/components/comuns/EstadoErro";
import FiltroDecisoes, {
  ORDEM_DECISOES,
} from "@/components/fila/FiltroDecisoes";
import Indicadores from "@/components/fila/Indicadores";
import TabelaFila from "@/components/fila/TabelaFila";
import PainelTransacao from "@/components/painel/PainelTransacao";
import { obterFila } from "@/lib/api";
import {
  FILTRO_VAZIO,
  LEGENDA_FILA,
  NAV_FILA,
  SELECIONE_TRANSACAO,
} from "@/lib/textos";
import type { Decisao, RespostaFila } from "@/lib/tipos";

const FILTRO_PADRAO: Decisao[] = ["BLOQUEAR", "PEDIR_CONFIRMACAO"];

export default function PaginaFila() {
  const [fila, setFila] = useState<RespostaFila | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [tentativa, setTentativa] = useState(0);
  const [filtro, setFiltro] = useState<Decisao[]>(FILTRO_PADRAO);
  const [selecionado, setSelecionado] = useState<number | null>(null);

  useEffect(() => {
    let cancelado = false;
    obterFila(ORDEM_DECISOES.join(","))
      .then((dados) => !cancelado && setFila(dados))
      .catch((e: Error) => !cancelado && setErro(e.message));
    return () => {
      cancelado = true;
    };
  }, [tentativa]);

  const visiveis = useMemo(
    () =>
      fila ? fila.itens.filter((item) => filtro.includes(item.decisao)) : [],
    [fila, filtro],
  );
  const idAberto = visiveis.some((i) => i.id_transacao === selecionado)
    ? selecionado
    : (visiveis[0]?.id_transacao ?? null);

  return (
    <div>
      <Heading>{NAV_FILA}</Heading>
      <p className="sentinela-legenda">{LEGENDA_FILA}</p>
      {erro && (
        <EstadoErro
          mensagem={erro}
          aoTentarNovamente={() => {
            setErro(null);
            setTentativa((t) => t + 1);
          }}
        />
      )}
      {!erro && !fila && <EstadoCarregando />}
      {fila && (
        <div className="sentinela-fila">
          <div className="sentinela-fila-esquerda">
            <Indicadores fila={fila} />
            <FiltroDecisoes selecionadas={filtro} aoMudar={setFiltro} />
            {visiveis.length === 0 ? (
              <p role="status">{FILTRO_VAZIO}</p>
            ) : (
              <TabelaFila
                itens={visiveis}
                total={fila.total_fila}
                idSelecionado={idAberto}
                aoSelecionar={setSelecionado}
              />
            )}
          </div>
          <div className="sentinela-fila-direita">
            {idAberto === null ? (
              <p>{SELECIONE_TRANSACAO}</p>
            ) : (
              <PainelTransacao key={idAberto} idTransacao={idAberto} />
            )}
          </div>
        </div>
      )}
    </div>
  );
}
