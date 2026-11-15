## O que muda
<!-- 2 a 4 linhas -->

Closes #

## Como verificar
<!-- comandos e o que observar -->

## Verificações do autor
- [ ] Portão Python: `black --check .`, `ruff check .` e `pytest -q` cole a última linha
- [ ] Portão do site, se mexeu em `web/`: lint, typecheck, test e build
- [ ] Invariantes preservadas (`python -m src.avaliar_agente`)
- [ ] Não alterei `tests/test_conformidade_*.py`
- [ ] Só arquivos permitidos pela Issue; nada de CSV bruto, `feedback.csv`, `.venv/`, caches ou `.env`
- [ ] Nenhum segredo, identificador ou linha da base em código, teste ou log
- [ ] CI verde antes do merge

## Verificação manual
<!-- o que foi conferido no navegador, com ✅ ou ❌ -->
