#!/usr/bin/env bash
#
# CaosZero — execução automatizada em Linux/macOS.
#
# Uso:
#   ./scripts/automacao.sh                      # simula a organização de ~/Downloads
#   ./scripts/automacao.sh --apply              # executa de verdade
#   ./scripts/automacao.sh --target ~/Downloads --apply --report
#   ./scripts/automacao.sh --doctor             # diagnóstico do sistema
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PYTHON="${CAOSZERO_PYTHON:-python3}"

if ! command -v "$PYTHON" >/dev/null 2>&1; then
    PYTHON="python"
fi
if ! command -v "$PYTHON" >/dev/null 2>&1; then
    echo "Erro: Python 3 não encontrado. Instale o Python 3.10+ ou defina CAOSZERO_PYTHON." >&2
    exit 1
fi

TARGET="${CAOSZERO_TARGET:-}"
APPLY=0
REPORT_MODE=""
DOCTOR=0
POSITIONAL=()

mostrar_ajuda() {
    sed -n '2,12p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --apply)
            APPLY=1
            shift
            ;;
        --report)
            REPORT_MODE="auto"
            shift
            if [[ $# -gt 0 && "$1" != -* ]]; then
                REPORT_MODE="$1"
                shift
            fi
            ;;
        --doctor)
            DOCTOR=1
            shift
            ;;
        --target)
            if [[ $# -lt 2 ]]; then
                echo "Erro: --target exige um caminho." >&2
                exit 1
            fi
            TARGET="$2"
            shift 2
            ;;
        -h|--help)
            mostrar_ajuda
            exit 0
            ;;
        -*)
            echo "Opção desconhecida: $1" >&2
            mostrar_ajuda >&2
            exit 1
            ;;
        *)
            POSITIONAL+=("$1")
            shift
            ;;
    esac
done

if [[ ${#POSITIONAL[@]} -gt 0 && -z "$TARGET" ]]; then
    TARGET="${POSITIONAL[0]}"
fi
if [[ -z "$TARGET" ]]; then
    if [[ -d "$HOME/Downloads" ]]; then
        TARGET="$HOME/Downloads"
    else
        TARGET="$(pwd)"
    fi
fi

ARGS=("$ROOT_DIR/caoszero.py")
if [[ $DOCTOR -eq 1 ]]; then
    ARGS+=(doctor "$TARGET")
else
    ARGS+=(organize "$TARGET")
    if [[ $APPLY -eq 1 ]]; then
        ARGS+=(--apply --yes)
    fi
    if [[ -n "$REPORT_MODE" ]]; then
        ARGS+=(--report "$REPORT_MODE")
    fi
fi

echo "=============================================="
echo "  CaosZero — automação de arquivos"
echo "=============================================="
echo "Python: $("$PYTHON" --version 2>&1)"
echo "Alvo...: $TARGET"
echo "Modo...: $([[ $APPLY -eq 1 ]] && echo 'EXECUÇÃO' || echo 'SIMULAÇÃO')"
echo ""

"$PYTHON" "${ARGS[@]}"

echo ""
echo "Execução finalizada. Consulte os relatórios em:"
echo "  ${CAOSZERO_HOME:-${XDG_DATA_HOME:-$HOME/.local/share}/caoszero}/reports"
