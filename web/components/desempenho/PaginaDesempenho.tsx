"use client";

/**
 * Página "Desempenho": números de março do Sentinela contra o sistema atual, detalhes do
 * modelo e, quando existirem, as análises extras (IA contra modelo, custos).
 */

import { useEffect, useState } from "react";
import { Heading, InlineNotification } from "@carbon/react";
import EstadoCarregando from "@/components/comuns/EstadoCarregando";
import EstadoErro from "@/components/comuns/EstadoErro";
import ComparacaoSistemas from "@/components/desempenho/ComparacaoSistemas";
import DetalhesModelo from "@/components/desempenho/DetalhesModelo";
import IndicadoresDesempenho from "@/components/desempenho/IndicadoresDesempenho";
import SecaoCustos from "@/components/desempenho/SecaoCustos";
import SecaoIaContraModelo from "@/components/desempenho/SecaoIaContraModelo";
import { obterMetricas } from "@/lib/api";
import { formatarInteiro } from "@/lib/formatacao";
import {
  AVISO_SINTETICO,
  LEGENDA_DESEMPENHO,
  TITULO_DESEMPENHO,
} from "@/lib/textos";
import type { RespostaMetricas } from "@/lib/tipos";

export default function PaginaDesempenho() {
  const [dados, setDados] = useState<RespostaMetricas | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [tentativa, setTentativa] = useState(0);

  useEffect(() => {
    let cancelado = false;
    obterMetricas()
      .then((resposta) => !cancelado && setDados(resposta))
      .catch((e: Error) => !cancelado && setErro(e.message));
    return () => {
      cancelado = true;
    };
  }, [tentativa]);

  if (erro) {
    const tentarDeNovo = () => {
      setErro(null);
      setTentativa((t) => t + 1);
    };
    return <EstadoErro mensagem={erro} aoTentarNovamente={tentarDeNovo} />;
  }
  if (!dados) return <EstadoCarregando />;

  const { metricas, avaliacao, extras } = dados;
  return (
    <div className="sentinela-pagina">
      <Heading>{TITULO_DESEMPENHO}</Heading>
      <p className="sentinela-legenda">
        {LEGENDA_DESEMPENHO(formatarInteiro(avaliacao.transacoes))}
      </p>
      <IndicadoresDesempenho avaliacao={avaliacao} />
      <ComparacaoSistemas avaliacao={avaliacao} />
      {extras.ia_contra_modelo && (
        <SecaoIaContraModelo dados={extras.ia_contra_modelo} />
      )}
      {extras.custos && <SecaoCustos custos={extras.custos} />}
      <DetalhesModelo metricas={metricas} />
      <InlineNotification
        kind="info"
        title=""
        subtitle={AVISO_SINTETICO}
        hideCloseButton
        lowContrast
      />
    </div>
  );
}
