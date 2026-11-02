#!/usr/bin/env bash
#
# Instala os hooks locais de Git (pre-commit e pre-push).
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
HOOKS_DIR="$ROOT_DIR/.git/hooks"

if [[ ! -d "$HOOKS_DIR" ]]; then
    echo "Erro: $ROOT_DIR não parece ser um repositório Git." >&2
    exit 1
fi

for hook in pre-commit pre-push; do
    install -m 755 "$SCRIPT_DIR/githooks/$hook" "$HOOKS_DIR/$hook"
    echo "Hook instalado: $hook"
done

echo ""
echo "Pronto. Os hooks agora rodam verificação antes de commit e push."
