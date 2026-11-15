"use client";

/**
 * Bloco "Pergunte à IA sobre este caso": o analista faz uma pergunta livre e o Granite responde
 * com as mesmas ferramentas da auditoria (ESPECIFICACAO, seção 16). Nunca muda a decisão.
 */

import { useState } from "react";
import { Button, InlineLoading, TextInput, Tile } from "@carbon/react";
import { perguntarIA } from "@/lib/api";
import { formatarDecimal } from "@/lib/formatacao";
import {
  AJUDA_PERGUNTA,
  BOTAO_PERGUNTAR,
  FERRAMENTAS_USADAS,
  FONTE_PERGUNTA,
  NOMES_FERRAMENTAS,
  PERGUNTA_PENDENTE,
  ROTULO_PERGUNTA,
  TITULO_PERGUNTE_IA,
  TITULO_RESPOSTA_IA,
} from "@/lib/textos";
import type { RespostaPergunta } from "@/lib/tipos";

export const LIMITE_PERGUNTA = 300;

interface PropsPergunteIA {
  idTransacao: number;
}

export default function PergunteIA({ idTransacao }: PropsPergunteIA) {
  const [pergunta, setPergunta] = useState("");
  const [carregando, setCarregando] = useState(false);
  const [resposta, setResposta] = useState<RespostaPergunta | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  async function perguntar() {
    const texto = pergunta.trim();
    if (!texto || carregando) return;
    setCarregando(true);
    setErro(null);
    try {
      setResposta(await perguntarIA(idTransacao, texto));
    } catch (e) {
      setResposta(null);
      setErro((e as Error).message);
    } finally {
      setCarregando(false);
    }
  }

  return (
    <Tile className="sentinela-bloco">
      <h3 className="sentinela-subtitulo">{TITULO_PERGUNTE_IA}</h3>
      <TextInput
        id={`pergunta-ia-${idTransacao}`}
        labelText={ROTULO_PERGUNTA}
        helperText={AJUDA_PERGUNTA}
        maxLength={LIMITE_PERGUNTA}
        value={pergunta}
        onChange={(evento) => setPergunta(evento.target.value)}
        onKeyDown={(evento) => {
          if (evento.key === "Enter") void perguntar();
        }}
      />
      <div className="sentinela-botoes">
        <Button
          onClick={perguntar}
          disabled={carregando || pergunta.trim() === ""}
        >
          {BOTAO_PERGUNTAR}
        </Button>
      </div>
      <div aria-live="polite" aria-busy={carregando}>
        {carregando && <InlineLoading description={PERGUNTA_PENDENTE} />}
        {erro && <p role="alert">{erro}</p>}
        {resposta && !carregando && (
          <div>
            <h4 className="sentinela-subtitulo">{TITULO_RESPOSTA_IA}</h4>
            <p>{resposta.resposta}</p>
            {resposta.ferramentas_usadas.length > 0 && (
              <>
                <p className="sentinela-legenda">{FERRAMENTAS_USADAS}</p>
                <ul className="sentinela-lista">
                  {resposta.ferramentas_usadas.map((ferramenta, indice) => (
                    <li key={`${ferramenta.nome}-${indice}`}>
                      {NOMES_FERRAMENTAS[ferramenta.nome] ?? ferramenta.nome}:{" "}
                      {ferramenta.resumo}
                    </li>
                  ))}
                </ul>
              </>
            )}
            <p className="sentinela-legenda">
              {FONTE_PERGUNTA(
                resposta.fonte,
                formatarDecimal(resposta.latencia_ms, 1),
              )}
            </p>
          </div>
        )}
      </div>
    </Tile>
  );
}