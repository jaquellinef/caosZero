# Instalação

## Requisitos

- Python **3.10** ou superior.
- Git (para clonar o repositório).
- Windows, Linux ou macOS.

## Opção 1 — direto do repositório

```bash
git clone https://github.com/julianasaunders/caosZero.git
cd caosZero
python caoszero.py --version
```

## Opção 2 — instalar como pacote

```bash
python -m pip install .
caoszero --help
```

## Opção 3 — ambiente virtual

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

Windows:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

## Verificar a instalação

```bash
python caoszero.py --version
python caoszero.py doctor
```

O diagnóstico mostra sistema, processo, CPU, memória, disco e permissões.

## Problemas comuns

| Problema | Solução |
| --- | --- |
| `python` não encontrado | Use `py -3` ou o caminho completo |
| `Permission denied` | Ajuste permissões ou use outra pasta |
| `ModuleNotFoundError` | Execute a partir da raiz do repositório |
| Script bloqueado no Windows | Use `powershell -ExecutionPolicy Bypass -File` |

Voltar para [Home](Home).
