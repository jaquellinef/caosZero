# Testes do CaosZero

## Estratégia

O projeto usa apenas a biblioteca padrão (`unittest`), sem dependências
externas. A pirâmide é dividida em:

| Camada | Arquivos | Objetivo |
| --- | --- | --- |
| Unitários | `test_config`, `test_utils`, `test_planner`, `test_executor`, `test_reporter`, `test_system_info` | Validar cada módulo isoladamente |
| Ponta a ponta | `test_cli` | Validar a CLI como um usuário faria |
| Integração | `test_integration` | Validar o fluxo completo com filesystem real |
| CI | `.github/workflows/ci.yml` | Executar em Ubuntu e Windows |

## Como executar

```bash
# Todos os testes
python -m unittest discover -s tests -v

# Um módulo
python -m unittest tests.test_planner -v

# Um teste específico
python -m unittest tests.test_planner.PlannerTests.test_categoriza_por_extensao -v

# Script de verificação rápida
./scripts/verificar.sh       # Linux/macOS
.\scripts\verificar.ps1      # Windows
```

## Isolamento

Nenhum teste toca arquivos reais do usuário. Todos usam:

- `tempfile.TemporaryDirectory()` para pastas temporárias;
- `CAOSZERO_HOME` apontando para um diretório temporário;
- `unittest.mock` quando necessário;
- `subprocess` apenas para testes da CLI.

O arquivo `tests/_bootstrap.py` garante que `src/` esteja no `sys.path`, mesmo
sem instalar o pacote.

## Cobertura por módulo

### `test_config.py`

- Valores padrão.
- Carregamento de JSON válido.
- JSON inválido e campos com tipo errado.
- Extensões sem ponto e normalização para minúsculas.
- Diretório de estado conforme o sistema.
- Criação de configuração de exemplo e proteção contra sobrescrita.

### `test_utils.py`

- Conversão de tamanhos (`human_size`, `parse_size`).
- Sanitização de nomes inválidos e reservados do Windows.
- Geração de destinos únicos.
- Detecção de arquivos ocultos.
- Expansão de padrões de renomeação (`{seq:03d}`, `{date}`, `{categoria}`).

### `test_planner.py`

- Categorização por extensão, incluindo extensões compostas.
- Filtros por padrão, idade, tamanho e categoria.
- Inclusão de subdiretórios e arquivos ocultos.
- Arquivamento por ano.
- Renomeação em massa.
- Resolução de colisões.
- Recusa da raiz do sistema.
- Alvo inexistente e alvo que não é diretório.
- Garantia de que o planejador não altera arquivos.

### `test_executor.py`

- Execução real move arquivos.
- Simulação não altera nada e não cria journal.
- Falha em uma operação não interrompe as demais.
- Journal é salvo antes e depois de cada operação.
- Undo restaura os arquivos.
- Undo não sobrescreve origem ocupada.
- Undo de simulação é recusado.

### `test_reporter.py`

- Markdown contém resumo, tabela e operações.
- CSV usa `;` e cabeçalho correto.
- JSON é válido e contém os campos esperados.
- Escolha de formato pela extensão.
- Relatório automático em diretório de estado.

### `test_system_info.py`

- Estrutura do dicionário retornado.
- Campos de processo, CPU, memória, disco e permissões.
- Renderização em texto sem exceções.
- Tolerância a sistemas sem load average ou cgroup.

### `test_cli.py`

- `--version` e `--help`.
- `demo` cria o sandbox.
- `organize` sem `--apply` não altera arquivos.
- `organize --apply --yes` executa.
- `--json` produz JSON válido.
- `undo --latest` restaura.
- Códigos de saída esperados.
- `doctor --json` funciona.
- `config --show` e `config --init`.

### `test_integration.py`

Fluxo completo:

```text
demo → organize (simulação) → organize --apply → relatório
     → undo → verificação de restauração → novo organize
```

Também cobre:

- `CAOSZERO_HOME` e `CAOSZERO_TARGET`;
- organização recursiva com arquivos antigos;
- renomeação em massa com colisão;
- relatórios MD, CSV e JSON;
- falha parcial e recuperação.

## Execução no CI

O workflow `.github/workflows/ci.yml` roda em matriz:

| Sistema | Python |
| --- | --- |
| Ubuntu | 3.10 e 3.12 |
| Windows | 3.10 e 3.12 |

Etapas:

1. `python -m compileall -q src tests`
2. `python -m unittest discover -s tests -v`
3. Smoke test da CLI (`demo`, `organize`, `--json`, `doctor`)
4. Upload dos relatórios como artefatos

## Como escrever novos testes

1. Use `TemporaryDirectory` para qualquer teste com arquivos.
2. Aponte `CAOSZERO_HOME` para o diretório temporário.
3. Não dependa de ordem de execução entre testes.
4. Prefira asserções sobre comportamento observável.
5. Um teste deve falhar por um motivo claro.

Exemplo:

```python
import os
import tempfile
import unittest
from pathlib import Path

from caoszero.config import Config
from caoszero.planner import PlanOptions, build_plan


class MeuTeste(unittest.TestCase):
    def test_organiza_pdf(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "relatorio.pdf").write_bytes(b"%PDF")
            plan = build_plan(root, Config(), PlanOptions(), state_dir=root / ".state")
            self.assertEqual(len(plan.operations), 1)
            self.assertEqual(plan.operations[0].destination.name, "relatorio.pdf")
```

## Métricas atuais

- **77 testes** automatizados.
- Cobertura funcional de todos os módulos.
- Tempo de execução inferior a 1 segundo em máquina local.
- Nenhuma dependência externa.

## Interpretando falhas

| Mensagem | Significado |
| --- | --- |
| `FileNotFoundError` | Um caminho esperado não existe |
| `PermissionError` | O teste tentou escrever fora do diretório temporário |
| `AssertionError` | O comportamento observado difere do esperado |
| `ModuleNotFoundError: caoszero` | `_bootstrap.py` não foi carregado |

## Checklist antes de abrir um PR

- [ ] `python -m unittest discover -s tests` passa.
- [ ] `python -m compileall -q src tests` passa.
- [ ] Nenhum arquivo temporário foi commitado.
- [ ] O README ou a documentação foi atualizado, se necessário.
- [ ] O commit segue Conventional Commits.
