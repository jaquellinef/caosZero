"""Execução das operações planejadas e desfazimento (undo)."""

from __future__ import annotations

import logging
import shutil
from dataclasses import dataclass
from pathlib import Path

from .journal import Journal
from .models import Action, Run, Status, new_run_id, now_iso
from .planner import Plan
from .utils import unique_destination


@dataclass
class ExecutionResult:
    run: Run
    moved: int
    failed: int
    undone: int
    undo_failed: int


def create_run(plan: Plan, dry_run: bool) -> Run:
    return Run(
        id=new_run_id(),
        started_at=now_iso(),
        target=str(plan.target),
        dry_run=dry_run,
        operations=plan.operations,
        skipped=plan.skipped,
        warnings=list(plan.warnings),
    )


def execute_plan(
    plan: Plan,
    journal: Journal,
    logger: logging.Logger,
    dry_run: bool = True,
) -> ExecutionResult:
    """Executa (ou apenas materializa) um plano.

    Em modo de simulação nada é gravado no disco e nenhum journal é criado.
    Em modo real, cada operação é persistida antes e depois de ser executada,
    permitindo recuperar o histórico mesmo se o processo for interrompido.
    """
    run = create_run(plan, dry_run=dry_run)
    moved = 0
    failed = 0

    if dry_run:
        run.finished_at = now_iso()
        logger.info("Simulação concluída: %s operações planejadas.", len(run.operations))
        return ExecutionResult(run=run, moved=0, failed=0, undone=0, undo_failed=0)

    journal.save(run)
    logger.info("Execução %s iniciada em %s", run.id, run.target)

    for operation in run.operations:
        if operation.status != Status.PLANNED:
            continue
        if operation.destination is None:
            operation.status = Status.FAILED
            operation.error = "operação sem destino"
            failed += 1
            journal.save(run)
            continue

        source = operation.source
        destination = operation.destination
        try:
            if not source.exists():
                raise FileNotFoundError(f"origem não encontrada: {source}")
            if source.is_symlink():
                raise OSError("link simbólico não é movido por segurança")
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.exists():
                # Pode ter surgido um arquivo entre o planejamento e a execução.
                destination = unique_destination(destination)
                operation.destination = destination
            shutil.move(str(source), str(destination))
            operation.status = Status.DONE
            operation.error = None
            moved += 1
            logger.info("Movido: %s -> %s", source, destination)
        except (OSError, shutil.Error) as exc:
            operation.status = Status.FAILED
            operation.error = str(exc)
            failed += 1
            logger.error("Falha ao mover %s: %s", source, exc)
        journal.save(run)

    run.finished_at = now_iso()
    journal.save(run)
    logger.info(
        "Execução %s finalizada: %s concluídas, %s falhas.", run.id, moved, failed
    )
    return ExecutionResult(run=run, moved=moved, failed=failed, undone=0, undo_failed=0)


def undo_run(
    run: Run,
    journal: Journal,
    logger: logging.Logger,
    dry_run: bool = False,
) -> ExecutionResult:
    """Tenta desfazer as operações concluídas de uma execução."""
    if run.dry_run:
        raise ValueError("Uma simulação não pode ser desfeita.")

    target_run = Run.from_dict(run.to_dict()) if dry_run else run
    undone = 0
    undo_failed = 0

    for operation in reversed(target_run.operations):
        if operation.status != Status.DONE or operation.destination is None:
            continue
        destination = operation.destination
        source = operation.source

        if not destination.exists():
            operation.status = Status.UNDO_FAILED
            operation.error = f"destino não existe mais: {destination}"
            undo_failed += 1
            continue
        if source.exists():
            operation.status = Status.UNDO_FAILED
            operation.error = f"origem já ocupada: {source}"
            undo_failed += 1
            continue

        if dry_run:
            undone += 1
            continue

        try:
            source.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(destination), str(source))
            operation.status = Status.UNDONE
            operation.error = None
            undone += 1
            logger.info("Desfeito: %s -> %s", destination, source)
        except (OSError, shutil.Error) as exc:
            operation.status = Status.UNDO_FAILED
            operation.error = str(exc)
            undo_failed += 1
            logger.error("Falha ao desfazer %s: %s", destination, exc)
        if not dry_run:
            journal.save(target_run)

    if not dry_run:
        target_run.finished_at = now_iso()
        journal.save(target_run)
    logger.info("Undo: %s restauradas, %s falhas.", undone, undo_failed)
    return ExecutionResult(
        run=target_run,
        moved=0,
        failed=0,
        undone=undone,
        undo_failed=undo_failed,
    )


def count_categories(run: Run) -> dict[str, int]:
    """Compatibilidade: contagem de operações por pasta de destino."""
    return run.by_category()


def available_actions() -> list[str]:
    return [action.value for action in Action]
