"use client";

/**
 * Cartão "Auditoria da IA": dispara a auditoria da transação e consulta o resultado
 * a cada 2 s, por até 60 s (ESPECIFICACAO, seção 14). Nunca bloqueia a decisão do modelo.
 */

import { useCallback, useEffect, useState } from "react";
import { InlineLoading, Tile } from "@carbon/react";
import EstadoErro from "@/components/comuns/EstadoErro";
import RelatorioAuditoria from "@/components/painel/RelatorioAuditoria";
import { iniciarAuditoria, obterAuditoria } from "@/lib/api";
import {
  AUDITORIA_DEMOROU,
  AUDITORIA_PENDENTE,
  TITULO_AUDITORIA,
} from "@/lib/textos";
import type { Auditoria } from "@/lib/tipos";

export const INTERVALO_CONSULTA_MS = 2000;
export const LIMITE_CONSULTA_MS = 60000;

type Estado =
  | { tipo: "pendente" }
  | { tipo: "concluida"; auditoria: Auditoria }
  | { tipo: "erro"; mensagem: string };

const esperar = (ms: number) =>
  new Promise((resolver) => setTimeout(resolver, ms));

async function acompanhar(
  idTransacao: number,
  cancelado: () => boolean,
): Promise<Estado> {
  const { id_auditoria: id } = await iniciarAuditoria(idTransacao);
  const inicio = Date.now();
  while (!cancelado()) {
    const auditoria = await obterAuditoria(id);
    if (auditoria.status === "concluida" && auditoria.relatorio) {
      return { tipo: "concluida", auditoria };
    }
    if (auditoria.status === "erro") {
      return {
        tipo: "erro",
        mensagem: auditoria.mensagem ?? AUDITORIA_DEMOROU,
      };
    }
    if (Date.now() - inicio >= LIMITE_CONSULTA_MS) break;
    await esperar(INTERVALO_CONSULTA_MS);
  }
  return { tipo: "erro", mensagem: AUDITORIA_DEMOROU };
}

interface PropsCartaoAuditoria {
  idTransacao: number;
}

export default function CartaoAuditoria({ idTransacao }: PropsCartaoAuditoria) {
  const [estado, setEstado] = useState<Estado>({ tipo: "pendente" });
  const [tentativa, setTentativa] = useState(0);

  const tentarDeNovo = useCallback(() => {
    setEstado({ tipo: "pendente" });
    setTentativa((t) => t + 1);
  }, []);

  useEffect(() => {
    let cancelado = false;
    acompanhar(idTransacao, () => cancelado)
      .then((novo) => !cancelado && setEstado(novo))
      .catch(
        (erro: Error) =>
          !cancelado && setEstado({ tipo: "erro", mensagem: erro.message }),
      );
    return () => {
      cancelado = true;
    };
  }, [idTransacao, tentativa]);

  return (
    <Tile
      className="sentinela-cartao-auditoria"
      aria-live="polite"
      aria-busy={estado.tipo === "pendente"}
    >
      <h3 className="sentinela-subtitulo">{TITULO_AUDITORIA}</h3>
      {estado.tipo === "pendente" && (
        <InlineLoading description={AUDITORIA_PENDENTE} />
      )}
      {estado.tipo === "erro" && (
        <EstadoErro
          mensagem={estado.mensagem}
          aoTentarNovamente={tentarDeNovo}
        />
      )}
      {estado.tipo === "concluida" && (
        <RelatorioAuditoria auditoria={estado.auditoria} />
      )}
    </Tile>
  );
}
