# Guia de uso

Cenários passo a passo para usar o CaosZero com segurança.

## Antes de começar

1. Tenha o Python 3.10+ instalado.
2. Clone o repositório ou instale o pacote (`python -m pip install .`).
3. Confirme que a CLI responde:

```bash
python caoszero.py --version
python caoszero.py --help
```

> Todos os exemplos usam `python caoszero.py`. Se você instalou o pacote, pode
> trocar por `caoszero`.

---

## Cenário 1 — Primeira organização com segurança

### Passo 1: criar um sandbox

```bash
python caoszero.py demo
```

Isso cria `sandbox_teste/` com documentos, imagens, vídeos, arquivos antigos,
um arquivo oculto e uma colisão proposital.

### Passo 2: simular

```bash
python caoszero.py organize sandbox_teste
```

Nada é alterado. Observe:

- arquivos analisados;
- operações planejadas;
- arquivos ignorados e o motivo;
- prévia origem → destino.

### Passo 3: executar

```bash
python caoszero.py organize sandbox_teste --apply --report
```

A CLI pede confirmação. Use `--yes` para automação.

### Passo 4: conferir o relatório

O caminho aparece no final da execução. Abra o Markdown e verifique a tabela de
operações.

### Passo 5: desfazer

```bash
python caoszero.py undo --latest
```

Os arquivos voltam para as posições originais.

---

## Cenário 2 — Organizar Downloads por categoria

```bash
# Simulação
python caoszero.py organize ~/Downloads

# Execução com relatório automático
python caoszero.py organize ~/Downloads --apply --report
```

Se houver muitos arquivos, o plano pode levar alguns segundos. O CaosZero não
entra em subpastas por padrão.

Para incluir subpastas:

```bash
python caoszero.py organize ~/Downloads --recursive --apply
```

---

## Cenário 3 — Arquivar somente arquivos antigos

```bash
python caoszero.py organize ~/Documentos --older-than 365 --archive-old 365 --apply
```

O resultado é:

```text
Documentos/
└── Arquivo/
    ├── 2024/
    └── 2025/
```

> Use `--archive-old` para mover os antigos e organizar o restante, ou combine
> com `--older-than` para afetar **somente** os antigos.

---

## Cenário 4 — Renomear fotos em massa

```bash
python caoszero.py organize ~/Fotos --rename "viagem-{seq:03d}{ext}" --rename-only
```

Prévia:

```text
[MOVER   ] IMG_001.jpg -> IMG_001.jpg   (se já estiver no lugar, é ignorado)
```

Para aplicar:

```bash
python caoszero.py organize ~/Fotos --rename "viagem-{seq:03d}{ext}" --rename-only --apply
```

Tokens disponíveis:

| Token | Significado | Exemplo |
| --- | --- | --- |
| `{name}` / `{stem}` | Nome sem extensão | `relatorio` |
| `{ext}` | Extensão com ponto | `.pdf` |
| `{extensao}` | Extensão sem ponto | `pdf` |
| `{seq}` | Sequência | `1`, `2`, `3` |
| `{seq:03d}` | Sequência formatada | `001` |
| `{date}` / `{data}` | Data de modificação | `2026-11-02` |
| `{categoria}` | Categoria detectada | `Imagens` |

---

## Cenário 5 — Filtrar por tipo e tamanho

```bash
# Somente PDFs
python caoszero.py organize . --pattern "*.pdf"

# Imagens entre 1 MB e 10 MB
python caoszero.py organize ./midias --category Imagens --min-size 1MB --max-size 10MB

# Arquivos grandes, com mais de 30 dias
python caoszero.py organize . --min-size 100MB --older-than 30
```

---

## Cenário 6 — Relatórios para planilha

```bash
python caoszero.py organize ./dados --apply --report relatorio.csv
```

O CSV usa `;` como separador e UTF-8 com BOM, para abrir corretamente no Excel
em português.

Para JSON:

```bash
python caoszero.py organize ./dados --apply --report relatorio.json
```

Para integrar com outro programa:

```bash
python caoszero.py organize ./dados --json > saida.json
```

---

## Cenário 7 — Automação diária

### Linux/macOS

```bash
chmod +x scripts/*.sh

# Testa o ambiente
./scripts/test_ambiente.sh

# Simula
./scripts/automacao.sh --target ~/Downloads

# Executa
./scripts/automacao.sh --target ~/Downloads --apply --report

# Agenda todos os dias às 09:00
./scripts/agendar_cron.sh --target ~/Downloads --time 09:00 --apply
```

### Windows

```powershell
.\scripts\test_ambiente.ps1
.\scripts\automacao.ps1 -Target "$HOME\Downloads"
.\scripts\automacao.ps1 -Target "$HOME\Downloads" -Apply -Report
.\scripts\agendar_tarefa.ps1 -Target "$HOME\Downloads" -Time "09:00" -Register
```

---

## Cenário 8 — Apresentação

```bash
python caoszero.py demo
python caoszero.py organize sandbox_teste
python caoszero.py organize sandbox_teste --apply --report
python caoszero.py undo --latest
python caoszero.py doctor
python caoszero.py interactive
```

O modo interativo evita digitar comandos longos durante a demonstração.

---

## Configuração personalizada

Crie um arquivo:

```bash
python caoszero.py config --init ./minha-config.json
```

Edite as categorias e use:

```bash
python caoszero.py organize . --config ./minha-config.json
```

Ou defina permanentemente:

```bash
export CAOSZERO_CONFIG=~/minha-config.json     # Linux/macOS
$env:CAOSZERO_CONFIG = "$HOME\minha-config.json"  # PowerShell
```

---

## Perguntas frequentes

### O CaosZero apaga arquivos?

Não. Ele move, renomeia e arquiva. Arquivos ignorados permanecem onde estão.

### O que acontece se o destino já existir?

Um nome único é gerado: `foto.jpg` → `foto (1).jpg`. Nada é sobrescrito.

### Posso desfazer qualquer execução?

Sim, desde que o journal ainda exista e os arquivos não tenham sido movidos
manualmente. Use `undo --list` para ver as execuções disponíveis.

### O que é o diretório de estado?

É onde ficam journal, logs e relatórios. No Linux/macOS:
`~/.local/share/caoszero`; no Windows: `%LOCALAPPDATA%\CaosZero`.

### Links simbólicos são seguidos?

Não. Por segurança, links são ignorados pelo planejador e recusados pelo
executor.

### Posso organizar a raiz do sistema?

Não. O CaosZero recusa explicitamente `/` e `C:\`.

### Como limpar o estado?

Apague o diretório de estado. Isso remove journals e logs, mas **não** desfaz
execuções já realizadas.

```bash
rm -rf ~/.local/share/caoszero          # Linux/macOS
Remove-Item -Recurse "$env:LOCALAPPDATA\CaosZero"  # Windows
```

---

## Solução de problemas

| Problema | Causa provável | Solução |
| --- | --- | --- |
| `python` não encontrado | Python fora do PATH | Use `py -3` ou caminho completo |
| `Permission denied` | Sem permissão na pasta | Ajuste permissões ou escolha outra pasta |
| `JSON inválido` | Configuração malformada | Valide com `python caoszero.py config --show` |
| Nada é organizado | Filtros muito restritivos | Remova `--pattern`, `--older-than` etc. |
| Undo falha | Origem ocupada ou destino ausente | Verifique o journal e restaure manualmente |
| Execução lenta | Muitos arquivos ou rede | Use uma pasta local e execute por partes |
