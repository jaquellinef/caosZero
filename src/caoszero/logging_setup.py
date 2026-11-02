"""Configuração de logs operacionais com rotação de arquivo."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOGGER_NAME = "caoszero"


def configure_logging(state_dir: Path, verbose: bool = False) -> logging.Logger:
    """Cria (ou reutiliza) o logger da aplicação.

    O console mostra apenas avisos por padrão para não poluir a saída da CLI.
    O arquivo guarda INFO/DEBUG com rotação de 1 MB e três backups.
    """
    state_dir = Path(state_dir).expanduser().resolve()
    logs_dir = state_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / "caoszero.log"

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    close_logging()

    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s", "%Y-%m-%d %H:%M:%S")
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO if verbose else logging.WARNING)
    console_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


def close_logging() -> None:
    """Fecha os handlers abertos (importante no Windows, que bloqueia arquivos)."""
    logger = logging.getLogger(LOGGER_NAME)
    for handler in list(logger.handlers):
        try:
            handler.flush()
            handler.close()
        finally:
            logger.removeHandler(handler)
