"""Leitura segura de diretórios e montagem do plano de operações.

O planejador nunca altera o sistema de arquivos: ele apenas observa metadados
(tamanho, data de modificação, permissões) e calcula destinos. Essa separação
é o que permite oferecer o modo de simulação (``--dry-run``) com segurança.
"""

from __future__ import annotations

import fnmatch
import os
import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path

from .config import Config, default_state_dir
from .errors import PlanError
from .models import Action, Operation, SkippedFile
from .utils import (
    human_size,
    is_hidden,
    matches_any,
    relative_label,
    render_pattern,
    unique_destination,
)


@dataclass
class PlanOptions:
    """Opções de seleção e transformação usadas pelo planejador."""

    recursive: bool = False
    include_hidden: bool = False
    pattern: str | None = None
    older_than: int | None = None
    archive_old_days: int | None = None
    rename_pattern: str | None = None
    rename_only: bool = False
    category: str | None = None
    min_size: int | None = None
    max_size: int | None = None


@dataclass
class Plan:
    """Resultado do planejamento, pronto para ser exibido ou executado."""

    target: Path
    operations: list[Operation] = field(default_factory=list)
    skipped: list[SkippedFile] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    scanned: int = 0

    @property
    def total_bytes(self) -> int:
        return sum(operation.size for operation in self.operations)

    def counts(self) -> dict[str, int]:
        return {
            "analisados": self.scanned,
            "operacoes": len(self.operations),
            "ignorados": len(self.skipped),
            "bytes": self.total_bytes,
        }


def _norm(path: Path | str) -> str:
    return os.path.normcase(str(path))


def _is_within(path: Path, root: Path) -> bool:
    """True quando ``path`` está dentro de ``root`` (inclusive igual)."""
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _prune_dirs(current: Path, dirs: list[str], options: PlanOptions, config: Config,
                target: Path, state_dir: Path) -> list[str]:
    kept: list[str] = []
    for name in dirs:
        candidate = current / name
        lowered = name.lower()
        if lowered in {item.lower() for item in config.ignore_dirs}:
            continue
        if _norm(candidate) == _norm(state_dir) or _is_within(candidate, state_dir):
            continue
        if not options.include_hidden and is_hidden(candidate):
            continue
        # Não entra nas pastas que o próprio CaosZero criou.
        if current == target and (
            lowered in {item.lower() for item in config.categories}
            or lowered == config.archive_dir.lower()
        ):
            continue
        kept.append(name)
    return kept


def _iter_files(target: Path, options: PlanOptions, config: Config, state_dir: Path):
    """Percorre arquivos sem seguir links simbólicos de diretório."""
    if not options.recursive:
        try:
            entries = sorted(target.iterdir(), key=lambda item: item.name.lower())
        except OSError as exc:
            raise PlanError(f"Não foi possível listar {target}: {exc}") from exc
        for entry in entries:
            yield entry
        return

    for current_raw, dirs, files in os.walk(target, followlinks=False):
        current = Path(current_raw)
        dirs[:] = _prune_dirs(current, dirs, options, config, target, state_dir)
        dirs.sort(key=str.lower)
        for name in sorted(files, key=str.lower):
            yield current / name


def _skip_reason(
    path: Path,
    target: Path,
    options: PlanOptions,
    config: Config,
    state_dir: Path,
    now: float,
) -> tuple[str | None, float]:
    """Retorna (motivo_para_ignorar, idade_em_dias)."""
    try:
        info = path.lstat()
    except OSError as exc:
        return f"metadados indisponíveis ({exc})", 0.0

    if path.is_symlink():
        return "link simbólico (ignorado por segurança)", 0.0
    if not path.is_file():
        return "não é um arquivo comum", 0.0

    # Nunca mexe no diretório de estado do próprio CaosZero.
    if _norm(path) == _norm(state_dir) or _is_within(path, state_dir):
        return "arquivo interno do CaosZero", 0.0

    name = path.name
    if not options.include_hidden and is_hidden(path):
        return "arquivo oculto", 0.0
    if name.lower() in {item.lower() for item in config.ignore_names}:
        return "nome na lista de ignorados", 0.0
    if matches_any(name, config.ignore_globs):
        return "padrão temporário ignorado", 0.0

    age_days = max(0.0, (now - info.st_mtime) / 86400.0)

    if options.pattern and not fnmatch.fnmatchcase(name.lower(), options.pattern.lower()):
        return "não corresponde ao padrão informado", age_days
    if options.older_than is not None and age_days < options.older_than:
        return f"mais novo que {options.older_than} dias", age_days
    if options.min_size is not None and info.st_size < options.min_size:
        return "menor que o tamanho mínimo", age_days
    if options.max_size is not None and info.st_size > options.max_size:
        return "maior que o tamanho máximo", age_days

    category = config.category_for(name)
    if options.category and category.lower() != options.category.lower():
        return f"categoria diferente de {options.category}", age_days

    return None, age_days


def _destination_for(
    source: Path,
    category: str,
    age_days: float,
    target: Path,
    options: PlanOptions,
    config: Config,
    sequence: int,
) -> tuple[Path, str, Action, str]:
    """Calcula destino, motivo e ação para um arquivo."""
    renamed = False
    new_name = source.name
    archiving = (
        options.archive_old_days is not None and age_days >= options.archive_old_days
    )

    if archiving:
        year = time.strftime("%Y", time.localtime(source.stat().st_mtime))
        destination_dir = target / config.archive_dir / year
        action = Action.ARCHIVE
        reason = f"arquivo antigo ({age_days:.0f} dias)"
    elif options.rename_only:
        destination_dir = source.parent
        action = Action.RENAME
        reason = "renomeação conforme padrão"
    else:
        destination_dir = target / category
        action = Action.MOVE
        reason = f"categoria {category}"

    if options.rename_pattern and not archiving:
        new_name = render_pattern(
            options.rename_pattern,
            source,
            sequence,
            category,
            mtime=source.stat().st_mtime,
        )
        renamed = new_name != source.name
        if renamed:
            reason = f"{reason}; renomeado para {new_name}"

    return destination_dir / new_name, reason, action, new_name


def build_plan(
    target: Path | str,
    config: Config | None = None,
    options: PlanOptions | None = None,
    state_dir: Path | None = None,
) -> Plan:
    """Analisa o alvo e devolve todas as operações que seriam realizadas."""
    config = config or Config()
    options = options or PlanOptions()
    state_dir = (state_dir or default_state_dir()).resolve()

    if options.rename_only and not options.rename_pattern:
        raise PlanError("--rename-only exige --rename com um padrão.")
    if options.older_than is not None and options.older_than < 0:
        raise PlanError("--older-than deve ser um número de dias maior ou igual a zero.")
    if options.archive_old_days is not None and options.archive_old_days < 0:
        raise PlanError("--archive-old deve ser um número de dias maior ou igual a zero.")

    target_path = Path(target).expanduser().resolve()
    if not target_path.exists():
        raise PlanError(f"O diretório alvo não existe: {target_path}")
    if not target_path.is_dir():
        raise PlanError(f"O alvo precisa ser um diretório: {target_path}")
    if target_path == Path(target_path.anchor):
        raise PlanError("Recusado: organizar a raiz do sistema de arquivos é inseguro.")
    if _norm(target_path) == _norm(state_dir):
        raise PlanError("O diretório de estado do CaosZero não pode ser o alvo da organização.")

    plan = Plan(target=target_path)
    if not os.access(target_path, os.W_OK):
        plan.warnings.append("O diretório alvo não tem permissão de escrita; a execução pode falhar.")
    if target_path == Path.home().resolve():
        plan.warnings.append(
            "O alvo é a pasta pessoal inteira. Prefira uma pasta específica, como Downloads."
        )
    if _is_within(state_dir, target_path):
        plan.warnings.append(
            f"O diretório de estado ({state_dir}) está dentro do alvo e será ignorado."
        )

    now = time.time()
    reserved: set[str] = set()
    sequence = 0
    seen: set[str] = set()

    for path in _iter_files(target_path, options, config, state_dir):
        if _norm(path) in seen:
            continue
        seen.add(_norm(path))

        # Diretórios não são operações: são apenas containers.
        if path.is_dir() and not path.is_symlink():
            continue

        reason, age_days = _skip_reason(path, target_path, options, config, state_dir, now)
        if reason:
            plan.skipped.append(SkippedFile(path=path, reason=reason))
            continue

        plan.scanned += 1
        category = config.category_for(path.name)

        will_rename = bool(options.rename_pattern) and not (
            options.archive_old_days is not None and age_days >= options.archive_old_days
        )
        if will_rename:
            sequence += 1

        destination, operation_reason, action, new_name = _destination_for(
            path,
            category,
            age_days,
            target_path,
            options,
            config,
            sequence,
        )

        if destination == path:
            plan.skipped.append(SkippedFile(path=path, reason="já está no destino"))
            if will_rename:
                sequence -= 1
            continue

        destination = unique_destination(destination, reserved)
        operation = Operation(
            action=action,
            source=path,
            destination=destination,
            reason=operation_reason,
            size=path.stat().st_size,
        )
        plan.operations.append(operation)

    if len(plan.operations) > 2000:
        plan.warnings.append(
            f"Plano com {len(plan.operations)} operações; considere executar por partes."
        )
    try:
        free = shutil.disk_usage(target_path).free
        min_free = config.min_free_mb * 1024 * 1024
        if free - plan.total_bytes < min_free:
            plan.warnings.append(
                "Espaço livre abaixo do limite de segurança configurado "
                f"({config.min_free_mb} MB)."
            )
    except OSError:
        pass

    return plan


def describe_plan(plan: Plan, limit: int = 25) -> str:
    """Resumo textual para a CLI (não é o relatório em arquivo)."""
    lines = [
        f"Alvo: {plan.target}",
        f"Arquivos analisados: {plan.scanned}",
        f"Operações planejadas: {len(plan.operations)} ({human_size(plan.total_bytes)})",
        f"Ignorados: {len(plan.skipped)}",
    ]

    if plan.warnings:
        lines.append("")
        lines.append("Avisos:")
        lines.extend(f"  ! {warning}" for warning in plan.warnings)

    if plan.operations:
        lines.append("")
        lines.append("Prévia das operações:")
        for operation in plan.operations[:limit]:
            destination = operation.destination or Path("?")
            lines.append(
                f"  [{operation.action.label():8}] "
                f"{relative_label(operation.source, plan.target)} -> "
                f"{relative_label(destination, plan.target)}"
            )
        remaining = len(plan.operations) - limit
        if remaining > 0:
            lines.append(f"  ... e mais {remaining} operações.")

    if plan.skipped:
        lines.append("")
        lines.append("Primeiros arquivos ignorados:")
        for item in plan.skipped[:limit]:
            lines.append(f"  - {relative_label(item.path, plan.target)}: {item.reason}")

    return "\n".join(lines)
