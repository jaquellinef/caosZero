#!/usr/bin/env bash
#
# Compatibilidade: a automação agora fica em scripts/automacao.sh.
# Este atalho evita quebrar links e comandos antigos.
#
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$ROOT_DIR/scripts/automacao.sh" "$@"
