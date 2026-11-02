# Divisão de tarefas

O projeto foi organizado para que cada integrante pudesse trabalhar de forma
autônoma e, ao mesmo tempo, revisar o trabalho da outra. As tarefas estão
rastreadas nas issues do GitHub.

## Resumo

| Integrante | Issues | Foco |
| --- | --- | --- |
| **Juliana Saunders** | 1, 3, 5, 7, 9, 11, 13 | Planejamento, núcleo de decisão, relatórios, CLI, qualidade, documentação, site |
| **Jaquelline Feitoza** | 2, 4, 6, 8, 10, 12 | Fundação, execução/undo, diagnóstico do SO, automação, testes, wiki |
| **Ambas** | 14 | Release, revisão final e apresentação |

## Detalhamento

### Juliana

| Issue | Entrega | Branch |
| --- | --- | --- |
| 1 | Planejamento, requisitos e backlog | `docs/1-planejamento` |
| 3 | Planejador e regras avançadas | `feat/3-planejador` |
| 5 | Relatórios MD/CSV/JSON | `feat/5-relatorios` |
| 7 | CLI e modo interativo | `feat/7-cli` |
| 9 | CI, hooks e qualidade | `chore/9-ci-hooks` |
| 11 | README e documentação técnica | `docs/11-documentacao` |
| 13 | Página web e GitHub Pages | `feat/13-pagina-web` |
| 14 | Release e apresentação (conjunta) | `release/v2.0.0` |

### Jaquelline

| Issue | Entrega | Branch |
| --- | --- | --- |
| 2 | Fundação do pacote e configuração | `feat/2-fundacao` |
| 4 | Journal, executor e undo | `feat/4-executor-undo` |
| 6 | Diagnóstico do SO (`doctor`) | `feat/6-diagnostico` |
| 8 | Scripts de automação e agendamento | `feat/8-automacao` |
| 10 | Testes de integração e QA | `test/10-integracao` |
| 12 | Wiki do projeto | `docs/12-wiki` |
| 14 | Release e apresentação (conjunta) | `release/v2.0.0` |

## Revisões cruzadas

| PR | Autor | Revisor |
| --- | --- | --- |
| 1 | Juliana | Jaquelline |
| 2 | Jaquelline | Juliana |
| 3 | Juliana | Jaquelline |
| 4 | Jaquelline | Juliana |
| 5 | Juliana | Jaquelline |
| 6 | Jaquelline | Juliana |
| 7 | Juliana | Jaquelline |
| 8 | Jaquelline | Juliana |
| 9 | Juliana | Jaquelline |
| 10 | Jaquelline | Juliana |
| 11 | Juliana | Jaquelline |
| 12 | Jaquelline | Juliana |
| 13 | Juliana | Jaquelline |
| 14 | Ambas | Ambas |

## Como o trabalho conjunto aparece no Git

- Cada branch tem o número da issue.
- Os commits seguem Conventional Commits.
- O autor do commit corresponde à integrante responsável.
- Trabalhos conjuntos usam `Co-authored-by`.
- Cada PR referencia a issue com `Closes #N`.
- O merge é feito em `develop`; a release vai para `main`.

## Cronograma executado

| Etapa | Issues | Resultado |
| --- | --- | --- |
| Fundação | 1–2 | Pacote, configuração e planejamento |
| Núcleo | 3–4 | Planejador, executor, journal e undo |
| Recursos | 5–6 | Relatórios e diagnóstico |
| Interface | 7–8 | CLI e automação |
| Qualidade | 9–10 | CI, hooks e integração |
| Documentação | 11–12 | README, docs e wiki |
| Entrega | 13–14 | Site, release e apresentação |

## Acordos de trabalho

- Português na documentação e nas mensagens de commit descritivas.
- Código e identificadores em português quando fizer sentido para o domínio.
- Sem dependências externas obrigatórias.
- Testes antes de abrir PR.
- Revisão obrigatória da outra integrante.
- Nenhum segredo ou arquivo local commitado.
