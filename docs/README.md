# Documentação do Sentinela

Toda a documentação vive aqui, em texto e Mermaid, e muda no mesmo Pull Request que muda o
código que ela descreve (Docs-as-Code).

| Arquivo | Pergunta que responde | Leitor principal |
| --- | --- | --- |
| [01-requisitos.md](01-requisitos.md) | O que será entregue, com qual prioridade? | Time e avaliadores |
| [02-user-stories.md](02-user-stories.md) | Para quem serve cada funcionalidade e quando está pronta? | Quem implementa e quem revisa |
| [03-user-flows.md](03-user-flows.md) | Que caminho o analista percorre e onde pode falhar? | Quem implementa a interface |
| [04-arquitetura.md](04-arquitetura.md) | Onde o sistema começa e termina, e de que peças é feito? | Time inteiro |
| [06-sequencias.md](06-sequencias.md) | Em que ordem as peças conversam quando o Granite falha ou o analista clica duas vezes? | Quem mexe no agente ou na interface |
| [07-decisoes.md](07-decisoes.md) | Por que decidimos assim, e o que rejeitamos? | Quem pensar em mudar uma decisão |
| [08-design-da-interface.md](08-design-da-interface.md) | Como a tela é, em cada estado? | Quem implementa a interface |
| [backlog.md](backlog.md) | Quais são as Issues, quem faz, o que pode alterar e quando está pronta? | Bob e o time |

## Artefatos que decidimos não produzir

A numeração segue o Manual da IDE (capítulo 2.4.8). Os números que faltam são artefatos que,
pela tabela "Qual diagrama, quando", não se aplicam a este projeto:

- **05 — Diagrama de classes, ERD e máquina de estados:** o domínio tem uma classe central
  (`AgenteSentinela`) e funções puras; não há banco de dados nem entidade com três ou mais
  estados com regra própria por transição. O código é a fonte fiel desse nível.
- **Diagrama de implantação:** o sistema não é hospedado; roda na máquina de cada pessoa
  (ver ADR-002).

## Testes de conformidade

`tests/test_conformidade_nucleo.py` e `tests/test_conformidade_interface.py` traduzem a
ESPECIFICACAO e o `08-design-da-interface.md` em verificações automáticas (ADR-009). São do
líder: o Bob não os altera. Uma Issue com código só termina com 0 falhas neles.
