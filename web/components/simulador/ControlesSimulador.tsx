"use client";

/**
 * Controles da compra simulada: valores, hora, chaves e contadores.
 */

import { NumberInput, Slider, Toggle } from "@carbon/react";
import { ehMadrugada, type ValoresSimulador } from "@/lib/simulacao";
import { CAMPOS_SIMULADOR, MADRUGADA_CALCULADA, NAO, SIM } from "@/lib/textos";

type CampoNumerico =
  | "valor"
  | "qtd_transacoes_cartao_1min"
  | "vel_cartao_terminal_1h"
  | "qtd_token_carteira_3m"
  | "dist_terminal_anterior_km";
type CampoLigado = "credito" | "nao_presente" | "ip_pais_desconhecido";

const NUMERICOS: Array<[CampoNumerico, string, number]> = [
  ["valor", CAMPOS_SIMULADOR.valor, 0.01],
  ["qtd_transacoes_cartao_1min", CAMPOS_SIMULADOR.rajada, 1],
  ["vel_cartao_terminal_1h", CAMPOS_SIMULADOR.terminais, 1],
  ["qtd_token_carteira_3m", CAMPOS_SIMULADOR.token, 1],
  ["dist_terminal_anterior_km", CAMPOS_SIMULADOR.distancia, 1],
];
const LIGADOS: Array<[CampoLigado, string]> = [
  ["credito", CAMPOS_SIMULADOR.credito],
  ["nao_presente", CAMPOS_SIMULADOR.naoPresente],
  ["ip_pais_desconhecido", CAMPOS_SIMULADOR.ip],
];

interface PropsControlesSimulador {
  valores: ValoresSimulador;
  aoMudar: (valores: ValoresSimulador) => void;
}

export default function ControlesSimulador({
  valores,
  aoMudar,
}: PropsControlesSimulador) {
  const mudar = (parcial: Partial<ValoresSimulador>) =>
    aoMudar({ ...valores, ...parcial });

  return (
    <div className="sentinela-controles">
      {NUMERICOS.map(([campo, rotulo, passo]) => (
        <NumberInput
          key={campo}
          id={`sim-${campo}`}
          label={rotulo}
          min={0}
          step={passo}
          value={valores[campo]}
          onChange={(_evento, { value }) =>
            mudar({ [campo]: Number(value) || 0 })
          }
        />
      ))}
      <Slider
        id="sim-hora"
        labelText={CAMPOS_SIMULADOR.hora}
        min={0}
        max={23}
        step={1}
        value={valores.hora}
        onChange={({ value }: { value: number }) => mudar({ hora: value })}
      />
      <p className="sentinela-legenda">
        {MADRUGADA_CALCULADA(ehMadrugada(valores.hora))}
      </p>
      <Slider
        id="sim-risco"
        labelText={CAMPOS_SIMULADOR.risco}
        min={0}
        max={100}
        step={1}
        value={valores.risco_estabelecimento}
        onChange={({ value }: { value: number }) =>
          mudar({ risco_estabelecimento: value })
        }
      />
      {LIGADOS.map(([campo, rotulo]) => (
        <Toggle
          key={campo}
          id={`sim-${campo}`}
          labelText={rotulo}
          labelA={NAO}
          labelB={SIM}
          toggled={valores[campo]}
          onToggle={(ligado: boolean) => mudar({ [campo]: ligado })}
        />
      ))}
    </div>
  );
}
