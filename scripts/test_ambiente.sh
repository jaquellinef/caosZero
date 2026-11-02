#!/usr/bin/env bash
#
# Cria um ambiente de demonstração com arquivos variados.
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PYTHON="${CAOSZERO_PYTHON:-python3}"
DESTINO="${1:-$ROOT_DIR/sandbox_teste}"

if ! command -v "$PYTHON" >/dev/null 2>&1; then
    PYTHON="python"
fi
if ! command -v "$PYTHON" >/dev/null 2>&1; then
    echo "Erro: Python 3 não encontrado." >&2
    exit 1
fi

"$PYTHON" "$ROOT_DIR/caoszero.py" demo "$DESTINO"
