"""Configuração do CaosZero.

A configuração é carregada, nesta ordem:

1. caminho informado em ``--config``;
2. variável de ambiente ``CAOSZERO_CONFIG``;
3. ``<CAOSZERO_HOME>/config.json``;
4. valores padrão embutidos no código.

O diretório de estado segue o padrão XDG no Linux/macOS e ``%LOCALAPPDATA%``
no Windows. A variável ``CAOSZERO_HOME`` tem precedência em todos os casos.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .errors import ConfigError

# Extensões mais longas primeiro para que ".tar.gz" seja reconhecido antes de ".gz".
DEFAULT_CATEGORIES: dict[str, list[str]] = {
    "Documentos": [
        ".pdf",
        ".doc",
        ".docx",
        ".txt",
        ".rtf",
        ".odt",
        ".md",
        ".epub",
        ".tex",
    ],
    "Planilhas": [".xls", ".xlsx", ".ods", ".csv", ".tsv"],
    "Apresentacoes": [".ppt", ".pptx", ".odp", ".key"],
    "Imagens": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".heic", ".tif", ".tiff"],
    "Videos": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"],
    "Musicas": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma"],
    "Compactados": [".zip", ".rar", ".7z", ".tar.gz", ".tar", ".tgz", ".bz2", ".xz", ".gz"],
    "Instaladores": [".exe", ".msi", ".deb", ".rpm", ".appimage", ".apk", ".dmg", ".pkg"],
    "Codigo": [
        ".py",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
        ".html",
        ".css",
        ".java",
        ".c",
        ".cpp",
        ".h",
        ".cs",
        ".go",
        ".rs",
        ".rb",
        ".php",
        ".sh",
        ".ps1",
        ".bat",
        ".json",
        ".xml",
        ".yml",
        ".yaml",
        ".toml",
        ".sql",
    ],
    "Outros": [],
}

DEFAULT_IGNORE_NAMES = [
    ".DS_Store",
    "Thumbs.db",
    "desktop.ini",
    "caoszero.log",
]

DEFAULT_IGNORE_GLOBS = [
    "*.tmp",
    "*.temp",
    "*.part",
    "*.partial",
    "*.crdownload",
    "*.download",
    "~$*",
    ".~lock.*",
]

DEFAULT_IGNORE_DIRS = [
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    "env",
]


def default_state_dir() -> Path:
    """Retorna o diretório de estado (logs, journal, relatórios)."""
    override = os.environ.get("CAOSZERO_HOME")
    if override:
        return Path(override).expanduser().resolve()

    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA")
        root = Path(base) if base else Path.home() / "AppData" / "Local"
        return root / "CaosZero"

    xdg = os.environ.get("XDG_DATA_HOME")
    root = Path(xdg).expanduser() if xdg else Path.home() / ".local" / "share"
    return root / "caoszero"


def default_config_path() -> Path:
    """Caminho usado por ``config --init`` e pela busca automática."""
    override = os.environ.get("CAOSZERO_CONFIG")
    if override:
        return Path(override).expanduser().resolve()
    return default_state_dir() / "config.json"


@dataclass
class Config:
    """Regras de organização carregadas pelo aplicativo."""

    categories: dict[str, list[str]] = field(
        default_factory=lambda: {name: list(exts) for name, exts in DEFAULT_CATEGORIES.items()}
    )
    ignore_names: list[str] = field(default_factory=lambda: list(DEFAULT_IGNORE_NAMES))
    ignore_globs: list[str] = field(default_factory=lambda: list(DEFAULT_IGNORE_GLOBS))
    ignore_dirs: list[str] = field(default_factory=lambda: list(DEFAULT_IGNORE_DIRS))
    archive_dir: str = "Arquivo"
    report_dir: str = "reports"
    min_free_mb: int = 50

    def category_for(self, filename: str) -> str:
        """Descobre a categoria de um arquivo pela extensão.

        Compara sem diferenciar maiúsculas de minúsculas e prioriza a
        extensão mais específica (``.tar.gz`` antes de ``.gz``).
        """
        lowered = filename.lower()
        candidates: list[tuple[str, str]] = []
        for category, extensions in self.categories.items():
            for extension in extensions:
                if extension and lowered.endswith(extension.lower()):
                    candidates.append((extension, category))

        if not candidates:
            return "Outros"

        # Extensões compostas vencem as simples.
        candidates.sort(key=lambda item: len(item[0]), reverse=True)
        return candidates[0][1]

    def to_dict(self) -> dict[str, Any]:
        return {
            "categories": {name: list(exts) for name, exts in self.categories.items()},
            "ignore_names": list(self.ignore_names),
            "ignore_globs": list(self.ignore_globs),
            "ignore_dirs": list(self.ignore_dirs),
            "archive_dir": self.archive_dir,
            "report_dir": self.report_dir,
            "min_free_mb": self.min_free_mb,
        }

    def save(self, path: Path) -> Path:
        path = Path(path).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="\n") as handle:
            json.dump(self.to_dict(), handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        return path


def _list_of_strings(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ConfigError(f"O campo '{field_name}' deve ser uma lista de textos.")
    return list(value)


def config_from_dict(data: dict[str, Any]) -> Config:
    """Valida um dicionário e devolve uma :class:`Config`."""
    if not isinstance(data, dict):
        raise ConfigError("A configuração deve ser um objeto JSON.")

    base = Config()
    categories = data.get("categories", base.categories)
    if not isinstance(categories, dict):
        raise ConfigError("O campo 'categories' deve ser um objeto.")

    parsed_categories: dict[str, list[str]] = {}
    for name, extensions in categories.items():
        if not isinstance(name, str) or not name.strip():
            raise ConfigError("Toda categoria precisa de um nome não vazio.")
        extensions = _list_of_strings(extensions, f"categories.{name}")
        parsed_categories[name] = [
            ext if ext.startswith(".") else f".{ext}" for ext in (e.lower().strip() for e in extensions)
        ]

    ignore_names = _list_of_strings(data.get("ignore_names", base.ignore_names), "ignore_names")
    ignore_globs = _list_of_strings(data.get("ignore_globs", base.ignore_globs), "ignore_globs")
    ignore_dirs = _list_of_strings(data.get("ignore_dirs", base.ignore_dirs), "ignore_dirs")

    archive_dir = data.get("archive_dir", base.archive_dir)
    report_dir = data.get("report_dir", base.report_dir)
    if not isinstance(archive_dir, str) or not archive_dir.strip():
        raise ConfigError("O campo 'archive_dir' deve ser um nome de diretório.")
    if not isinstance(report_dir, str) or not report_dir.strip():
        raise ConfigError("O campo 'report_dir' deve ser um nome de diretório.")

    min_free_mb = data.get("min_free_mb", base.min_free_mb)
    if not isinstance(min_free_mb, int) or min_free_mb < 0:
        raise ConfigError("O campo 'min_free_mb' deve ser um inteiro maior ou igual a zero.")

    return Config(
        categories=parsed_categories,
        ignore_names=ignore_names,
        ignore_globs=ignore_globs,
        ignore_dirs=ignore_dirs,
        archive_dir=archive_dir,
        report_dir=report_dir,
        min_free_mb=min_free_mb,
    )


def load_config(path: Path | None = None) -> Config:
    """Carrega a configuração do caminho indicado ou dos locais padrão."""
    explicit = Path(path).expanduser() if path else None
    candidate = explicit or default_config_path()

    if not candidate.exists():
        if explicit is not None:
            raise ConfigError(f"Arquivo de configuração não encontrado: {candidate}")
        return Config()

    try:
        with candidate.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except json.JSONDecodeError as exc:
        raise ConfigError(
            f"JSON inválido em {candidate} (linha {exc.lineno}, coluna {exc.colno})."
        ) from exc
    except OSError as exc:
        raise ConfigError(f"Não foi possível ler a configuração: {exc}") from exc

    config = config_from_dict(data)
    return config


def init_config(path: Path | None = None, force: bool = False) -> Path:
    """Escreve um arquivo de configuração de exemplo."""
    destination = Path(path).expanduser() if path else default_config_path()
    if destination.exists() and not force:
        raise ConfigError(f"Já existe um arquivo em {destination}. Use --force para sobrescrever.")
    return Config().save(destination)
