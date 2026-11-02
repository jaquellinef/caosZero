# Conceitos de Sistemas Operacionais

| Conceito | Onde aparece | Como demonstrar |
| --- | --- | --- |
| Sistema de arquivos | `planner.py`, `executor.py` | `organize` |
| Chamadas de sistema | `journal.py`, `reporter.py` | Journal e relatórios |
| Processos | `system_info.py` | `doctor` (PID, PPID, threads) |
| CPU | `system_info.py` | `doctor` (núcleos, load, cgroup) |
| Memória | `system_info.py` | `doctor` (total, disponível, cgroup) |
| Disco | `planner.py`, `system_info.py` | Aviso de espaço e `doctor` |
| Permissões | `system_info.py`, `planner.py` | Modo octal e simbólico |
| Concorrência | `utils.py`, `executor.py` | Colisão resolvida com `(1)` |
| Automação | `scripts/` | cron e Agendador de Tarefas |
| Tolerância a falhas | `journal.py`, `executor.py` | `undo` |

## Explicação resumida

### Sistema de arquivos

Arquivos, diretórios e metadados. O CaosZero lê `stat`, calcula destinos e usa
`rename`/`move` para reorganizar.

### Processos

Cada execução é um processo Python com PID, PPID e threads. O agendador cria
novos processos em horários definidos.

### Memória e CPU

O `doctor` mostra recursos visíveis e limites de cgroup, relevantes em
contêineres.

### Permissões

O modo octal (`0644`) e simbólico (`-rw-r--r--`) indicam quem pode ler, escrever
e executar. O planejador avisa quando falta permissão de escrita.

### Journaling

Registrar a intenção antes de executar permite recuperação e undo, ideia
semelhante à de sistemas de arquivos journaling.

Detalhes em
[CONCEITOS-SO.md](https://github.com/julianasaunders/caosZero/blob/main/docs/CONCEITOS-SO.md).

Voltar para [Home](Home).
