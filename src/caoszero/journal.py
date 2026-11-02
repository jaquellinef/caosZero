"""Histórico (journal) das execuções do CaosZero.

Cada execução real vira um arquivo JSON em ``<estado>/runs``. O journal é a
base do comando ``undo``: ele guarda a origem e o destino de cada operação.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

from .errors import JournalError
from .models import Run, Status

_SAFE_ID = re.compile(r"^[A-Za-z0-9._-]+$")


class Journal:
    def __init__(self, state_dir: Path):
        self.state_dir = Path(state_dir).expanduser().resolve()
        self.runs_dir = self.state_dir / "runs"
        self.reports_dir = self.state_dir / "reports"
        self.logs_dir = self.state_dir / "logs"

    def ensure_dirs(self) -> None:
        for directory in (self.state_dir, self.runs_dir, self.reports_dir, self.logs_dir):
            directory.mkdir(parents=True, exist_ok=True)

    def path_for(self, run_id: str) -> Path:
        if not _SAFE_ID.match(run_id):
            raise JournalError(f"Identificador de execução inválido: {run_id!r}")
        return self.runs_dir / f"{run_id}.json"

    def save(self, run: Run) -> Path:
        self.ensure_dirs()
        destination = self.path_for(run.id)
        temporary = destination.with_suffix(".json.tmp")
        try:
            with temporary.open("w", encoding="utf-8", newline="\n") as handle:
                json.dump(run.to_dict(), handle, ensure_ascii=False, indent=2)
                handle.write("\n")
            os.replace(temporary, destination)
        except OSError as exc:
            raise JournalError(f"Não foi possível gravar o histórico: {exc}") from exc
        return destination

    def load(self, run_id: str) -> Run:
        path = self.path_for(run_id)
        if not path.exists():
            raise JournalError(f"Execução não encontrada: {run_id}")
        try:
            with path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            raise JournalError(f"Histórico corrompido em {path}: {exc}") from exc
        try:
            return Run.from_dict(data)
        except (KeyError, ValueError, TypeError) as exc:
            raise JournalError(f"Histórico inválido em {path}: {exc}") from exc

    def list_runs(self) -> list[Run]:
        if not self.runs_dir.exists():
            return []
        runs: list[Run] = []
        for path in self.runs_dir.glob("*.json"):
            try:
                with path.open("r", encoding="utf-8") as handle:
                    runs.append(Run.from_dict(json.load(handle)))
            except (OSError, json.JSONDecodeError, KeyError, ValueError, TypeError):
                continue
        runs.sort(key=lambda run: (run.started_at, run.id), reverse=True)
        return runs

    def latest(self, undoable_only: bool = True) -> Run | None:
        for run in self.list_runs():
            if run.dry_run:
                continue
            if undoable_only and not any(op.status == Status.DONE for op in run.operations):
                continue
            return run
        return None
