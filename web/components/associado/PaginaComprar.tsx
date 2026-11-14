"use client";

/**
 * Simular compra (Issue #95): cenários prontos e o formulário completo. A compra passa pelo
 * Sentinela e entra no extrato e na fila da agência. Tela 4 do protótipo.
 */

import { useState } from "react";
import Link from "next/link";
import { obterInicio, simularCompra } from "@/lib/api";
import { useCarregar } from "@/lib/useCarregar";
import { CENARIOS, ESTABELECIMENTOS, montarEntradaCompra, type ValoresCompra } from "@/lib/compra";
import type { RespostaCompra } from "@/lib/tipos";
import EstadoErro from "@/components/comuns/EstadoErro";
import { formatarTipo } from "@/lib/formatacao";
import {
  BOTAO_COMPRAR,
  CAMPOS_COMPRA,
  CARREGANDO,
  CARTAO_BLOQUEADO,
  CARTAO_DESCRICAO,
  CENARIO_PRONTO,
  COMPRANDO,
  ERRO_CARTAO_BLOQUEADO,
  LEGENDA_COMPRAR,
  MAIS_DETALHES,
  MODALIDADES,
  PAISES,
  RESULTADO_COMPRA,
  TITULO_COMPRAR,
  VER_AVISO,
  VER_COMPRA,
} from "@/lib/textos";

const CLASSE_RESULTADO: Record<string, string> = {
  APROVADA: "sc-aviso--ok",
  AGUARDANDO: "sc-aviso--espera",
  BLOQUEADA: "sc-aviso--bloqueio",
  CONTESTADA: "sc-aviso--bloqueio",
};

export default function PaginaComprar() {
  const { dados: inicio, erro: erroInicio, recarregar } = useCarregar(obterInicio);
  const [cenario, setCenario] = useState<string | null>(CENARIOS[0].id);
  const [valores, setValores] = useState<ValoresCompra>(CENARIOS[0].valores);
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const [resultado, setResultado] = useState<RespostaCompra | null>(null);

  const cartao = inicio?.cartoes.find((c) => c.tipo === valores.tipoCartao) ?? null;

  function mudar(parcial: Partial<ValoresCompra>) {
    setValores((v) => ({ ...v, ...parcial }));
    setCenario(null);
    setResultado(null);
  }

  function escolherCenario(id: string) {
    const escolhido = CENARIOS.find((c) => c.id === id);
    if (!escolhido) return;
    setValores(escolhido.valores);
    setCenario(id);
    setResultado(null);
    setErro(null);
  }

  async function comprar(evento: React.FormEvent) {
    evento.preventDefault();
    if (!cartao) return;
    setEnviando(true);
    setErro(null);
    setResultado(null);
    try {
      setResultado(await simularCompra(montarEntradaCompra(valores, cartao.id)));
      recarregar();
    } catch (e) {
      const mensagem = (e as Error).message;
      setErro(mensagem.includes("(409)") ? ERRO_CARTAO_BLOQUEADO : mensagem);
    } finally {
      setEnviando(false);
    }
  }

  const numero = (campo: keyof ValoresCompra) => (e: React.ChangeEvent<HTMLInputElement>) =>
    mudar({ [campo]: Number(e.target.value) } as Partial<ValoresCompra>);

  return (
    <>
      <div className="sc-cabecalho-tela">
        <h1>{TITULO_COMPRAR}</h1>
      </div>
      <p className="sc-apoio" style={{ marginBottom: 14 }}>
        {LEGENDA_COMPRAR}
      </p>

      {erroInicio && <EstadoErro mensagem={erroInicio} aoTentarNovamente={recarregar} />}
      {!inicio && !erroInicio && <p className="sc-carregando">{CARREGANDO}</p>}

      {inicio && (
        <form onSubmit={comprar} className="sc-formulario" noValidate>
          <fieldset>
            <legend className="sc-rotulo">{CENARIO_PRONTO}</legend>
            <div className="sc-chips" style={{ marginTop: 6 }}>
              {CENARIOS.map((c) => (
                <button
                  key={c.id}
                  type="button"
                  className="sc-chip"
                  aria-pressed={cenario === c.id}
                  title={c.descricao}
                  onClick={() => escolherCenario(c.id)}
                >
                  {c.nome}
                </button>
              ))}
            </div>
          </fieldset>

          <label className="sc-campo">
            <span>{CAMPOS_COMPRA.cartao}</span>
            <select
              value={valores.tipoCartao}
              onChange={(e) => mudar({ tipoCartao: e.target.value as ValoresCompra["tipoCartao"] })}
            >
              {inicio.cartoes.map((c) => (
                <option key={c.id} value={c.tipo}>
                  {CARTAO_DESCRICAO(formatarTipo(c.tipo), c.final)}
                  {c.bloqueado ? ` (${CARTAO_BLOQUEADO})` : ""}
                </option>
              ))}
            </select>
          </label>

          <div className="sc-duas">
            <label className="sc-campo">
              <span>{CAMPOS_COMPRA.valor}</span>
              <input type="number" min={0} step={0.01} inputMode="decimal" value={valores.valor} onChange={numero("valor")} />
            </label>
            <label className="sc-campo">
              <span>{CAMPOS_COMPRA.hora}</span>
              <input type="number" min={0} max={23} step={1} value={valores.hora} onChange={numero("hora")} />
            </label>
          </div>

          <label className="sc-campo">
            <span>{CAMPOS_COMPRA.estabelecimento}</span>
            <select value={valores.estabelecimento} onChange={(e) => mudar({ estabelecimento: e.target.value })}>
              {ESTABELECIMENTOS.map((e) => (
                <option key={e.nome} value={e.nome}>
                  {e.nome}
                </option>
              ))}
            </select>
          </label>

          <div className="sc-duas">
            <label className="sc-campo">
              <span>{CAMPOS_COMPRA.modalidade}</span>
              <select
                value={valores.nao_presente ? "nao" : "sim"}
                onChange={(e) => mudar({ nao_presente: e.target.value === "nao" })}
              >
                <option value="sim">{MODALIDADES.presente}</option>
                <option value="nao">{MODALIDADES.naoPresente}</option>
              </select>
            </label>
            <label className="sc-campo">
              <span>{CAMPOS_COMPRA.pais}</span>
              <select
                value={valores.ip_pais_desconhecido ? "desconhecido" : "conhecido"}
                onChange={(e) => mudar({ ip_pais_desconhecido: e.target.value === "desconhecido" })}
              >
                <option value="conhecido">{PAISES.conhecido}</option>
                <option value="desconhecido">{PAISES.desconhecido}</option>
              </select>
            </label>
          </div>

          <label className="sc-campo">
            <span>{CAMPOS_COMPRA.rajada}</span>
            <input type="number" min={0} step={1} value={valores.qtd_transacoes_cartao_1min} onChange={numero("qtd_transacoes_cartao_1min")} />
          </label>

          <details className="sc-detalhes">
            <summary>{MAIS_DETALHES}</summary>
            <label className="sc-campo">
              <span>{CAMPOS_COMPRA.terminais}</span>
              <input type="number" min={0} step={1} value={valores.vel_cartao_terminal_1h} onChange={numero("vel_cartao_terminal_1h")} />
            </label>
            <label className="sc-campo">
              <span>{CAMPOS_COMPRA.token}</span>
              <input type="number" min={0} step={1} value={valores.qtd_token_carteira_3m} onChange={numero("qtd_token_carteira_3m")} />
            </label>
            <label className="sc-campo">
              <span>{CAMPOS_COMPRA.distancia}</span>
              <input type="number" min={0} step={1} value={valores.dist_terminal_anterior_km} onChange={numero("dist_terminal_anterior_km")} />
            </label>
          </details>

          <button type="submit" className="sc-botao" disabled={enviando || !cartao}>
            {enviando ? COMPRANDO : BOTAO_COMPRAR}
          </button>
        </form>
      )}

      {erro && (
        <div className="sc-aviso sc-aviso--bloqueio" role="alert" style={{ marginTop: 12 }}>
          {erro}
        </div>
      )}

      {resultado && (
        <div
          className={`sc-aviso ${CLASSE_RESULTADO[resultado.compra.situacao]}`}
          role="status"
          style={{ marginTop: 12 }}
        >
          <b>{RESULTADO_COMPRA[resultado.compra.situacao].titulo}</b>{" "}
          {RESULTADO_COMPRA[resultado.compra.situacao].texto}
          <div className="sc-linha" style={{ marginTop: 8, justifyContent: "flex-start" }}>
            {resultado.id_notificacao && (
              <Link
                className="sc-botao sc-botao--pequeno"
                href={`/associado/avisos/${resultado.id_notificacao}?compra=${resultado.compra.id_compra}`}
              >
                {VER_AVISO}
              </Link>
            )}
            <Link
              className="sc-botao sc-botao--pequeno sc-botao--secundario"
              href={`/associado/compras/${resultado.compra.id_compra}`}
            >
              {VER_COMPRA}
            </Link>
          </div>
        </div>
      )}
    </>
  );
}
