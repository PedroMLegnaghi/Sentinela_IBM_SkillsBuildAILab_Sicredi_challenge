"use client";

/**
 * Tela de entrada simulada (ESPECIFICACAO, seção 17; Issue #91): escolhe um perfil e entra.
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { entrar, obterPerfis } from "@/lib/api";
import { guardarSessao, iniciais, inicioDoPapel } from "@/lib/sessao";
import type { Papel, Perfil } from "@/lib/tipos";
import EstadoErro from "@/components/comuns/EstadoErro";
import {
  ALT_LOGO,
  CARREGANDO,
  ENTRANDO,
  ENTRAR_BOTAO,
  ENTRAR_LEGENDA,
  ENTRAR_TITULO,
  GRUPOS_PAPEL,
  ROTULOS_PAPEL,
} from "@/lib/textos";

const ORDEM_PAPEIS: Papel[] = ["associado", "auditor", "gerente", "matriz"];

export default function PaginaEntrar() {
  const router = useRouter();
  const [perfis, setPerfis] = useState<Perfil[] | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [escolhido, setEscolhido] = useState<string | null>(null);
  const [entrando, setEntrando] = useState(false);
  const [tentativa, setTentativa] = useState(0);

  useEffect(() => {
    let ativo = true;
    obterPerfis()
      .then((r) => {
        if (!ativo) return;
        setPerfis(r.perfis);
        setErro(null);
        setEscolhido((atual) => atual ?? r.perfis[0]?.id_perfil ?? null);
      })
      .catch((e: Error) => ativo && setErro(e.message));
    return () => {
      ativo = false;
    };
  }, [tentativa]);

  async function aoEntrar() {
    if (!escolhido) return;
    setEntrando(true);
    try {
      const sessao = await entrar(escolhido);
      guardarSessao(sessao);
      router.push(inicioDoPapel(sessao.perfil.papel));
    } catch (e) {
      setErro((e as Error).message);
      setEntrando(false);
    }
  }

  return (
    <main className="sc-entrar">
      <div className="sc-entrar__caixa">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img className="sc-entrar__logo" src="/logo-sicredi-branco.png" alt={ALT_LOGO} />
        <div className="sc-entrar__folha">
          <h1 style={{ fontSize: "1.375rem" }}>{ENTRAR_TITULO}</h1>
          <p className="sc-apoio" style={{ marginTop: 4 }}>
            {ENTRAR_LEGENDA}
          </p>

          {erro && <EstadoErro mensagem={erro} aoTentarNovamente={() => setTentativa((t) => t + 1)} />}
          {!perfis && !erro && <p className="sc-carregando">{CARREGANDO}</p>}

          {perfis &&
            ORDEM_PAPEIS.map((papel) => {
              const doPapel = perfis.filter((p) => p.papel === papel);
              if (!doPapel.length) return null;
              return (
                <section key={papel} className="sc-entrar__grupo" aria-label={GRUPOS_PAPEL[papel]}>
                  <h2 className="sc-rotulo" style={{ fontStyle: "normal" }}>
                    {GRUPOS_PAPEL[papel]}
                  </h2>
                  {doPapel.map((perfil) => (
                    <button
                      key={perfil.id_perfil}
                      type="button"
                      className="sc-entrar__pessoa"
                      aria-pressed={escolhido === perfil.id_perfil}
                      onClick={() => setEscolhido(perfil.id_perfil)}
                      onDoubleClick={aoEntrar}
                    >
                      <span className="sc-avatar" aria-hidden="true">
                        {iniciais(perfil.nome)}
                      </span>
                      <span>
                        <b>{perfil.nome}</b>
                        <small>
                          {ROTULOS_PAPEL[perfil.papel]} · {perfil.filial.nome}
                        </small>
                      </span>
                    </button>
                  ))}
                </section>
              );
            })}

          {perfis && (
            <button
              type="button"
              className="sc-botao"
              style={{ marginTop: 18 }}
              disabled={!escolhido || entrando}
              onClick={aoEntrar}
            >
              {entrando ? ENTRANDO : ENTRAR_BOTAO}
            </button>
          )}
        </div>
      </div>
    </main>
  );
}
