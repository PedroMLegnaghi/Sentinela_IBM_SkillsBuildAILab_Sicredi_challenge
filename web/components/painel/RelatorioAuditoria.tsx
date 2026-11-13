"use client";

/**
 * Relatório concluído da auditoria: parecer em destaque, evidências, dados ausentes e o
 * rastro das ferramentas, na ordem em que a IA as usou.
 */

import { InlineNotification } from "@carbon/react";
import { formatarDecimal } from "@/lib/formatacao";
import {
  DADOS_AUSENTES,
  EVIDENCIAS_A_FAVOR,
  EVIDENCIAS_CONTRA,
  FERRAMENTAS_USADAS,
  FONTE_AUDITORIA,
  NOMES_FERRAMENTAS,
  RISCO_E_CONFIANCA,
  RISCO_INDEFINIDO,
  ROTULOS_CONFIANCA,
  ROTULOS_PARECER,
  ROTULOS_RISCO_IA,
} from "@/lib/textos";
import type { Auditoria, ParecerIA } from "@/lib/tipos";

const ESTILO_PARECER: Record<
  ParecerIA,
  { kind: "success" | "warning" | "info"; icone: string }
> = {
  CONFIRMA: { kind: "success", icone: "✔" },
  DIVERGE: { kind: "warning", icone: "⚠" },
  INCONCLUSIVO: { kind: "info", icone: "?" },
};

function ListaTexto({ titulo, itens }: { titulo: string; itens: string[] }) {
  if (itens.length === 0) return null;
  return (
    <div className="sentinela-bloco">
      <h4 className="sentinela-rotulo">{titulo}</h4>
      <ul className="sentinela-lista">
        {itens.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

interface PropsRelatorioAuditoria {
  auditoria: Auditoria;
}

export default function RelatorioAuditoria({
  auditoria,
}: PropsRelatorioAuditoria) {
  const relatorio = auditoria.relatorio;
  if (!relatorio) return null;
  const estilo = ESTILO_PARECER[relatorio.parecer];
  const risco = relatorio.risco_ia
    ? ROTULOS_RISCO_IA[relatorio.risco_ia]
    : RISCO_INDEFINIDO;
  const ms = formatarDecimal(auditoria.latencia_ms ?? 0, 0);

  return (
    <div>
      <InlineNotification
        kind={estilo.kind}
        title=""
        subtitle={`${estilo.icone} ${ROTULOS_PARECER[relatorio.parecer]}`}
        hideCloseButton
        lowContrast
      />
      <p className="sentinela-legenda">
        {RISCO_E_CONFIANCA(risco, ROTULOS_CONFIANCA[relatorio.confianca])}
      </p>
      <p>{relatorio.explicacao}</p>
      <ListaTexto
        titulo={EVIDENCIAS_A_FAVOR}
        itens={relatorio.evidencias_a_favor}
      />
      <ListaTexto
        titulo={EVIDENCIAS_CONTRA}
        itens={relatorio.evidencias_contra}
      />
      <ListaTexto titulo={DADOS_AUSENTES} itens={relatorio.dados_ausentes} />
      <div className="sentinela-bloco">
        <h4 className="sentinela-rotulo">{FERRAMENTAS_USADAS}</h4>
        <ol className="sentinela-lista">
          {relatorio.ferramentas_usadas.map((f, indice) => (
            <li key={`${f.nome}-${indice}`}>
              <strong>{NOMES_FERRAMENTAS[f.nome] ?? f.nome}</strong>: {f.resumo}
            </li>
          ))}
        </ol>
      </div>
      <p className="sentinela-legenda">
        {FONTE_AUDITORIA(relatorio.fonte, relatorio.modelo, ms)}
      </p>
    </div>
  );
}
