"""Utilitários compartilhados pelos testes."""

from __future__ import annotations

import os
import time
from pathlib import Path


def make_file(
    root: Path,
    relative: str,
    content: bytes = b"conteudo de teste",
    days_old: float = 0,
) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    if days_old:
        timestamp = time.time() - days_old * 86400
        os.utime(path, (timestamp, timestamp))
    return path
