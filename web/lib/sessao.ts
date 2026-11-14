/**
 * Sessão simulada do site (ESPECIFICACAO, seção 17.1; Issue #91).
 * Guarda { token, perfil } no sessionStorage da aba. Não há senha: é só uma simulação.
 */

import { useSyncExternalStore } from "react";
import type { Papel, Sessao } from "@/lib/tipos";

const CHAVE = "sentinela.sessao";
const ouvintes = new Set<() => void>();

let brutoEmCache: string | null = null;
let sessaoEmCache: Sessao | null = null;

function lerBruto(): string | null {
  try {
    return window.sessionStorage.getItem(CHAVE);
  } catch {
    return null;
  }
}

function avisar(): void {
  ouvintes.forEach((ouvinte) => ouvinte());
}

/** Sessão atual, ou null fora do navegador e sem sessão. */
export function obterSessao(): Sessao | null {
  if (typeof window === "undefined") return null;
  const bruto = lerBruto();
  if (bruto !== brutoEmCache) {
    brutoEmCache = bruto;
    try {
      sessaoEmCache = bruto ? (JSON.parse(bruto) as Sessao) : null;
    } catch {
      sessaoEmCache = null;
    }
  }
  return sessaoEmCache;
}

/** Grava a sessão depois de POST /api/sessao. */
export function guardarSessao(sessao: Sessao): void {
  try {
    window.sessionStorage.setItem(CHAVE, JSON.stringify(sessao));
  } catch {
    // Sem sessionStorage (janela privada bloqueada): a sessão vale só até recarregar.
    brutoEmCache = JSON.stringify(sessao);
    sessaoEmCache = sessao;
  }
  avisar();
}

/** Encerra a sessão. */
export function sair(): void {
  try {
    window.sessionStorage.removeItem(CHAVE);
  } catch {
    // nada a remover
  }
  brutoEmCache = null;
  sessaoEmCache = null;
  avisar();
}

function assinar(ouvinte: () => void): () => void {
  ouvintes.add(ouvinte);
  return () => ouvintes.delete(ouvinte);
}

/**
 * Sessão atual para componentes. Devolve undefined enquanto a página não carregou no
 * navegador (renderização no servidor), null sem sessão e a Sessao quando há login.
 */
export function useSessao(): Sessao | null | undefined {
  return useSyncExternalStore(assinar, obterSessao, () => undefined);
}

/** Página inicial de cada papel. */
export function inicioDoPapel(papel: Papel): string {
  if (papel === "associado") return "/associado";
  if (papel === "gerente") return "/filial/painel";
  return "/filial/fila";
}

/** Iniciais do nome para o avatar ("Ana Souza" → "AS"). */
export function iniciais(nome: string): string {
  const partes = nome.trim().split(/\s+/);
  const primeira = partes[0]?.[0] ?? "";
  const ultima = partes.length > 1 ? partes[partes.length - 1][0] : "";
  return (primeira + ultima).toUpperCase();
}
