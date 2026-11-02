# Conceitos de Sistemas Operacionais no CaosZero

Este documento conecta a teoria da disciplina ao código do projeto. Cada seção
indica onde o conceito aparece e como demonstrá-lo na apresentação.

---

## 1. Sistema de arquivos

### Teoria

O sistema de arquivos é a abstração do SO para armazenar e recuperar dados.
Ele organiza bytes em **arquivos**, agrupa arquivos em **diretórios** e mantém
**metadados** (nome, tamanho, datas, permissões, proprietário, inode).

### No CaosZero

- `planner.py` percorre diretórios com `Path.iterdir()` e `os.walk()`.
- `config.py` associa extensões a categorias.
- `executor.py` usa `shutil.move()` para mover arquivos.
- `utils.py` usa `Path.suffix`, `Path.suffixes` e `Path.with_name()`.

### Demonstração

```bash
python caoszero.py demo
python caoszero.py organize sandbox_teste
```

O plano mostra a origem, o destino e o motivo de cada operação — tudo derivado
de metadados do sistema de arquivos.

---

## 2. Chamadas de sistema e entrada/saída

### Teoria

Aplicações em espaço de usuário pedem serviços ao kernel por meio de chamadas
de sistema: `open`, `read`, `write`, `stat`, `rename`, `mkdir`, `unlink`. O
kernel valida permissões, atualiza metadados e faz o buffering.

### No CaosZero

| Operação | Chamada típica |
| --- | --- |
| Ler um arquivo | `open` / `read` |
| Consultar metadados | `stat` / `lstat` |
| Criar diretório | `mkdir` |
| Mover/renomear | `rename` (ou copiar + remover entre dispositivos) |
| Gravar journal | `open` / `write` / `fsync` |

Python encapsula essas chamadas em `pathlib`, `os` e `shutil`. O journal é
gravado de forma incremental para reduzir a janela de perda de dados.

### Demonstração

Execute `organize --apply` e observe o arquivo JSON criado em
`<estado>/runs/`. Cada operação registra origem, destino, tamanho, status e
eventual erro.

---

## 3. Processos

### Teoria

Um processo é um programa em execução, com PID, espaço de endereçamento,
descritores de arquivo e estado. Processos podem criar outros processos
(`fork`/`exec` no POSIX, `CreateProcess` no Windows).

### No CaosZero

O comando `doctor` mostra:

- **PID** do processo atual;
- **PPID** (processo pai);
- usuário efetivo;
- número de threads ativas;
- executável do interpretador Python;
- uptime do sistema.

Os scripts de automação iniciam um novo processo Python a cada execução. O
agendador (cron ou Agendador de Tarefas) é quem cria esse processo.

### Demonstração

```bash
python caoszero.py doctor
```

Compare o PID exibido com o PID do shell que executou o comando.

---

## 4. Gerência de CPU

### Teoria

O SO escala processos e threads entre núcleos, aplica prioridades e, em
contêineres, respeita limites de CPU via cgroups. O **load average** (POSIX)
resume a demanda por CPU.

### No CaosZero

- `os.cpu_count()` retorna os núcleos visíveis.
- `os.getloadavg()` retorna o load average (quando disponível).
- `system_info.py` lê `/sys/fs/cgroup/cpu.max` para detectar limites de
  contêiner.
- O número efetivo de núcleos é `min(núcleos visíveis, limite do cgroup)`.

### Demonstração

```bash
python caoszero.py doctor --json
```

Em um contêiner, o limite de cgroup pode ser menor que o número de núcleos da
máquina física.

---

## 5. Gerência de memória

### Teoria

O SO gerencia memória física e virtual, paginação e proteção. Em contêineres,
o cgroup impõe um limite de memória. É comum o processo ver menos memória do que
a máquina possui.

### No CaosZero

- Windows: `GlobalMemoryStatusEx` via `ctypes`.
- Linux: leitura de `/proc/meminfo` (`MemTotal`, `MemAvailable`).
- macOS: `sysctl -n hw.memsize`.
- Cgroup: `/sys/fs/cgroup/memory.max` ou `memory.limit_in_bytes`.

O diagnóstico é usado para avaliar se há memória suficiente para varrer
diretórios muito grandes.

---

## 6. Gerência de disco

### Teoria

O SO organiza o armazenamento em blocos e sistemas de arquivos. `statvfs` /
`GetDiskFreeSpaceEx` informam espaço total, usado e livre. Pouco espaço livre
pode causar falhas de escrita e corrupção.

### No CaosZero

- `shutil.disk_usage()` calcula total, usado e livre.
- `planner.py` compara o espaço livre com `min_free_mb` da configuração.
- O plano emite aviso quando o espaço está abaixo do limite de segurança.
- O planejamento não move arquivos para outro dispositivo sem necessidade.

### Demonstração

```bash
python caoszero.py doctor ~/Downloads
```

Observe o percentual usado e o espaço livre antes de uma organização grande.

---

## 7. Permissões e controle de acesso

### Teoria

Cada arquivo tem um proprietário, um grupo e bits de permissão. No POSIX, o
modo é representado em octal (`0644`, `0755`). O Windows usa ACLs, mas o Python
expõe uma visão simplificada.

### No CaosZero

- `doctor` mostra modo octal e simbólico (`-rw-r--r--`).
- `os.access()` verifica leitura, escrita e execução.
- O planejador avisa quando o alvo não tem permissão de escrita.
- O executor cria diretórios com as permissões padrão do processo.

### Demonstração

```bash
python caoszero.py doctor
python caoszero.py organize /caminho/sem/permissao
```

No segundo caso, a validação e o aviso aparecem antes de qualquer alteração.

---

## 8. Concorrência e colisões

### Teoria

Dois processos podem tentar criar o mesmo arquivo ao mesmo tempo. O SO garante
atomicidade de `rename` dentro do mesmo sistema de arquivos, mas a aplicação
precisa lidar com destinos já existentes.

### No CaosZero

- O planejador reserva destinos em um `set` e gera nomes únicos.
- O executor verifica novamente antes de mover; se o destino surgiu no meio do
  caminho, gera outro nome.
- Arquivos nunca são sobrescritos.
- Links simbólicos são ignorados.

### Demonstração

O sandbox do `demo` já contém `Imagens/foto_ferias.jpg` e um arquivo
`foto_ferias.jpg` na raiz, forçando uma colisão. O plano mostra o sufixo `(1)`.

---

## 9. Agendamento e automação

### Teoria

O SO oferece mecanismos para executar tarefas sem intervenção humana: `cron` e
`systemd timers` no Linux, Agendador de Tarefas no Windows. Eles criam processos
em horários definidos, com contexto de usuário e ambiente próprios.

### No CaosZero

- `scripts/agendar_cron.sh` registra uma entrada de crontab.
- `scripts/agendar_tarefa.ps1` cria uma tarefa diária no Windows.
- Ambos usam caminhos absolutos para Python e para o projeto.
- Sem `--apply`/`-Register`, apenas mostram o que seria feito.

### Demonstração

```bash
./scripts/agendar_cron.sh --target ~/Downloads --time 09:00
```

O script imprime a linha de crontab sem alterar nada.

---

## 10. Tolerância a falhas e journaling

### Teoria

Sistemas de arquivos journaling registram operações antes de aplicá-las,
permitindo recuperação após queda. A ideia é semelhante em aplicações: registrar
intenção e resultado para poder reconstruir o estado.

### No CaosZero

- O journal é salvo antes da primeira operação e após cada operação.
- Cada operação tem status independente.
- O `undo` percorre as operações concluídas em ordem inversa.
- Se uma restauração falha, as demais continuam.
- O journal nunca é sobrescrito por outra execução.

### Demonstração

```bash
python caoszero.py organize sandbox_teste --apply --report
python caoszero.py undo --list
python caoszero.py undo --latest
```

---

## 11. Interface de linha de comando

### Teoria

A CLI é uma interface baseada em texto. O processo lê `argv`, variáveis de
ambiente e arquivos de configuração, e devolve um **código de saída** que pode
ser usado por scripts.

### No CaosZero

- `argparse` define subcomandos e valida argumentos.
- Variáveis `CAOSZERO_*` alteram o comportamento.
- Códigos de saída: `0` sucesso, `1` erro, `2` cancelado, `130` interrompido.
- `--json` permite integração com outras ferramentas.

---

## 12. Resumo para a apresentação

| Conceito | Comando | O que mostrar |
| --- | --- | --- |
| Sistema de arquivos | `organize` | Prévia com origem e destino |
| Chamadas de sistema | `organize --apply` | Journal JSON gerado |
| Processos | `doctor` | PID, PPID, threads |
| CPU | `doctor` | Núcleos, load, cgroup |
| Memória | `doctor` | Total, disponível, cgroup |
| Disco | `doctor` | Total, usado, livre |
| Permissões | `doctor` | Modo octal e simbólico |
| Concorrência | `demo` + `organize` | Colisão resolvida com `(1)` |
| Automação | `scripts/` | Cron e Agendador |
| Tolerância a falhas | `undo` | Restauração da execução |
