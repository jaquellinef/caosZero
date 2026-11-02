# Roteiro da apresentação — 10 a 15 minutos

## Objetivo

Demonstrar o CaosZero 2.0 como solução para o tópico **4.5. Automatizador de
Tarefas com Arquivos**, evidenciando os conceitos de Sistemas Operacionais
aplicados no código.

## Formato

- Duração alvo: **12 minutos** (margem de 3 minutos para perguntas).
- Duas apresentadoras alternando blocos.
- Demonstração ao vivo com terminal e repositório no GitHub.
- Plano B: gravação de tela ou saída salva, caso o ambiente falhe.

## Divisão de fala

| Bloco | Tempo | Quem | Conteúdo |
| --- | --- | --- | --- |
| 1. Abertura | 1 min | Juliana | Problema, proposta e organização do repositório |
| 2. Planejamento | 1 min | Juliana | Issues, backlog, branches e divisão |
| 3. Arquitetura | 2 min | Jaquelline | Módulos, fluxo e journal |
| 4. Demonstração | 4 min | Jaquelline | `demo`, `organize`, `apply`, `undo` |
| 5. Conceitos de SO | 3 min | Juliana | `doctor`, permissões, CPU, memória, cgroup |
| 6. Qualidade e automação | 1 min | Jaquelline | Testes, CI, scripts e agendamento |
| 7. Fechamento | 1 min | Juliana | Resultados, limitações e próximos passos |
| 8. Perguntas | até 3 min | Ambas | Dúvidas da banca |

---

## Bloco 1 — Abertura (1 min) — Juliana

> “Todo mundo tem uma pasta de Downloads que virou um caos. O CaosZero nasceu
> para resolver isso, mas o projeto integrador pediu mais: transformar a ideia
> em um automatizador de tarefas com arquivos, seguro, testável e capaz de
> desfazer o que fez.”

Destacar:

- Tema 4.5 do `Projeto.md`.
- Evolução do projeto original para uma CLI Python.
- Uso de issues, pull requests, branches, wiki e GitHub Pages.

## Bloco 2 — Planejamento (1 min) — Juliana

Mostrar no GitHub:

1. Aba **Issues**: 14 issues com objetivo, tarefas e critérios de aceite.
2. **Milestone** `v2.0.0 - MVP`.
3. Aba **Pull Requests**: histórico de branches e revisões.
4. Divisão: Juliana (planejamento, planejador, relatórios, CLI, CI, docs, site);
   Jaquelline (fundação, executor/undo, diagnóstico, automação, testes, wiki).

> “Cada issue virou uma branch com o número da tarefa. Cada PR foi revisado
> pela outra integrante antes do merge em `develop`.”

## Bloco 3 — Arquitetura (2 min) — Jaquelline

Explicar o diagrama:

```text
CLI → Planejador → Plano → Executor → Journal → Undo
                         └→ Relatórios
```

Pontos-chave:

- O planejador **não altera arquivos**: apenas lê metadados.
- O executor é a única camada com permissão de mover.
- O journal registra antes e depois de cada operação.
- O undo percorre as operações em ordem inversa.
- Nenhum arquivo é sobrescrito: colisões geram `(1)`, `(2)` etc.

## Bloco 4 — Demonstração (4 min) — Jaquelline

### Preparação (antes da apresentação)

```bash
cd caosZero
python caoszero.py --version
python caoszero.py demo /tmp/caoszero-demo
```

### Roteiro ao vivo

```bash
# 1. Simulação: nada é alterado
python caoszero.py organize /tmp/caoszero-demo

# 2. Execução com relatório
python caoszero.py organize /tmp/caoszero-demo --apply --report

# 3. Mostrar a árvore de diretórios
find /tmp/caoszero-demo -maxdepth 2 -type d    # Linux/macOS
tree /F /tmp/caoszero-demo                     # Windows (se disponível)

# 4. Mostrar o journal
python caoszero.py undo --list

# 5. Desfazer
python caoszero.py undo --latest

# 6. Renomear em massa
python caoszero.py organize /tmp/caoszero-demo --rename "arquivo-{seq:03d}{ext}" --rename-only --apply
```

> Dica: use `--yes` nos comandos de execução para evitar pausas.

Se o tempo estiver curto, pule a renomeação.

## Bloco 5 — Conceitos de SO (3 min) — Juliana

```bash
python caoszero.py doctor
```

Apontar na saída:

1. **Processo:** PID e PPID do processo Python.
2. **CPU:** núcleos visíveis, load average e limite de cgroup.
3. **Memória:** total, disponível e limite de cgroup.
4. **Disco:** total, usado, livre e percentual.
5. **Permissões:** modo octal e simbólico do diretório alvo.
6. **Ambiente:** variáveis que alteram o comportamento.

Relacionar com o código:

| Conceito | Arquivo |
| --- | --- |
| Processos e recursos | `system_info.py` |
| Sistema de arquivos | `planner.py`, `executor.py` |
| Permissões | `planner.py`, `utils.py` |
| Journaling | `journal.py` |
| Concorrência e colisões | `utils.unique_destination` |
| Automação | `scripts/` |

## Bloco 6 — Qualidade e automação (1 min) — Jaquelline

Mostrar:

- Aba **Actions**: CI verde em Ubuntu e Windows, Python 3.10 e 3.12.
- `python -m unittest discover -s tests -v`: 65 testes.
- `scripts/automacao.sh` e `scripts/automacao.ps1`.
- Agendamento com cron e Agendador de Tarefas.
- Hooks de pre-commit e pre-push.

> “A automação não serve só para organizar arquivos: ela também garante que o
> próprio projeto seja confiável.”

## Bloco 7 — Fechamento (1 min) — Juliana

Resultados:

- Aplicação funcional, multiplataforma e sem dependências externas.
- 14 issues, 14 branches, 14 pull requests e uma release.
- Documentação, wiki e página web.
- Conceitos de SO demonstrados na prática.

Limitações:

- Sem interface gráfica.
- Sem deduplicação por conteúdo.
- Sem sincronização em nuvem.

Próximos passos:

- Suporte a perfis de configuração.
- Modo `watch` para monitorar pastas.
- Empacotamento em executável.

## Bloco 8 — Perguntas (até 3 min) — Ambas

### Perguntas prováveis e respostas

**O que acontece se o programa cair no meio da execução?**
O journal é salvo após cada operação. As operações já concluídas permanecem
registradas e podem ser desfeitas com `undo`.

**Como vocês garantem que nenhum arquivo é perdido?**
Simulação por padrão, confirmação, verificação de destino, nomes únicos e undo.
Nada é sobrescrito ou apagado.

**Por que não usar uma biblioteca de terceiros?**
Para demonstrar domínio da biblioteca padrão e facilitar a execução em qualquer
ambiente da disciplina, sem instalação extra.

**Qual é o conceito de SO mais importante do projeto?**
O journaling aliado ao sistema de arquivos: ele permite recuperar o estado e
desfazer operações, algo essencial em sistemas reais.

**Como o projeto lida com permissões?**
O `doctor` mostra o modo octal/simbólico e o planejador avisa quando não há
permissão de escrita. O executor reporta falhas por operação.

**O projeto funcionaria em um contêiner?**
Sim. O `doctor` lê limites de cgroup de CPU e memória, e a aplicação não exige
privilégios especiais.

**Qual foi o maior desafio?**
Evitar colisões e garantir que o undo fosse seguro sem sobrescrever arquivos.

## Checklist da apresentação

### Antes

- [ ] Repositório atualizado e CI verde.
- [ ] Python 3.10+ disponível no computador da apresentação.
- [ ] Sandbox criado em local conhecido.
- [ ] Terminal com fonte legível e histórico limpo.
- [ ] Abas abertas: README, Issues, Actions, Wiki, GitHub Pages.
- [ ] Plano B: vídeo ou saída salva.

### Durante

- [ ] Falar pausadamente e alternar as apresentadoras.
- [ ] Mostrar a saída real, não apenas slides.
- [ ] Destacar a segurança (simulação e undo).
- [ ] Relacionar cada comando a um conceito de SO.

### Depois

- [ ] Deixar o repositório público e a release disponível.
- [ ] Responder às perguntas com exemplos do código.
- [ ] Registrar feedback para a próxima versão.
