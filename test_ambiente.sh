#!/usr/bin/env bash
#
# Compatibilidade: o ambiente de teste agora fica em scripts/test_ambiente.sh.
#
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$ROOT_DIR/scripts/test_ambiente.sh" "$@"
