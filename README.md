# CaosZero 2.0

**Automatizador de tarefas com arquivos** — projeto integrador da disciplina de
**Sistemas Operacionais**.

O CaosZero organiza pastas por categoria, renomeia arquivos em massa, arquiva
itens antigos, gera relatórios e permite **desfazer** a última execução. Tudo
pela linha de comando, sem dependências externas obrigatórias.

[![CI](https://github.com/julianasaunders/caosZero/actions/workflows/ci.yml/badge.svg)](https://github.com/julianasaunders/caosZero/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Licença MIT](https://img.shields.io/badge/licen%C3%A7a-MIT-green.svg)](LICENSE)

> **Segurança em primeiro lugar:** por padrão o CaosZero apenas **simula** a
> organização. Nenhum arquivo é alterado sem a opção `--apply`.

---

## Sumário

- [Demonstração rápida](#demonstração-rápida)
- [Funcionalidades](#funcionalidades)
- [Instalação](#instalação)
- [Comandos](#comandos)
- [Como funciona](#como-funciona)
- [Conceitos de Sistemas Operacionais](#conceitos-de-sistemas-operacionais)
- [Automação e agendamento](#automação-e-agendamento)
- [Configuração](#configuração)
- [Testes](#testes)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Documentação](#documentação)
- [Comunidade e segurança](#comunidade-e-segurança)
- [Equipe](#equipe)
- [Licença](#licença)

---

## Demonstração rápida

```bash
# 1. Crie uma pasta de demonstração com arquivos variados
python caoszero.py demo

# 2. Veja o que seria feito (simulação, nada é alterado)
python caoszero.py organize sandbox_teste

# 3. Organize de verdade e gere um relatório
python caoszero.py organize sandbox_teste --apply --report

# 4. Desfaça a última execução
python caoszero.py undo --latest

# 5. Veja o diagnóstico do sistema operacional
python caoszero.py doctor
```

Exemplo de saída da simulação:

```text
Alvo: C:\Users\voce\sandbox_teste
Arquivos analisados: 16
Operações planejadas: 13 (1.2 KB)
Ignorados: 5

Prévia das operações:
  [MOVER   ] backup_projeto.zip -> Compactados\backup_projeto.zip
  [MOVER   ] captura_tela.png -> Imagens\captura_tela.png
  [MOVER   ] dados.csv -> Planilhas\dados.csv
  [MOVER   ] documento_antigo.pdf -> Documentos\documento_antigo.pdf
  ...
```

---

## Funcionalidades

- **Organização por extensão** com categorias configuráveis.
- **Simulação segura** (`dry-run`) por padrão.
- **Filtros**: glob, idade, tamanho, categoria, subdiretórios e ocultos.
- **Renomeação em massa** com `{name}`, `{ext}`, `{seq}`, `{date}` e `{categoria}`.
- **Arquivamento de antigos** em `Arquivo/AAAA/`.
- **Journal em JSON** de cada execução.
- **Undo** da última execução (ou de um ID específico).
- **Relatórios** em Markdown, CSV e JSON.
- **Diagnóstico do SO** (`doctor`): processo, CPU, memória, disco, permissões,
  variáveis de ambiente e limites de cgroup.
- **Modo interativo** para apresentações.
- **Scripts** de automação para Bash e PowerShell.
- **Sem dependências externas** para executar.

---

## Instalação

### Requisitos

- Python **3.10** ou superior.
- Windows, Linux ou macOS.

### Opção 1 — usar direto do repositório

```bash
git clone https://github.com/julianasaunders/caosZero.git
cd caosZero
python caoszero.py --help
```

### Opção 2 — instalar como pacote

```bash
python -m pip install .
caoszero --help
```

### Opção 3 — ambiente virtual (recomendado)

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

Windows (PowerShell):

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

> Se `python` não estiver no PATH, use o caminho completo do interpretador ou o
> launcher `py -3` no Windows.

---

## Comandos

### `organize`

Planeja ou executa a organização de uma pasta.

```bash
python caoszero.py organize [ALVO] [opções]
```

| Opção | Descrição |
| --- | --- |
| `--apply` | Executa de verdade (sem isso, apenas simula) |
| `-r`, `--recursive` | Inclui subdiretórios |
| `--hidden` | Inclui arquivos ocultos |
| `--pattern "*.pdf"` | Filtra por padrão glob |
| `--older-than 30` | Somente arquivos com mais de 30 dias |
| `--archive-old 180` | Move arquivos com 180+ dias para `Arquivo/AAAA` |
| `--rename "arquivo-{seq:03d}{ext}"` | Renomeia durante a organização |
| `--rename-only` | Renomeia no lugar, sem criar categorias |
| `--category Imagens` | Restringe a uma categoria |
| `--min-size 10KB` | Tamanho mínimo |
| `--max-size 2GB` | Tamanho máximo |
| `--report [ARQUIVO]` | Gera relatório (sem valor: automático em Markdown) |
| `--json` | Saída JSON para automação |
| `-y`, `--yes` | Não pede confirmação |
| `-v`, `--verbose` | Log detalhado |
| `--config ARQUIVO` | Configuração JSON alternativa |

Exemplos:

```bash
# Simular organização de Downloads
python caoszero.py organize ~/Downloads

# Organizar somente PDFs com mais de 90 dias
python caoszero.py organize . --pattern "*.pdf" --older-than 90 --apply

# Arquivar arquivos antigos e organizar o restante
python caoszero.py organize . --archive-old 180 --apply

# Renomear fotos em massa, mantendo-as no lugar
python caoszero.py organize ./fotos --rename "IMG-{seq:04d}{ext}" --rename-only --apply

# Gerar relatório CSV
python caoszero.py organize ./dados --apply --report relatorio.csv
```

### `undo`

Desfaz uma execução registrada no journal.

```bash
python caoszero.py undo --list          # lista execuções
python caoszero.py undo --latest        # desfaz a última
python caoszero.py undo 20261102-101500-a1b2c3
python caoszero.py undo --dry-run       # mostra o que seria restaurado
```

### `doctor`

Mostra recursos do sistema operacional usados pela aplicação.

```bash
python caoszero.py doctor
python caoszero.py doctor --json
python caoszero.py doctor ~/Downloads
```

### `config`

```bash
python caoszero.py config --show        # configuração efetiva
python caoszero.py config --path        # caminho do arquivo
python caoszero.py config --init        # cria configuração de exemplo
python caoszero.py config --init ./minha-config.json
```

### `demo`

Cria uma pasta com arquivos variados (inclusive antigos, ocultos e com colisão
de nomes) para testar sem risco.

```bash
python caoszero.py demo
python caoszero.py demo ./minha-demo
```

### `interactive`

Menu guiado, útil para apresentações.

```bash
python caoszero.py interactive
```

### Códigos de saída

| Código | Significado |
| --- | --- |
| `0` | Sucesso |
| `1` | Erro de validação ou falha em operações |
| `2` | Operação cancelada pelo usuário |
| `130` | Interrompido com `Ctrl+C` |

---

## Como funciona

O fluxo é dividido em quatro etapas:

```text
1. Planejar  →  lê metadados e calcula destinos (não altera nada)
2. Confirmar →  mostra a prévia e pede confirmação (ou usa --yes)
3. Executar  →  move/renomeia e grava cada passo no journal
4. Relatar   →  gera MD/CSV/JSON e permite undo
```

O **planejador** nunca toca nos arquivos. O **executor** é a única camada que
move, renomeia ou arquiva. Essa separação é o que torna a simulação confiável.

Antes de mover, o CaosZero verifica:

- se a origem ainda existe e não é um link simbólico;
- se o destino já existe (nesse caso, gera um nome único);
- se há espaço livre suficiente no disco;
- se o diretório alvo permite escrita.

Cada operação é registrada no journal **antes e depois** de ser executada, o
que permite recuperar o histórico mesmo se o processo for interrompido.

---

## Conceitos de Sistemas Operacionais

O projeto demonstra, de forma aplicada:

| Conceito | Onde aparece |
| --- | --- |
| **Sistema de arquivos** | Varredura, categorias e movimentação de arquivos |
| **Chamadas de sistema e I/O** | `open`, `stat`, `rename`, `mkdir`, journals e relatórios |
| **Processos** | PID, PPID, threads, uptime e execução por agendador |
| **Gerência de CPU** | Núcleos, load average e limites de cgroup |
| **Gerência de memória** | Memória total/disponível e limites de cgroup |
| **Gerência de disco** | Espaço livre, uso percentual e verificação antes da execução |
| **Permissões** | Modo octal/simbólico e teste de leitura/escrita/execução |
| **Concorrência** | Colisões de nomes e destinos únicos |
| **Automação** | Scripts, cron e Agendador de Tarefas |
| **Tolerância a falhas** | Journal, status por operação e undo |

Detalhes em [`docs/CONCEITOS-SO.md`](docs/CONCEITOS-SO.md).

---

## Automação e agendamento

### Linux/macOS

```bash
chmod +x scripts/*.sh
./scripts/automacao.sh                                  # simula ~/Downloads
./scripts/automacao.sh --apply --report                 # executa e relata
./scripts/automacao.sh --target ~/Downloads --doctor    # diagnóstico

# Agendar diariamente às 09:00
./scripts/agendar_cron.sh --target ~/Downloads --time 09:00 --apply
```

### Windows (PowerShell)

```powershell
.\scripts\automacao.ps1
.\scripts\automacao.ps1 -Apply -Report
.\scripts\automacao.ps1 -Target "$HOME\Downloads" -Doctor

# Agendar diariamente às 09:00
.\scripts\agendar_tarefa.ps1 -Target "$HOME\Downloads" -Time "09:00" -Register
```

Os scripts de agendamento **não registram nada** sem `--apply`/`-Register`.

---

## Configuração

A configuração é procurada nesta ordem:

1. `--config CAMINHO`
2. variável `CAOSZERO_CONFIG`
3. `<CAOSZERO_HOME>/config.json`
4. valores padrão embutidos

O diretório de estado (journal, logs e relatórios) segue o padrão do sistema:

| Sistema | Caminho padrão |
| --- | --- |
| Linux/macOS | `~/.local/share/caoszero` |
| Windows | `%LOCALAPPDATA%\CaosZero` |
| Qualquer | `CAOSZERO_HOME` (tem precedência) |

Variáveis de ambiente:

| Variável | Efeito |
| --- | --- |
| `CAOSZERO_HOME` | Diretório de estado |
| `CAOSZERO_CONFIG` | Arquivo de configuração |
| `CAOSZERO_TARGET` | Diretório alvo padrão |
| `CAOSZERO_PYTHON` | Interpretador usado pelos scripts |

Exemplo de configuração:

```json
{
  "categories": {
    "Documentos": [".pdf", ".docx", ".txt", ".md"],
    "Imagens": [".jpg", ".png", ".gif"],
    "Outros": []
  },
  "ignore_names": [".DS_Store", "Thumbs.db"],
  "ignore_globs": ["*.tmp", "*.part"],
  "ignore_dirs": [".git", "node_modules", "__pycache__"],
  "archive_dir": "Arquivo",
  "report_dir": "reports",
  "min_free_mb": 50
}
```

Consulte [`config/caoszero.example.json`](config/caoszero.example.json).

---

## Testes

```bash
python -m unittest discover -s tests -v
```

O projeto usa apenas a biblioteca padrão do Python. Os testes cobrem
configuração, utilitários, planejador, executor, journal, undo, relatórios,
diagnóstico e a CLI ponta a ponta.

```bash
# Executar um módulo específico
python -m unittest tests.test_planner -v

# Validação rápida do ambiente
./scripts/verificar.sh       # Linux/macOS
.\scripts\verificar.ps1      # Windows
```

Detalhes em [`docs/TESTES.md`](docs/TESTES.md).

---

## Estrutura do projeto

```text
caosZero/
├── caoszero.py                 # atalho para executar sem instalar
├── pyproject.toml              # metadados e entrypoint
├── src/caoszero/
│   ├── cli.py                  # interface de linha de comando
│   ├── config.py               # configuração e diretórios padrão
│   ├── planner.py              # planejamento (sem efeitos colaterais)
│   ├── executor.py             # execução e undo
│   ├── journal.py              # persistência das execuções
│   ├── reporter.py             # relatórios MD/CSV/JSON
│   ├── system_info.py          # diagnóstico do SO
│   ├── models.py               # modelos de domínio
│   ├── utils.py                # utilitários
│   └── demo.py                 # sandbox de demonstração
├── tests/                      # testes automatizados
├── scripts/                    # automação, agendamento e hooks
├── config/                     # configuração de exemplo
├── docs/                       # documentação e roteiro da apresentação
├── .github/                    # CI, templates e CODEOWNERS
├── index.html                  # página do projeto (GitHub Pages)
└── README.md
```

---

## Documentação

| Documento | Conteúdo |
| --- | --- |
| [Planejamento](docs/PLANEJAMENTO.md) | Escopo, backlog, riscos e cronograma |
| [Arquitetura](docs/ARQUITETURA.md) | Módulos, fluxo de dados e decisões |
| [Conceitos de SO](docs/CONCEITOS-SO.md) | Teoria aplicada ao código |
| [Guia de uso](docs/GUIA-DE-USO.md) | Cenários passo a passo |
| [Testes](docs/TESTES.md) | Estratégia, cobertura e como rodar |
| [Apresentação](docs/APRESENTACAO.md) | Roteiro de 10 a 15 minutos |
| [Divisão de tarefas](docs/DIVISAO-DE-TAREFAS.md) | Responsabilidades e histórico |
| [Contribuição](CONTRIBUTING.md) | Branches, commits, PRs e revisão |
| [Código de conduta](CODE_OF_CONDUCT.md) | Convivência e colaboração |
| [Segurança](SECURITY.md) | Relato de vulnerabilidades e garantias |
| [Changelog](CHANGELOG.md) | Histórico de versões |

A wiki do projeto está em
<https://github.com/julianasaunders/caosZero/wiki>.

---

## Comunidade e segurança

- **Contribuições:** leia o [guia de contribuição](CONTRIBUTING.md) antes de
  abrir uma issue ou pull request.
- **Convivência:** todas as interações seguem o
  [Código de Conduta](CODE_OF_CONDUCT.md).
- **Vulnerabilidades:** não abra issues públicas com detalhes exploráveis. Use
  o canal privado descrito na [Política de Segurança](SECURITY.md).

O CaosZero foi projetado para reduzir riscos: simulação por padrão, nenhuma
sobrescrita, nenhuma exclusão, recusa da raiz do sistema e undo baseado em
journal.

---

## Equipe

| Integrante | GitHub |
| --- | --- |
| Juliana Saunders | [@julianasaunders](https://github.com/julianasaunders) |
| Jaquelline Feitoza | [@jaquellinef](https://github.com/jaquellinef) |

Orientação: disciplina de **Sistemas Operacionais**.

---

## Licença

Distribuído sob a licença **MIT**. Veja [`LICENSE`](LICENSE).
