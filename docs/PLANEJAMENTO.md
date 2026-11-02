# Planejamento do CaosZero 2.0

## 1. Contexto

O CaosZero nasceu como uma ideia simples: organizar arquivos acumulados em
pastas como `Downloads`, `Documentos` e `Desktop`. Para o projeto integrador de
**Sistemas Operacionais**, essa ideia foi mantida e evoluída para uma aplicação
de linha de comando capaz de **automatizar tarefas com arquivos** de forma
segura, auditável e reversível.

O recorte do trabalho é o tópico **4.5. Automatizador de Tarefas com Arquivos**
do documento `Projeto.md` da disciplina. Os tópicos 4 e 7 do documento foram
deliberadamente ignorados, conforme orientação do grupo.

## 2. Problema

Usuários acumulam arquivos em pastas de uso intenso. A organização manual é
lenta, repetitiva e sujeita a erros: nomes duplicados, arquivos antigos que
poderiam ser arquivados, relatórios que ninguém gera e nenhuma forma simples de
desfazer uma movimentação errada.

Além disso, a automação precisa respeitar limites do sistema operacional:
permissões, espaço em disco, nomes reservados, links simbólicos e concorrência
com outros processos.

## 3. Objetivos

### Objetivo geral

Entregar um automatizador de tarefas com arquivos, multiplataforma, que
demonstre na prática conceitos de Sistemas Operacionais e possa ser usado tanto
por uma pessoa quanto por um agendador de tarefas.

### Objetivos específicos

- Planejar a organização **antes** de alterar qualquer arquivo.
- Mover arquivos para categorias configuráveis por extensão.
- Renomear arquivos em massa com padrões previsíveis.
- Arquivar arquivos antigos por ano.
- Registrar cada execução em um journal e permitir `undo`.
- Gerar relatórios em Markdown, CSV e JSON.
- Diagnosticar recursos do sistema (`doctor`).
- Automatizar a execução com scripts e agendadores.
- Garantir qualidade com testes automatizados e integração contínua.

## 4. Escopo

### Dentro do escopo (MVP)

- CLI Python 3.10+ sem dependências externas obrigatórias.
- Organização por extensão com simulação padrão.
- Filtros por padrão de nome, idade, tamanho, categoria e subdiretórios.
- Renomeação em massa e arquivamento de antigos.
- Journal em JSON e `undo` da última execução.
- Relatórios MD/CSV/JSON.
- Diagnóstico de processo, CPU, memória, disco e permissões.
- Scripts de automação para Bash e PowerShell.
- Testes unitários e de integração.
- Documentação, wiki e página web.

### Fora do escopo

- Interface gráfica desktop ou aplicativo mobile.
- Sincronização em nuvem.
- Deduplicação por hash de conteúdo.
- Banco de dados externo.
- Suporte a sistemas diferentes de Windows, Linux e macOS.

## 5. Público-alvo

- Estudantes que precisam organizar arquivos de disciplinas.
- Pessoas que baixam muitos arquivos e perdem tempo organizando pastas.
- Equipes que querem automatizar a limpeza de diretórios de trabalho.
- Professores que desejam um exemplo aplicado de automação e SO.

## 6. Funcionalidades

| Funcionalidade | Comando | Conceito de SO |
| --- | --- | --- |
| Simular organização | `organize` | Sistema de arquivos, metadados |
| Executar organização | `organize --apply` | Chamadas de sistema, I/O |
| Renomear em massa | `organize --rename` | Namespaces de arquivos |
| Arquivar antigos | `organize --archive-old` | `mtime`, organização por tempo |
| Desfazer | `undo` | Journaling e recuperação |
| Relatórios | `--report` | I/O, buffers e encoding |
| Diagnóstico | `doctor` | Processos, CPU, memória, cgroup |
| Automação | `scripts/` | Agendamento e processos |
| Configuração | `config` | Ambiente e arquivos de configuração |

## 7. Requisitos não funcionais

- **Segurança:** simulação por padrão; confirmação em operações reais; recusa
  da raiz do sistema; ignora links simbólicos; nunca sobrescreve arquivos.
- **Portabilidade:** Windows, Linux e macOS; caminhos via `pathlib`.
- **Desempenho:** varredura linear; plano em memória; sem dependências pesadas.
- **Observabilidade:** logs rotativos, journal e relatórios.
- **Testabilidade:** núcleo puro e testes por módulo.
- **Acessibilidade:** CLI com textos claros e página web responsiva.

## 8. Arquitetura resumida

```text
CLI (argparse)
   │
   ├── Configuração (JSON)
   ├── Planejador ──► Plano (operações)
   ├── Executor ────► Journal (JSON) ──► Undo
   ├── Relatórios (MD/CSV/JSON)
   └── Diagnóstico do SO
```

O planejador não altera arquivos. O executor é a única camada com permissão
para mover, renomear ou arquivar. Essa separação permite simular com segurança.

## 9. Backlog

| # | Issue | Responsável | Branch |
| --- | --- | --- | --- |
| 1 | Planejamento e requisitos | Juliana | `docs/1-planejamento` |
| 2 | Fundação do pacote | Jaquelline | `feat/2-fundacao` |
| 3 | Planejador e regras | Juliana | `feat/3-planejador` |
| 4 | Journal, executor e undo | Jaquelline | `feat/4-executor-undo` |
| 5 | Relatórios | Juliana | `feat/5-relatorios` |
| 6 | Diagnóstico do SO | Jaquelline | `feat/6-diagnostico` |
| 7 | CLI e modo interativo | Juliana | `feat/7-cli` |
| 8 | Scripts e agendamento | Jaquelline | `feat/8-automacao` |
| 9 | CI, hooks e qualidade | Juliana | `chore/9-ci-hooks` |
| 10 | Testes de integração | Jaquelline | `test/10-integracao` |
| 11 | README e documentação | Juliana | `docs/11-documentacao` |
| 12 | Wiki | Jaquelline | `docs/12-wiki` |
| 13 | Página web | Juliana | `feat/13-pagina-web` |
| 14 | Release e apresentação | Ambas | `release/v2.0.0` |

## 10. Divisão de trabalho

A divisão busca equilibrar dependências técnicas e permitir que cada integrante
consiga trabalhar de forma autônoma, com revisões cruzadas nos pontos críticos.

- **Juliana:** planejamento, planejador, relatórios, CLI, CI, documentação,
  página web e release.
- **Jaquelline:** fundação, executor/undo, diagnóstico, automação, testes de
  integração e wiki.
- **Conjunto:** definição do escopo, revisão de PRs e apresentação final.

O detalhamento está em [`DIVISAO-DE-TAREFAS.md`](DIVISAO-DE-TAREFAS.md).

## 11. Cronograma

| Etapa | Período | Entrega |
| --- | --- | --- |
| Semana 1 | Escopo e fundação | Issues 1–2 |
| Semana 2 | Núcleo | Issues 3–4 |
| Semana 3 | Recursos e interface | Issues 5–8 |
| Semana 4 | Qualidade e documentação | Issues 9–12 |
| Semana 5 | Site, release e ensaio | Issues 13–14 |

## 12. Riscos e mitigação

| Risco | Impacto | Mitigação |
| --- | --- | --- |
| Mover arquivo errado | Alto | Simulação padrão, confirmação e undo |
| Colisão de nomes | Médio | Sufixos únicos e verificação antes de mover |
| Permissão negada | Médio | Diagnóstico e mensagens claras |
| Falta de espaço | Médio | Checagem de espaço livre antes da execução |
| Diferenças entre SOs | Médio | CI em Ubuntu e Windows |
| Prazo curto | Alto | MVP priorizado e escopo congelado |

## 13. Critérios de sucesso

- A aplicação executa o fluxo completo em uma pasta de demonstração.
- Todos os testes passam em Windows e Linux.
- O `undo` restaura os arquivos de uma execução real.
- A documentação permite que uma pessoa externa reproduza o projeto.
- A apresentação cabe em 15 minutos e demonstra os conceitos de SO.

## 14. Premissas

- Python 3.10 ou superior disponível no ambiente.
- O usuário tem permissão de leitura e escrita na pasta alvo.
- O projeto é avaliado como trabalho acadêmico, sem necessidade de assinatura
  digital ou empacotamento em instalador.
