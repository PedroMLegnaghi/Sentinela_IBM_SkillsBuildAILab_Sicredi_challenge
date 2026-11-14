"use client";

/**
 * /filial leva cada papel para a sua página inicial (Issue #91).
 */

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { inicioDoPapel, useSessao } from "@/lib/sessao";
import { VERIFICANDO_SESSAO } from "@/lib/textos";

export default function Pagina() {
  const sessao = useSessao();
  const router = useRouter();
  useEffect(() => {
    if (sessao) router.replace(inicioDoPapel(sessao.perfil.papel));
  }, [sessao, router]);
  return <p className="sc-carregando">{VERIFICANDO_SESSAO}</p>;
}
