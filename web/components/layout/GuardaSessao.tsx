"use client";

/**
 * Só mostra o conteúdo quando há sessão do papel certo; senão, leva para /entrar
 * (ou para o início do próprio papel). Issue #91.
 */

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { inicioDoPapel, useSessao } from "@/lib/sessao";
import type { Papel, Sessao } from "@/lib/tipos";
import { VERIFICANDO_SESSAO } from "@/lib/textos";

interface PropsGuarda {
  papeis: Papel[];
  children: (sessao: Sessao) => React.ReactNode;
}

export default function GuardaSessao({ papeis, children }: PropsGuarda) {
  const sessao = useSessao();
  const router = useRouter();
  const permitido = !!sessao && papeis.includes(sessao.perfil.papel);

  useEffect(() => {
    if (sessao === undefined) return;
    if (sessao === null) router.replace("/entrar");
    else if (!papeis.includes(sessao.perfil.papel)) {
      router.replace(inicioDoPapel(sessao.perfil.papel));
    }
  }, [sessao, papeis, router]);

  if (!permitido) {
    return <p className="sc-carregando" style={{ padding: 24 }}>{VERIFICANDO_SESSAO}</p>;
  }
  return <>{children(sessao)}</>;
}
