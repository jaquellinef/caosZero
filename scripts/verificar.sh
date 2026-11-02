#!/usr/bin/env bash
#
# Verificação completa usada localmente e como referência para a CI.
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PYTHON="${CAOSZERO_PYTHON:-python3}"
if ! command -v "$PYTHON" >/dev/null 2>&1; then
    PYTHON="python"
fi
if ! command -v "$PYTHON" >/dev/null 2>&1; then
    echo "Erro: Python 3 não encontrado." >&2
    exit 1
fi

cd "$ROOT_DIR"
echo "==> Compilando módulos"
"$PYTHON" -m compileall -q src tests

echo "==> Executando testes automatizados"
"$PYTHON" -m unittest discover -s tests -v

echo "==> Smoke test da CLI"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT
export CAOSZERO_HOME="$TMP_DIR/estado"
"$PYTHON" caoszero.py demo "$TMP_DIR/sandbox" >/dev/null
"$PYTHON" caoszero.py organize "$TMP_DIR/sandbox" --apply --yes --report "$TMP_DIR/relatorio.md" >/dev/null
"$PYTHON" caoszero.py doctor --json >/dev/null
test -f "$TMP_DIR/relatorio.md"

echo "==> Tudo certo."
