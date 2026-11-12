## O que muda
<!-- 2 a 4 linhas -->

Closes #

## Requisitos e histórias
<!-- exemplo: RF007 · US006 -->

## Como verificar
<!-- comandos e o que observar -->

## Verificações do autor
- [ ] `black --check .`, `ruff check .` e `pytest -q` passam localmente
- [ ] Invariantes da ESPECIFICACAO, seção 11, preservadas (`python -m src.avaliar_agente`)
- [ ] Conformidade rodada com `data/` presente: 0 falhas; skips só de Issues futuras
      (cole aqui a última linha da saída)
- [ ] Não alterei `tests/test_conformidade_*.py` nem a configuração do pytest
- [ ] A alteração corresponde ao escopo da Issue, nada além dela
- [ ] Só arquivos permitidos pela Issue; nada de `data/`, `.venv/`, caches ou `.env` no diff
- [ ] Nenhum segredo, token ou senha
- [ ] Nenhuma linha da base em teste, documentação ou log
- [ ] Testes presentes onde o AGENTS.md (seção 10) exige
- [ ] Contratos públicos novos ou alterados têm docstring
- [ ] Diagramas de `docs/` atualizados se mudou assinatura, módulo ou dependência
- [ ] Interface: estados e textos conforme `docs/08-design-da-interface.md` (se aplicável)

## Verificação manual
<!-- critérios da Issue verificados no navegador, com ✅ ou ❌ -->
