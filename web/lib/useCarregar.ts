/**
 * Carrega dados da API num componente (Issues #93 a #99).
 * Devolve { dados, erro, recarregar }: `dados` fica null enquanto carrega ou quando a
 * `chave` muda (por exemplo, um filtro), e `recarregar` busca de novo.
 */

import { useEffect, useState } from "react";

interface Estado<T> {
  versao: string;
  dados: T | null;
  erro: string | null;
}

export function useCarregar<T>(buscar: () => Promise<T>, chave = "") {
  const [tentativa, setTentativa] = useState(0);
  const [estado, setEstado] = useState<Estado<T>>({ versao: "", dados: null, erro: null });
  const versao = `${chave}#${tentativa}`;

  useEffect(() => {
    let cancelado = false;
    buscar()
      .then((dados) => !cancelado && setEstado({ versao, dados, erro: null }))
      .catch(
        (e: Error) => !cancelado && setEstado({ versao, dados: null, erro: e.message }),
      );
    return () => {
      cancelado = true;
    };
    // `buscar` muda a cada renderização; a versão (chave + tentativa) decide quando buscar.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [versao]);

  const atual = estado.versao === versao;
  return {
    dados: atual ? estado.dados : null,
    erro: atual ? estado.erro : null,
    recarregar: () => setTentativa((t) => t + 1),
  };
}
