"""Ponto de entrada de compatibilidade.

Mantém o comando ``python caoszero.py`` funcionando a partir da raiz do
repositório, sem exigir instalação do pacote.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from caoszero.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
