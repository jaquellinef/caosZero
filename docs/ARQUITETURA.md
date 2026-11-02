# Arquitetura do CaosZero

## Visão geral

O CaosZero é uma aplicação de linha de comando escrita em Python 3.10+, sem
dependências externas obrigatórias. A arquitetura separa **planejamento**,
**execução** e **observação** para que a simulação seja confiável e o undo seja
possível.

```text
┌─────────────────────────────────────────────────────────────┐
│                         CLI (argparse)                      │
│  organize │ undo │ doctor │ config │ demo │ interactive     │
└───────┬───────────────┬──────────────┬──────────────────────┘
        │               │              │
        ▼               ▼              ▼
┌──────────────┐ ┌─────────────┐ ┌────────────────┐
│  Configuração │ │ Planejador  │ │ Diagnóstico SO │
│  (JSON)       │ │ (somente    │ │ (processo,     │
│               │ │  leitura)   │ │  CPU, memória) │
└───────┬──────┘ └──────┬──────┘ └────────────────┘
        │               │
        │               ▼
        │        ┌─────────────┐
        │        │    Plano    │
        │        │ (operações) │
        │        └──────┬──────┘
        │               │
        ▼               ▼
┌──────────────────────────────┐
│           Executor           │
│  move / renomeia / arquiva   │
└──────────────┬───────────────┘
               │
      ┌────────┴────────┐
      ▼                 ▼
┌───────────┐    ┌─────────────┐
│  Journal  │    │ Relatórios  │
│  (JSON)   │    │ MD/CSV/JSON │
└─────┬─────┘    └─────────────┘
      │
      ▼
┌───────────┐
│   Undo    │
└───────────┘
```

## Módulos

| Módulo | Responsabilidade | Efeitos colaterais |
| --- | --- | --- |
| `cli.py` | Parse de argumentos, confirmação, saída e códigos de retorno | Nenhum (delega) |
| `config.py` | Carregar/validar JSON, resolver diretórios padrão | Leitura de arquivo |
| `models.py` | `Action`, `Status`, `Operation`, `Run`, `SkippedFile` | Nenhum |
| `planner.py` | Varredura, filtros, categorias, colisões, renomeação | Nenhum |
| `executor.py` | Executar o plano e desfazer | Move arquivos |
| `journal.py` | Persistir e recuperar execuções | Escrita atômica |
| `reporter.py` | Gerar MD, CSV e JSON | Escrita de relatório |
| `system_info.py` | Coletar recursos do SO | Leitura do sistema |
| `logging_setup.py` | Log rotativo em `caoszero.log` | Escrita de log |
| `utils.py` | Tamanhos, nomes, padrões, caminhos | Nenhum |
| `demo.py` | Criar sandbox de demonstração | Escrita em pasta temporária |

## Fluxo de dados

### 1. Planejamento

```text
alvo + configuração + opções
        │
        ▼
varredura (os.walk / iterdir)
        │
        ▼
filtros (ocultos, ignorados, padrão, idade, tamanho, categoria)
        │
        ▼
categoria por extensão (mais específica vence: .tar.gz > .gz)
        │
        ▼
cálculo do destino + resolução de colisão
        │
        ▼
Plano (operações + ignorados + avisos)
```

O planejador é **puro**: não cria diretórios, não move arquivos e não grava
nada. Ele apenas lê metadados (`lstat`, `stat`) e calcula caminhos.

### 2. Execução

```text
Plano
  │
  ├─ journal.save(run)                 ← estado inicial
  │
  ├─ para cada operação:
  │     verifica origem
  │     cria diretório de destino
  │     resolve colisão tardia
  │     shutil.move(origem, destino)
  │     atualiza status (concluida/falhou)
  │     journal.save(run)              ← persistência incremental
  │
  └─ journal.save(run)                 ← estado final
```

Falhas são isoladas: uma operação com erro não impede as seguintes. O status
individual fica registrado no journal.

### 3. Undo

```text
run (journal)
  │
  ├─ percorre operações em ordem inversa
  ├─ somente status "concluida"
  ├─ verifica se destino ainda existe
  ├─ verifica se origem está livre
  ├─ shutil.move(destino, origem)
  └─ marca "desfeita" ou "desfazer_falhou"
```

O undo nunca sobrescreve um arquivo existente. Se a origem já estiver ocupada,
a operação é marcada como falha e o restante continua.

### 4. Relatórios

O relatório é gerado a partir do `Run` final. O formato é escolhido pela
extensão:

| Extensão | Formato | Encoding |
| --- | --- | --- |
| `.md` | Markdown | UTF-8 |
| `.csv` | CSV com `;` | UTF-8 com BOM |
| `.json` | JSON | UTF-8 |

Sem extensão, o padrão é Markdown. Sem caminho (`--report`), o arquivo vai para
`<estado>/reports/relatorio-<run>.md`.

## Modelo de dados

### `Operation`

```python
Operation(
    action=Action.MOVE,
    source=Path("Downloads/foto.jpg"),
    destination=Path("Downloads/Imagens/foto.jpg"),
    reason="categoria Imagens",
    size=2048,
    status=Status.PLANNED,
)
```

### Ciclo de vida

```text
planejada ──► concluida ──► desfeita
    │              │
    └──────────────┴──► falhou / desfazer_falhou
```

### Journal

Cada execução gera um arquivo JSON em `<estado>/runs/<id>.json`. O nome do
arquivo é o ID da execução (`AAAAMMDD-HHMMSS-sufixo`), o que mantém a ordenação
cronológica natural.

## Decisões de projeto

### Por que simular por padrão?

Mover arquivos é uma operação destrutiva do ponto de vista do usuário. O padrão
seguro é mostrar o plano; a execução exige uma ação explícita (`--apply`).

### Por que separar plano e execução?

Permite testar toda a lógica de decisão sem tocar no disco. Também permite que
o usuário revise o plano antes de confirmar e que o journal registre exatamente
o que foi planejado.

### Por que journal em JSON?

- Legível por humanos.
- Sem dependências.
- Fácil de versionar e inspecionar.
- Suficiente para o volume de operações do projeto.

### Por que não sobrescrever arquivos?

Sobrescrever é irreversível e pode destruir dados. O CaosZero sempre gera um
nome único (`arquivo (1).ext`) quando o destino já existe.

### Por que ignorar links simbólicos?

Seguir links pode mover arquivos fora do diretório alvo ou criar ciclos. O
planejador ignora links e o executor recusa movê-los.

### Por que recusar a raiz do sistema?

Organizar `/` ou `C:\` poderia mover arquivos essenciais e quebrar o sistema.
A validação é feita no planejador.

## Tratamento de erros

| Situação | Comportamento |
| --- | --- |
| Alvo inexistente | `PlanError`, código 1 |
| Alvo não é diretório | `PlanError`, código 1 |
| Raiz do sistema | `PlanError`, código 1 |
| Configuração inválida | `ConfigError`, código 1 |
| Falha ao mover um arquivo | Operação marcada como falha, demais continuam |
| Destino ocupado | Nome único gerado automaticamente |
| Sem permissão de escrita | Aviso no plano; execução pode falhar |
| `Ctrl+C` | Código 130 |

## Concorrência e integridade

O CaosZero não usa locks de sistema de arquivos. Ele reduz riscos com:

- verificação de existência antes de mover;
- resolução de colisão no planejamento **e** na execução;
- journal incremental;
- undo que não sobrescreve.

Para uso concorrente intenso, recomenda-se executar uma instância por diretório
alvo ou usar um agendador que evite sobreposição.

## Portabilidade

- Caminhos via `pathlib`.
- Diretório de estado por sistema (`XDG`, `%LOCALAPPDATA%`).
- Detecção de arquivos ocultos em POSIX e Windows.
- Sanitização de nomes reservados do Windows (`CON`, `NUL`, `COM1` etc.).
- Diagnóstico de memória específico por plataforma.
- CI em Ubuntu e Windows.
