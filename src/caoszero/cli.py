"""Interface de linha de comando do CaosZero."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from . import __version__
from .config import Config, default_config_path, default_state_dir, init_config, load_config
from .demo import criar_sandbox
from .errors import CaosZeroError
from .executor import execute_plan, undo_run
from .journal import Journal
from .logging_setup import close_logging, configure_logging
from .models import Status
from .planner import PlanOptions, build_plan, describe_plan
from .reporter import write_report
from .system_info import collect_system_info, render_text
from .utils import human_size, parse_size, relative_label

DESCRIPTION = """\
CaosZero — automatizador de tarefas com arquivos.

Organiza pastas por categoria, renomeia arquivos em massa, arquiva itens
antigos, gera relatórios e permite desfazer a última execução.

Por padrão o comando 'organize' apenas SIMULA as operações. Use --apply
para alterar os arquivos de verdade.
"""

EPILOG = """\
exemplos:
  python caoszero.py demo
  python caoszero.py organize ./sandbox_teste
  python caoszero.py organize ./Downloads --apply --report
  python caoszero.py organize . --recursive --archive-old 180 --apply
  python caoszero.py organize . --rename "arquivo-{seq:03d}{ext}" --apply
  python caoszero.py undo --list
  python caoszero.py undo --latest
  python caoszero.py doctor
"""


def _size_arg(value: str) -> int:
    try:
        return parse_size(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def _configure_stdout() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def _confirm(question: str) -> bool:
    if not sys.stdin.isatty():
        return False
    try:
        answer = input(f"{question} [s/N] ").strip().lower()
    except EOFError:
        return False
    return answer in {"s", "sim", "y", "yes"}


def _state() -> Path:
    return default_state_dir()


def _default_target(value: str | None) -> Path:
    raw = value or os.environ.get("CAOSZERO_TARGET") or "."
    return Path(raw).expanduser()


def _print_plan(plan) -> None:
    print(describe_plan(plan))


def _report_path(value: str, run) -> Path:
    if value == "auto":
        return _state() / "reports" / f"relatorio-{run.id}.md"
    return Path(value).expanduser()


def _validate_organize_args(args: argparse.Namespace, config: Config) -> None:
    if args.rename_only and not args.rename:
        raise CaosZeroError("--rename-only exige --rename com um padrão.")
    if args.min_size is not None and args.max_size is not None and args.min_size > args.max_size:
        raise CaosZeroError("--min-size não pode ser maior que --max-size.")
    if args.category and not any(
        name.lower() == args.category.lower() for name in config.categories
    ):
        available = ", ".join(config.categories)
        raise CaosZeroError(
            f"Categoria desconhecida: {args.category}. Disponíveis: {available}."
        )


def cmd_organize(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    _validate_organize_args(args, config)
    state_dir = _state()
    logger = configure_logging(state_dir, verbose=args.verbose)

    options = PlanOptions(
        recursive=args.recursive,
        include_hidden=args.hidden,
        pattern=args.pattern,
        older_than=args.older_than,
        archive_old_days=args.archive_old,
        rename_pattern=args.rename,
        rename_only=args.rename_only,
        category=args.category,
        min_size=args.min_size,
        max_size=args.max_size,
    )

    target = _default_target(args.target)
    plan = build_plan(target, config=config, options=options, state_dir=state_dir)
    dry_run = not args.apply

    if not args.json:
        _print_plan(plan)

    if not plan.operations:
        if args.json:
            print(
                json.dumps(
                    {
                        "mode": "simulacao" if dry_run else "execucao",
                        "summary": plan.counts(),
                        "operations": [],
                        "report": None,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            print("\nNada a fazer: nenhum arquivo corresponde aos critérios.")
        return 0

    if not dry_run and not args.yes:
        if not _confirm(f"Executar {len(plan.operations)} operações em {target}?"):
            print("Operação cancelada. Nenhum arquivo foi alterado.")
            return 2

    result = execute_plan(plan, Journal(state_dir), logger, dry_run=dry_run)
    run = result.run

    report_path = None
    if args.report:
        report_path = write_report(run, _report_path(args.report, run))

    if args.json:
        payload = {
            "mode": "simulacao" if dry_run else "execucao",
            "summary": run.counts(),
            "by_category": run.by_category(),
            "run_id": run.id,
            "operations": [operation.to_dict() for operation in run.operations],
            "report": str(report_path) if report_path else None,
            "warnings": run.warnings,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if result.failed == 0 else 1

    print("")
    if dry_run:
        print(f"SIMULAÇÃO concluída: {len(run.operations)} operações foram apenas calculadas.")
        print("Nenhum arquivo foi alterado. Use --apply para executar.")
    else:
        print(f"Execução {run.id} concluída em {run.target}.")
        print(
            f"  Concluídas: {result.moved} | "
            f"Falhas: {result.failed} | "
            f"Volume: {human_size(run.counts()['bytes'])}"
        )
        if result.moved:
            print("  Para desfazer: python caoszero.py undo --latest")

    if report_path:
        print(f"Relatório: {report_path}")

    return 0 if result.failed == 0 else 1


def cmd_undo(args: argparse.Namespace) -> int:
    state_dir = _state()
    logger = configure_logging(state_dir, verbose=args.verbose)
    journal = Journal(state_dir)

    if args.list:
        runs = journal.list_runs()
        if not runs:
            print("Nenhuma execução registrada.")
            return 0
        print(f"{'ID':28} {'INÍCIO':19} {'OPS':>4} {'CONCLUÍDAS':>10} {'ALVO'}")
        for run in runs:
            counts = run.counts()
            print(
                f"{run.id:28} {run.started_at:19} {counts['total']:>4} "
                f"{counts['concluidas']:>10} {run.target}"
            )
        return 0

    if args.run_id:
        run = journal.load(args.run_id)
    else:
        run = journal.latest(undoable_only=True)

    if run is None:
        print("Nenhuma execução com operações para desfazer.")
        return 0
    if run.dry_run:
        raise CaosZeroError("Esta execução foi uma simulação e não pode ser desfeita.")

    done = [op for op in run.operations if op.status == Status.DONE]
    if not done:
        print(f"A execução {run.id} não possui operações concluídas para desfazer.")
        return 0

    print(f"Execução: {run.id} ({run.started_at})")
    print(f"Alvo: {run.target}")
    print(f"Operações a restaurar: {len(done)}")
    for operation in done[:20]:
        destination = operation.destination or Path("?")
        print(
            f"  {relative_label(destination, Path(run.target))} -> "
            f"{relative_label(operation.source, Path(run.target))}"
        )
    if len(done) > 20:
        print(f"  ... e mais {len(done) - 20} operações.")

    if args.dry_run:
        print("\nSimulação de undo: nada foi alterado.")
        return 0

    if not args.yes and not _confirm(f"Desfazer {len(done)} operações?"):
        print("Operação cancelada. Nenhum arquivo foi alterado.")
        return 2

    result = undo_run(run, journal, logger, dry_run=False)
    print(
        f"\nUndo concluído: {result.undone} restauradas, "
        f"{result.undo_failed} não puderam ser restauradas."
    )
    if result.undo_failed:
        for operation in run.operations:
            if operation.status == Status.UNDO_FAILED:
                print(f"  - {operation.destination}: {operation.error}")
        return 1
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    info = collect_system_info(_default_target(args.target))
    if args.json:
        print(json.dumps(info, ensure_ascii=False, indent=2))
    else:
        print(render_text(info))
    return 0


def cmd_config(args: argparse.Namespace) -> int:
    state_dir = _state()

    if args.init is not None:
        destination = None if args.init == "auto" else Path(args.init).expanduser()
        written = init_config(destination, force=args.force)
        print(f"Configuração criada em {written}")
        return 0

    if args.path:
        print(default_config_path())
        return 0

    config = load_config(None)
    print(f"Arquivo: {default_config_path()}")
    print(json.dumps(config.to_dict(), ensure_ascii=False, indent=2))
    return 0


def cmd_demo(args: argparse.Namespace) -> int:
    destination = Path(args.directory).expanduser()
    root = criar_sandbox(destination)
    print(f"Ambiente de demonstração criado em: {root.resolve()}")
    print("")
    print("Próximos passos:")
    print(f"  python caoszero.py organize {root}")
    print(f"  python caoszero.py organize {root} --apply --report")
    print(f"  python caoszero.py organize {root} --archive-old 180 --apply")
    print(f"  python caoszero.py organize {root} --rename 'arquivo-{{seq:03d}}{{ext}}' --apply")
    print(f"  python caoszero.py undo --latest")
    return 0


def cmd_interactive(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    state_dir = _state()
    logger = configure_logging(state_dir, verbose=True)
    journal = Journal(state_dir)

    print("=" * 50)
    print(f"  CaosZero v{__version__} — modo interativo")
    print("=" * 50)
    default = os.environ.get("CAOSZERO_TARGET") or os.getcwd()
    try:
        raw_target = input(f"Diretório alvo [{default}]: ").strip()
    except (EOFError, KeyboardInterrupt):
        return 130
    target = Path(raw_target or default).expanduser()

    while True:
        print("")
        print(f"Alvo atual: {target}")
        print("1) Simular organização (dry-run)")
        print("2) Organizar agora")
        print("3) Relatório da última execução")
        print("4) Desfazer última execução")
        print("5) Diagnóstico do sistema")
        print("6) Criar ambiente de demonstração")
        print("0) Sair")
        try:
            choice = input("Escolha: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("")
            return 0

        if choice == "0":
            return 0
        if choice in {"1", "2"}:
            try:
                plan = build_plan(target, config=config, options=PlanOptions(), state_dir=state_dir)
            except CaosZeroError as exc:
                print(f"Erro: {exc}")
                continue
            _print_plan(plan)
            if not plan.operations:
                continue
            if choice == "1":
                print("\nSimulação: nenhum arquivo foi alterado.")
                continue
            if not _confirm(f"Executar {len(plan.operations)} operações?"):
                print("Cancelado.")
                continue
            result = execute_plan(plan, journal, logger, dry_run=False)
            print(f"Concluídas: {result.moved} | Falhas: {result.failed}")
            path = write_report(result.run, state_dir / "reports" / f"relatorio-{result.run.id}.md")
            print(f"Relatório: {path}")
        elif choice == "3":
            run = journal.latest(undoable_only=False)
            if run is None:
                print("Nenhuma execução registrada.")
                continue
            path = write_report(run, state_dir / "reports" / f"relatorio-{run.id}.md")
            print(f"Relatório: {path}")
        elif choice == "4":
            run = journal.latest(undoable_only=True)
            if run is None:
                print("Nenhuma execução para desfazer.")
                continue
            done = [op for op in run.operations if op.status == Status.DONE]
            if not done:
                print("Nada a desfazer.")
                continue
            if not _confirm(f"Desfazer {len(done)} operações de {run.id}?"):
                print("Cancelado.")
                continue
            result = undo_run(run, journal, logger, dry_run=False)
            print(f"Restauradas: {result.undone} | Falhas: {result.undo_failed}")
        elif choice == "5":
            print(render_text(collect_system_info(target)))
        elif choice == "6":
            root = criar_sandbox(Path.cwd() / "sandbox_teste")
            print(f"Ambiente criado em {root}")
        else:
            print("Opção inválida.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="caoszero",
        description=DESCRIPTION,
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"CaosZero {__version__}")
    subparsers = parser.add_subparsers(dest="command", metavar="COMANDO")

    organize = subparsers.add_parser(
        "organize",
        help="planeja ou executa a organização de uma pasta",
        description="Organiza arquivos por categoria, renomeia, arquiva antigos e gera relatório.",
    )
    organize.add_argument("target", nargs="?", help="diretório alvo (padrão: CAOSZERO_TARGET ou .)")
    organize.add_argument("--apply", action="store_true", help="executa de verdade (padrão: simular)")
    organize.add_argument("-r", "--recursive", action="store_true", help="inclui subdiretórios")
    organize.add_argument("--hidden", action="store_true", help="inclui arquivos ocultos")
    organize.add_argument("--pattern", help="filtra nomes por glob, ex.: '*.pdf'")
    organize.add_argument("--older-than", type=int, metavar="DIAS", help="somente arquivos mais antigos que N dias")
    organize.add_argument("--archive-old", type=int, metavar="DIAS", help="move arquivos com N+ dias para Arquivo/AAAA")
    organize.add_argument("--rename", metavar="PADRAO", help="renomeia usando {name}, {ext}, {seq}, {date}")
    organize.add_argument("--rename-only", action="store_true", help="renomeia no lugar, sem criar categorias")
    organize.add_argument("--category", metavar="NOME", help="restringe a uma categoria")
    organize.add_argument("--min-size", type=_size_arg, metavar="TAM", help="tamanho mínimo, ex.: 10KB")
    organize.add_argument("--max-size", type=_size_arg, metavar="TAM", help="tamanho máximo, ex.: 2GB")
    organize.add_argument("--report", nargs="?", const="auto", metavar="ARQUIVO", help="grava relatório .md/.csv/.json (sem valor: automático)")
    organize.add_argument("--json", action="store_true", help="saída JSON para automação")
    organize.add_argument("-y", "--yes", action="store_true", help="não pede confirmação")
    organize.add_argument("-v", "--verbose", action="store_true", help="log detalhado")
    organize.add_argument("--config", type=Path, help="arquivo de configuração JSON")
    organize.set_defaults(handler=cmd_organize)

    undo = subparsers.add_parser(
        "undo",
        help="desfaz uma execução anterior",
        description="Restaura os arquivos movidos por uma execução registrada no journal.",
    )
    undo.add_argument("run_id", nargs="?", help="ID da execução (padrão: última)")
    undo.add_argument("--latest", action="store_true", help="usa a execução mais recente (padrão)")
    undo.add_argument("--list", action="store_true", help="lista execuções registradas")
    undo.add_argument("--dry-run", action="store_true", help="apenas mostra o que seria restaurado")
    undo.add_argument("-y", "--yes", action="store_true", help="não pede confirmação")
    undo.add_argument("-v", "--verbose", action="store_true", help="log detalhado")
    undo.set_defaults(handler=cmd_undo)

    doctor = subparsers.add_parser(
        "doctor",
        help="mostra CPU, memória, disco, processo e permissões",
        description="Diagnóstico dos recursos do sistema operacional usados pela aplicação.",
    )
    doctor.add_argument("target", nargs="?", help="diretório para analisar o disco (padrão: .)")
    doctor.add_argument("--json", action="store_true", help="saída JSON")
    doctor.set_defaults(handler=cmd_doctor)

    config = subparsers.add_parser(
        "config",
        help="mostra ou cria a configuração",
        description="Exibe a configuração efetiva ou grava um arquivo de exemplo.",
    )
    config.add_argument("--show", action="store_true", help="mostra a configuração efetiva")
    config.add_argument("--path", action="store_true", help="mostra o caminho do arquivo de configuração")
    config.add_argument("--init", nargs="?", const="auto", metavar="ARQUIVO", help="cria configuração de exemplo")
    config.add_argument("--force", action="store_true", help="sobrescreve arquivo existente em --init")
    config.set_defaults(handler=cmd_config)

    demo = subparsers.add_parser(
        "demo",
        help="cria uma pasta de demonstração com arquivos variados",
        description="Gera um sandbox seguro para testar a aplicação.",
    )
    demo.add_argument("directory", nargs="?", default="sandbox_teste", help="pasta de destino")
    demo.set_defaults(handler=cmd_demo)

    interactive = subparsers.add_parser(
        "interactive",
        help="abre o menu interativo",
        description="Menu guiado para demonstrar a aplicação sem decorar comandos.",
    )
    interactive.add_argument("--config", type=Path, help="arquivo de configuração JSON")
    interactive.set_defaults(handler=cmd_interactive)

    return parser


def main(argv: list[str] | None = None) -> int:
    _configure_stdout()
    parser = build_parser()
    args = parser.parse_args(argv)

    handler = getattr(args, "handler", None)
    if handler is None:
        parser.print_help()
        return 0

    try:
        return int(handler(args))
    except CaosZeroError as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nInterrompido pelo usuário.", file=sys.stderr)
        return 130
    finally:
        close_logging()


if __name__ == "__main__":
    raise SystemExit(main())
