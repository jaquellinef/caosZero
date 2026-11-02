"""Funções utilitárias: tamanhos, nomes, caminhos e padrões de renomeação."""

from __future__ import annotations

import fnmatch
import os
import re
import stat
from datetime import datetime
from pathlib import Path

_UNITS = ("B", "KB", "MB", "GB", "TB", "PB")
_INVALID_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_RESERVED_WINDOWS = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{index}" for index in range(1, 10)),
    *(f"LPT{index}" for index in range(1, 10)),
}


def human_size(size: int) -> str:
    """Converte bytes em texto legível (base 1024)."""
    if size < 0:
        return "0 B"
    value = float(size)
    for unit in _UNITS:
        if value < 1024 or unit == _UNITS[-1]:
            if unit == "B":
                return f"{int(value)} {unit}"
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} PB"


def parse_size(text: str) -> int:
    """Interpreta ``10MB``, ``500 KB`` ou ``1024`` e devolve bytes."""
    cleaned = text.strip().replace(" ", "").upper()
    match = re.fullmatch(r"(\d+(?:[.,]\d+)?)(B|KB|MB|GB|TB)?", cleaned)
    if not match:
        raise ValueError(f"Tamanho inválido: {text!r}. Exemplos: 500KB, 10MB, 2GB.")
    number = float(match.group(1).replace(",", "."))
    unit = match.group(2) or "B"
    factor = 1024 ** _UNITS.index(unit)
    return int(number * factor)


def sanitize_filename(name: str) -> str:
    """Remove caracteres proibidos e evita nomes reservados do Windows."""
    cleaned = _INVALID_CHARS.sub("-", name).strip().strip(".")
    cleaned = re.sub(r"\s+", " ", cleaned)
    if not cleaned:
        cleaned = "arquivo"
    stem = cleaned.split(".")[0].upper()
    if stem in _RESERVED_WINDOWS:
        cleaned = f"_{cleaned}"
    return cleaned[:200]


def unique_destination(path: Path, reserved: set[str] | None = None) -> Path:
    """Devolve um caminho livre acrescentando `` (n)`` antes da extensão."""
    reserved = reserved if reserved is not None else set()

    def key(candidate: Path) -> str:
        return os.path.normcase(str(candidate.resolve(strict=False)))

    if not path.exists() and key(path) not in reserved:
        reserved.add(key(path))
        return path

    suffix = "".join(path.suffixes)
    stem = path.name[: -len(suffix)] if suffix else path.name
    counter = 1
    while True:
        candidate = path.with_name(f"{stem} ({counter}){suffix}")
        if not candidate.exists() and key(candidate) not in reserved:
            reserved.add(key(candidate))
            return candidate
        counter += 1


def is_hidden(path: Path) -> bool:
    """Detecta arquivos ocultos em POSIX e Windows."""
    if path.name.startswith("."):
        return True
    if os.name == "nt":
        try:
            attributes = path.stat().st_file_attributes
        except (OSError, AttributeError):
            return False
        return bool(attributes & stat.FILE_ATTRIBUTE_HIDDEN)
    return False


def matches_any(name: str, patterns: list[str]) -> bool:
    """Compara um nome com uma lista de padrões glob (case-insensitive)."""
    lowered = name.lower()
    return any(fnmatch.fnmatchcase(lowered, pattern.lower()) for pattern in patterns)


def render_pattern(
    pattern: str,
    source: Path,
    sequence: int,
    category: str,
    mtime: float | None = None,
) -> str:
    """Expande um padrão de renomeação.

    Tokens disponíveis: ``{name}``/``{stem}``, ``{ext}``, ``{extensao}``,
    ``{date}``/``{data}``, ``{seq}``, ``{categoria}``.
    ``{seq:03d}`` produz ``001``.
    """
    extension = source.suffix
    stem = source.name[: -len(extension)] if extension else source.name
    moment = datetime.fromtimestamp(mtime if mtime is not None else source.stat().st_mtime)
    values = {
        "name": stem,
        "stem": stem,
        "ext": extension,
        "extensao": extension.lstrip("."),
        "date": moment.strftime("%Y-%m-%d"),
        "data": moment.strftime("%Y-%m-%d"),
        "seq": str(sequence),
        "categoria": category,
    }

    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        spec = match.group(2)
        if key not in values:
            return match.group(0)
        value = values[key]
        if spec:
            try:
                return format(int(value), spec) if value.isdigit() else format(value, spec)
            except (ValueError, TypeError):
                return value
        return value

    rendered = re.sub(r"\{([a-zA-Z_]+)(?::([^}]+))?\}", replace, pattern)
    rendered = sanitize_filename(rendered)

    # Preserva a extensão quando o padrão não a informa.
    if extension and not rendered.lower().endswith(extension.lower()):
        rendered = f"{rendered}{extension}"
    return rendered


def relative_label(path: Path, root: Path) -> str:
    """Caminho relativo para exibição; mantém absoluto se estiver fora."""
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)
