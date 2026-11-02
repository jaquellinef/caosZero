"""Diagnóstico de recursos do sistema operacional.

Demonstra, na prática, conceitos de processos, memória, CPU, disco,
permissões, variáveis de ambiente e limites de cgroup (containers).
"""

from __future__ import annotations

import ctypes
import getpass
import os
import platform
import shutil
import socket
import stat
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any

from .utils import human_size


class _MemoryStatusEx(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


def _windows_memory() -> dict[str, int] | None:
    try:
        status = _MemoryStatusEx()
        status.dwLength = ctypes.sizeof(_MemoryStatusEx)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):  # type: ignore[attr-defined]
            return None
        return {"total": int(status.ullTotalPhys), "available": int(status.ullAvailPhys)}
    except (AttributeError, OSError):
        return None


def _linux_memory() -> dict[str, int] | None:
    path = Path("/proc/meminfo")
    if not path.exists():
        return None
    values: dict[str, int] = {}
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if ":" not in line:
                continue
            key, raw = line.split(":", 1)
            parts = raw.strip().split()
            if parts and parts[0].isdigit():
                values[key] = int(parts[0]) * 1024
    except OSError:
        return None
    total = values.get("MemTotal")
    available = values.get("MemAvailable", values.get("MemFree"))
    if total is None:
        return None
    return {"total": total, "available": available or 0}


def _macos_memory() -> dict[str, int] | None:
    try:
        total = int(
            subprocess.check_output(["sysctl", "-n", "hw.memsize"], text=True, timeout=3).strip()
        )
        return {"total": total, "available": 0}
    except (OSError, subprocess.SubprocessError, ValueError):
        return None


def memory_info() -> dict[str, int] | None:
    if os.name == "nt":
        return _windows_memory()
    if sys.platform == "darwin":
        return _macos_memory()
    return _linux_memory()


def _cgroup_memory_limit() -> int | None:
    for candidate in (
        "/sys/fs/cgroup/memory.max",
        "/sys/fs/cgroup/memory/memory.limit_in_bytes",
    ):
        path = Path(candidate)
        if not path.exists():
            continue
        try:
            raw = path.read_text(encoding="utf-8").strip()
        except OSError:
            continue
        if raw.isdigit():
            return int(raw)
    return None


def _cgroup_cpu_limit() -> float | None:
    try:
        raw = Path("/sys/fs/cgroup/cpu.max").read_text(encoding="utf-8").split()
        if raw[0] != "max":
            return round(int(raw[0]) / int(raw[1]), 2)
    except (OSError, ValueError, IndexError):
        pass
    try:
        quota = int(Path("/sys/fs/cgroup/cpu/cpu.cfs_quota_us").read_text().strip())
        period = int(Path("/sys/fs/cgroup/cpu/cpu.cfs_period_us").read_text().strip())
        if quota > 0 and period > 0:
            return round(quota / period, 2)
    except (OSError, ValueError):
        pass
    return None


def _uptime_seconds() -> float | None:
    if os.name == "nt":
        try:
            return ctypes.windll.kernel32.GetTickCount64() / 1000.0  # type: ignore[attr-defined]
        except (AttributeError, OSError):
            return None
    try:
        return float(Path("/proc/uptime").read_text().split()[0])
    except (OSError, ValueError, IndexError):
        return None


def _permission_string(mode: int) -> str:
    return stat.filemode(mode)


def collect_system_info(target: Path | str = ".") -> dict[str, Any]:
    """Coleta um retrato dos recursos que a aplicação utiliza."""
    target_path = Path(target).expanduser().resolve()
    memory = memory_info()
    usage = shutil.disk_usage(target_path if target_path.exists() else Path.cwd())

    cpu_count = os.cpu_count() or 1
    cgroup_cpu = _cgroup_cpu_limit()
    effective_cpu = min(cpu_count, cgroup_cpu) if cgroup_cpu else cpu_count

    load: list[float] | None = None
    try:
        load = [round(value, 2) for value in os.getloadavg()]
    except (AttributeError, OSError):
        load = None

    try:
        info = target_path.stat()
        permissions = {
            "octal": oct(stat.S_IMODE(info.st_mode)),
            "simbolica": _permission_string(info.st_mode),
            "leitura": os.access(target_path, os.R_OK),
            "escrita": os.access(target_path, os.W_OK),
            "execucao": os.access(target_path, os.X_OK),
            "device": str(info.st_dev),
        }
    except OSError:
        permissions = {}

    env_keys = [
        "SHELL",
        "LANG",
        "XDG_DATA_HOME",
        "CAOSZERO_HOME",
        "CAOSZERO_CONFIG",
        "CAOSZERO_TARGET",
        "TEMP",
        "TMPDIR",
    ]
    environment = {key: os.environ[key] for key in env_keys if key in os.environ}
    environment["PATH_entradas"] = len(os.environ.get("PATH", "").split(os.pathsep))

    return {
        "sistema": {
            "nome": platform.system(),
            "release": platform.release(),
            "versao": platform.version(),
            "arquitetura": platform.machine(),
            "hostname": socket.gethostname(),
            "python": platform.python_version(),
        },
        "processo": {
            "pid": os.getpid(),
            "ppid": os.getppid(),
            "usuario": getpass.getuser(),
            "threads_ativas": threading.active_count(),
            "executavel": sys.executable,
            "uptime_s": _uptime_seconds(),
        },
        "cpu": {
            "nucleos": cpu_count,
            "nucleos_efetivos": effective_cpu,
            "limite_cgroup": cgroup_cpu,
            "load_average": load,
        },
        "memoria": {
            "total": memory["total"] if memory else None,
            "disponivel": memory["available"] if memory else None,
            "limite_cgroup": _cgroup_memory_limit(),
        },
        "disco": {
            "total": usage.total,
            "usado": usage.used,
            "livre": usage.free,
            "percentual_usado": round((usage.used / usage.total) * 100, 1) if usage.total else 0,
        },
        "alvo": {
            "caminho": str(target_path),
            "existe": target_path.exists(),
            "permissoes": permissions,
        },
        "ambiente": environment,
    }


def render_text(info: dict[str, Any]) -> str:
    """Formata o diagnóstico para leitura no terminal."""
    system = info["sistema"]
    process = info["processo"]
    cpu = info["cpu"]
    memory = info["memoria"]
    disk = info["disco"]
    target = info["alvo"]
    env = info["ambiente"]

    memory_total = human_size(memory["total"]) if memory["total"] else "indisponível"
    memory_available = human_size(memory["disponivel"]) if memory["disponivel"] else "indisponível"
    cgroup_memory = human_size(memory["limite_cgroup"]) if memory.get("limite_cgroup") else "sem limite"
    uptime = f"{process['uptime_s'] / 3600:.1f} h" if process["uptime_s"] else "indisponível"
    load = ", ".join(str(value) for value in cpu["load_average"]) if cpu["load_average"] else "indisponível"

    lines = [
        "==============================================",
        "  CaosZero — Diagnóstico do Sistema",
        "==============================================",
        "",
        "[Sistema operacional]",
        f"  Nome...............: {system['nome']} {system['release']}",
        f"  Arquitetura........: {system['arquitetura']}",
        f"  Hostname...........: {system['hostname']}",
        f"  Python.............: {system['python']}",
        "",
        "[Processo atual]",
        f"  PID................: {process['pid']}",
        f"  PPID...............: {process['ppid']}",
        f"  Usuário............: {process['usuario']}",
        f"  Threads ativas.....: {process['threads_ativas']}",
        f"  Uptime.............: {uptime}",
        "",
        "[CPU e memória]",
        f"  Núcleos............: {cpu['nucleos']} (efetivos: {cpu['nucleos_efetivos']})",
        f"  Limite de CPU......: {cpu['limite_cgroup'] or 'sem limite de cgroup'}",
        f"  Load average.......: {load}",
        f"  Memória total......: {memory_total}",
        f"  Memória disponível.: {memory_available}",
        f"  Limite de memória..: {cgroup_memory}",
        "",
        "[Armazenamento do alvo]",
        f"  Caminho............: {target['caminho']}",
        f"  Total..............: {human_size(disk['total'])}",
        f"  Usado..............: {human_size(disk['usado'])} ({disk['percentual_usado']}%)",
        f"  Livre..............: {human_size(disk['livre'])}",
        f"  Permissões.........: {target['permissoes'].get('octal', '—')} "
        f"{target['permissoes'].get('simbolica', '')}",
        f"  Escrita permitida..: {'sim' if target['permissoes'].get('escrita') else 'não'}",
        "",
        "[Variáveis de ambiente]",
    ]
    if env:
        for key, value in env.items():
            lines.append(f"  {key:18}: {value}")
    else:
        lines.append("  Nenhuma variável monitorada definida.")
    lines.append("")
    return "\n".join(lines)
