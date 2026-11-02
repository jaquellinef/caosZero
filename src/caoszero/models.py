"""Modelos de domínio compartilhados entre planejador, executor e relatórios."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


class Action(str, Enum):
    """Ações que o planejador pode propor."""

    MOVE = "mover"
    RENAME = "renomear"
    ARCHIVE = "arquivar"

    def label(self) -> str:
        return {
            Action.MOVE: "MOVER",
            Action.RENAME: "RENOMEAR",
            Action.ARCHIVE: "ARQUIVAR",
        }[self]


class Status(str, Enum):
    """Ciclo de vida de uma operação."""

    PLANNED = "planejada"
    DONE = "concluida"
    FAILED = "falhou"
    UNDONE = "desfeita"
    UNDO_FAILED = "desfazer_falhou"


@dataclass
class Operation:
    action: Action
    source: Path
    destination: Path | None
    reason: str = ""
    size: int = 0
    status: Status = Status.PLANNED
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "action": self.action.value,
            "source": str(self.source),
            "destination": str(self.destination) if self.destination else None,
            "reason": self.reason,
            "size": self.size,
            "status": self.status.value,
            "error": self.error,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Operation":
        destination = data.get("destination")
        return cls(
            action=Action(data["action"]),
            source=Path(data["source"]),
            destination=Path(destination) if destination else None,
            reason=str(data.get("reason", "")),
            size=int(data.get("size", 0)),
            status=Status(data.get("status", Status.PLANNED.value)),
            error=data.get("error"),
        )


@dataclass
class SkippedFile:
    path: Path
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {"path": str(self.path), "reason": self.reason}


@dataclass
class Run:
    """Uma execução (real ou simulada) do CaosZero."""

    id: str
    started_at: str
    target: str
    dry_run: bool
    operations: list[Operation] = field(default_factory=list)
    skipped: list[SkippedFile] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    finished_at: str | None = None
    version: str = "2.0.0"

    def counts(self) -> dict[str, int]:
        counts = {
            "total": len(self.operations),
            "planejadas": 0,
            "concluidas": 0,
            "falharam": 0,
            "desfeitas": 0,
            "ignorados": len(self.skipped),
            "bytes": 0,
        }
        for operation in self.operations:
            counts["bytes"] += operation.size
            if operation.status == Status.PLANNED:
                counts["planejadas"] += 1
            elif operation.status == Status.DONE:
                counts["concluidas"] += 1
            elif operation.status == Status.FAILED:
                counts["falharam"] += 1
            elif operation.status == Status.UNDONE:
                counts["desfeitas"] += 1
        return counts

    def by_category(self) -> dict[str, int]:
        result: dict[str, int] = {}
        for operation in self.operations:
            if operation.destination is None:
                category = "—"
            elif operation.action == Action.RENAME:
                category = "Renomeados"
            else:
                category = operation.destination.parent.name
            result[category] = result.get(category, 0) + 1
        return dict(sorted(result.items()))

    def is_applied(self) -> bool:
        return not self.dry_run

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "version": self.version,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "target": self.target,
            "dry_run": self.dry_run,
            "counts": self.counts(),
            "by_category": self.by_category(),
            "warnings": list(self.warnings),
            "operations": [operation.to_dict() for operation in self.operations],
            "skipped": [item.to_dict() for item in self.skipped],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Run":
        return cls(
            id=str(data["id"]),
            version=str(data.get("version", "2.0.0")),
            started_at=str(data["started_at"]),
            finished_at=data.get("finished_at"),
            target=str(data["target"]),
            dry_run=bool(data.get("dry_run", False)),
            warnings=list(data.get("warnings", [])),
            operations=[Operation.from_dict(item) for item in data.get("operations", [])],
            skipped=[SkippedFile(Path(item["path"]), item.get("reason", "")) for item in data.get("skipped", [])],
        )


def now_iso() -> str:
    """Data/hora local em ISO 8601, sem microssegundos."""
    return datetime.now().replace(microsecond=0).isoformat(sep=" ")


def new_run_id() -> str:
    """Identificador ordenável: data, hora e sufixo aleatório curto."""
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    suffix = os.urandom(3).hex()
    return f"{stamp}-{suffix}"
