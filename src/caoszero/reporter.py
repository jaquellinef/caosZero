"""Geração de relatórios em Markdown, CSV e JSON."""

from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path

from .models import Run, Status
from .utils import human_size, relative_label


def _escape(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


def _status_label(run: Run, status: Status) -> str:
    if run.dry_run and status == Status.PLANNED:
        return "simulada"
    return status.value


def build_markdown(run: Run) -> str:
    counts = run.counts()
    target = Path(run.target)
    mode = "Simulação (nenhum arquivo alterado)" if run.dry_run else "Execução real"
    generated = datetime.now().replace(microsecond=0).isoformat(sep=" ")

    lines = [
        "# Relatório CaosZero",
        "",
        f"- **Execução:** `{run.id}`",
        f"- **Data de início:** {run.started_at}",
        f"- **Data de término:** {run.finished_at or '—'}",
        f"- **Modo:** {mode}",
        f"- **Diretório alvo:** `{run.target}`",
        f"- **Versão:** {run.version}",
        f"- **Gerado em:** {generated}",
        "",
        "## Resumo",
        "",
        "| Indicador | Valor |",
        "| --- | ---: |",
        f"| Arquivos analisados | {counts['total']} |",
        f"| Operações planejadas | {counts['planejadas']} |",
        f"| Operações concluídas | {counts['concluidas']} |",
        f"| Operações com falha | {counts['falharam']} |",
        f"| Operações desfeitas | {counts['desfeitas']} |",
        f"| Arquivos ignorados | {counts['ignorados']} |",
        f"| Volume movimentado | {human_size(counts['bytes'])} |",
        "",
    ]

    by_category = run.by_category()
    if by_category:
        lines.extend(
            [
                "### Distribuição por categoria",
                "",
                "| Categoria | Operações |",
                "| --- | ---: |",
            ]
        )
        for category, total in by_category.items():
            lines.append(f"| {_escape(category)} | {total} |")
        lines.append("")

    if run.warnings:
        lines.extend(["## Avisos", ""])
        lines.extend(f"- {_escape(warning)}" for warning in run.warnings)
        lines.append("")

    lines.extend(
        [
            "## Operações",
            "",
            "| # | Ação | Origem | Destino | Tamanho | Status | Observação |",
            "| ---: | --- | --- | --- | ---: | --- | --- |",
        ]
    )
    for index, operation in enumerate(run.operations, start=1):
        source = relative_label(operation.source, target)
        destination = (
            relative_label(operation.destination, target) if operation.destination else "—"
        )
        detail = operation.error or operation.reason
        lines.append(
            "| {index} | {action} | `{source}` | `{destination}` | {size} | {status} | {detail} |".format(
                index=index,
                action=operation.action.label(),
                source=_escape(source),
                destination=_escape(destination),
                size=human_size(operation.size),
                status=_status_label(run, operation.status),
                detail=_escape(detail),
            )
        )
    if not run.operations:
        lines.append("| — | — | — | — | — | — | Nenhuma operação. |")
    lines.append("")

    if run.skipped:
        lines.extend(
            [
                "## Arquivos ignorados",
                "",
                "| Arquivo | Motivo |",
                "| --- | --- |",
            ]
        )
        for item in run.skipped:
            lines.append(
                f"| `{_escape(relative_label(item.path, target))}` | {_escape(item.reason)} |"
            )
        lines.append("")

    lines.extend(
        [
            "## Conceitos de Sistemas Operacionais demonstrados",
            "",
            "- **Sistema de arquivos:** varredura de diretórios e movimentação de arquivos.",
            "- **Gerenciamento de diretórios e permissões:** criação de pastas e verificação de acesso.",
            "- **Entrada/saída e logs:** gravação do journal e deste relatório em disco.",
            "- **Recursos do sistema:** checagem de espaço livre antes da execução.",
            "- **Automação:** execução não interativa por scripts e agendadores.",
            "",
            "---",
            "",
            "*Relatório gerado automaticamente pelo CaosZero.*",
            "",
        ]
    )
    return "\n".join(lines)


def build_csv(run: Run) -> str:
    import io

    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, delimiter=";", lineterminator="\n")
    writer.writerow(
        [
            "id_execucao",
            "acao",
            "origem",
            "destino",
            "tamanho_bytes",
            "status",
            "motivo",
            "erro",
        ]
    )
    for operation in run.operations:
        writer.writerow(
            [
                run.id,
                operation.action.value,
                str(operation.source),
                str(operation.destination) if operation.destination else "",
                operation.size,
                operation.status.value,
                operation.reason,
                operation.error or "",
            ]
        )
    writer.writerow([])
    writer.writerow(["arquivo_ignorado", "motivo"])
    for item in run.skipped:
        writer.writerow([str(item.path), item.reason])
    return buffer.getvalue()


def build_json(run: Run) -> str:
    payload = run.to_dict()
    payload["generated_at"] = datetime.now().replace(microsecond=0).isoformat(sep=" ")
    payload["mode"] = "simulacao" if run.dry_run else "execucao"
    return json.dumps(payload, ensure_ascii=False, indent=2)


def write_report(run: Run, path: Path | str) -> Path:
    """Escreve o relatório e devolve o caminho efetivamente usado."""
    destination = Path(path).expanduser()
    if destination.exists() and destination.is_dir():
        destination = destination / f"relatorio-{run.id}.md"
    if not destination.suffix:
        destination = destination.with_suffix(".md")

    destination.parent.mkdir(parents=True, exist_ok=True)
    suffix = destination.suffix.lower()

    if suffix == ".csv":
        content = build_csv(run)
        destination.write_text(content, encoding="utf-8-sig", newline="")
    elif suffix == ".json":
        destination.write_text(build_json(run) + "\n", encoding="utf-8", newline="\n")
    else:
        destination.write_text(build_markdown(run), encoding="utf-8", newline="\n")
    return destination
