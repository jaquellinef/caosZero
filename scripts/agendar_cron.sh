#!/usr/bin/env bash
#
# Agenda a organização automática de uma pasta usando cron.
#
# Sem --install, apenas mostra a linha que seria adicionada.
# Com --install, adiciona a linha ao crontab do usuário (sem duplicar).
#
# Uso:
#   ./scripts/agendar_cron.sh ~/Downloads
#   ./scripts/agendar_cron.sh ~/Downloads --install
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PYTHON="${CAOSZERO_PYTHON:-$(command -v python3 || command -v python || true)}"
TARGET="${1:-$HOME/Downloads}"
INSTALL=0

if [[ "${2:-}" == "--install" ]]; then
    INSTALL=1
fi

if [[ -z "$PYTHON" ]]; then
    echo "Erro: Python 3 não encontrado." >&2
    exit 1
fi

if [[ ! -d "$TARGET" ]]; then
    echo "Erro: diretório não encontrado: $TARGET" >&2
    exit 1
fi

STATE_DIR="${CAOSZERO_HOME:-${XDG_DATA_HOME:-$HOME/.local/share}/caoszero}"
LOG_FILE="$STATE_DIR/logs/cron.log"
mkdir -p "$STATE_DIR/logs"

LINE="0 9 * * 1 \"$PYTHON\" \"$ROOT_DIR/caoszero.py\" organize \"$TARGET\" --apply --yes --report >> \"$LOG_FILE\" 2>&1"

echo "Linha de agendamento (toda segunda-feira às 09:00):"
echo "$LINE"

if [[ $INSTALL -eq 0 ]]; then
    echo ""
    echo "Para instalar, execute novamente com --install."
    echo "Para editar manualmente: crontab -e"
    exit 0
fi

if crontab -l 2>/dev/null | grep -Fq "$ROOT_DIR/caoszero.py"; then
    echo ""
    echo "Já existe um agendamento do CaosZero no crontab. Nada foi alterado."
    exit 0
fi

(crontab -l 2>/dev/null || true; echo "$LINE") | crontab -
echo ""
echo "Agendamento instalado. Verifique com: crontab -l"
