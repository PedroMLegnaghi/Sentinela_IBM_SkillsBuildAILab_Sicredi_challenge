"use client";

/**
 * Simulação a partir de uma transação: controles à esquerda; "Original" e "Simulada" lado a
 * lado, e o parecer da IA para a simulada logo abaixo.
 */

import { useEffect, useState } from "react";
import { Button } from "@carbon/react";
import EstadoCarregando from "@/components/comuns/EstadoCarregando";
import EstadoErro from "@/components/comuns/EstadoErro";
import CartaoAuditoria from "@/components/painel/CartaoAuditoria";
import ControlesSimulador from "@/components/simulador/ControlesSimulador";
import ResultadoAnalise from "@/components/simulador/ResultadoAnalise";
import { analisar, obterTransacao } from "@/lib/api";
import {
  montarEntradaSimulada,
  valoresIniciais,
  type ValoresSimulador,
} from "@/lib/simulacao";
import {
  BOTAO_ANALISAR,
  BOTAO_VOLTAR_ORIGINAL,
  SIMULADA_VAZIA,
  TITULO_ORIGINAL,
  TITULO_SIMULADA,
} from "@/lib/textos";
import type { RespostaAnalisar, RespostaTransacao } from "@/lib/tipos";

interface PropsSimuladorTransacao {
  idTransacao: number;
}

export default function SimuladorTransacao({
  idTransacao,
}: PropsSimuladorTransacao) {
  const [original, setOriginal] = useState<RespostaTransacao | null>(null);
  const [valores, setValores] = useState<ValoresSimulador | null>(null);
  const [simulada, setSimulada] = useState<RespostaAnalisar | null>(null);
  const [analisando, setAnalisando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    let cancelado = false;
    obterTransacao(idTransacao)
      .then((dados) => {
        if (cancelado) return;
        setOriginal(dados);
        setValores(valoresIniciais(dados.transacao));
      })
      .catch((e: Error) => !cancelado && setErro(e.message));
    return () => {
      cancelado = true;
    };
  }, [idTransacao]);

  if (erro) return <EstadoErro mensagem={erro} />;
  if (!original || !valores) return <EstadoCarregando />;

  async function simular() {
    if (!original || !valores) return;
    setAnalisando(true);
    try {
      setSimulada(
        await analisar(montarEntradaSimulada(original.transacao, valores)),
      );
    } catch (e) {
      setErro((e as Error).message);
    } finally {
      setAnalisando(false);
    }
  }

  return (
    <div className="sentinela-simulador">
      <div>
        <ControlesSimulador valores={valores} aoMudar={setValores} />
        <div className="sentinela-botoes">
          <Button onClick={simular} disabled={analisando}>
            {BOTAO_ANALISAR}
          </Button>
          <Button
            kind="ghost"
            onClick={() => {
              setValores(valoresIniciais(original.transacao));
              setSimulada(null);
            }}
          >
            {BOTAO_VOLTAR_ORIGINAL}
          </Button>
        </div>
      </div>
      <div>
        <div className="sentinela-lado-a-lado">
          <ResultadoAnalise
            titulo={TITULO_ORIGINAL}
            analise={original.analise}
          />
          {simulada ? (
            <ResultadoAnalise
              titulo={TITULO_SIMULADA}
              analise={simulada.analise}
            />
          ) : (
            <p className="sentinela-legenda">{SIMULADA_VAZIA}</p>
          )}
        </div>
        {simulada?.id_auditoria && (
          <CartaoAuditoria
            key={simulada.id_auditoria}
            idAuditoria={simulada.id_auditoria}
          />
        )}
      </div>
    </div>
  );
}
