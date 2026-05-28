"""cgroup v2 unified-hierarchy reader.

We deliberately only support v2 — v1 is on its way out and the legacy paths
add a lot of branching. If the host is on v1, this module returns empty.
"""
from __future__ import annotations

from pathlib import Path

from meridian_agent.system.procfs import SYS

CGROUP_ROOT = SYS / "fs/cgroup"


def _is_v2() -> bool:
    # v2 unified hierarchy uses cgroup.controllers at root
    return (CGROUP_ROOT / "cgroup.controllers").is_file()


def _read_int(path: Path) -> int | None:
    try:
        return int(path.read_text().strip())
    except (OSError, ValueError):
        return None


def _read_kv(path: Path) -> dict[str, int]:
    out: dict[str, int] = {}
    try:
        text = path.read_text()
    except OSError:
        return out
    for line in text.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            try:
                out[parts[0]] = int(parts[1])
            except ValueError:
                continue
    return out


def collect() -> dict[str, float]:
    if not _is_v2():
        return {}
    out: dict[str, float] = {}

    mem = _read_int(CGROUP_ROOT / "memory.current")
    if mem is not None:
        out["memory_current_bytes"] = float(mem)
    mem_max = (CGROUP_ROOT / "memory.max").read_text().strip() if (CGROUP_ROOT / "memory.max").is_file() else "max"
    if mem_max != "max":
        try:
            out["memory_max_bytes"] = float(mem_max)
        except ValueError:
            pass

    cpu_stat = _read_kv(CGROUP_ROOT / "cpu.stat")
    if "usage_usec" in cpu_stat:
        out["cpu_usage_usec"] = float(cpu_stat["usage_usec"])
    if "throttled_usec" in cpu_stat:
        out["cpu_throttled_usec"] = float(cpu_stat["throttled_usec"])

    pids_current = _read_int(CGROUP_ROOT / "pids.current")
    if pids_current is not None:
        out["pids_current"] = float(pids_current)

    pressure = CGROUP_ROOT / "memory.pressure"
    if pressure.is_file():
        try:
            for line in pressure.read_text().splitlines():
                # "some avg10=0.00 avg60=0.00 avg300=0.00 total=12345"
                parts = line.split()
                if not parts:
                    continue
                kind = parts[0]
                for kv in parts[1:]:
                    if "=" not in kv:
                        continue
                    k, v = kv.split("=", 1)
                    try:
                        out[f"memory_pressure_{kind}_{k}"] = float(v)
                    except ValueError:
                        continue
        except OSError:
            pass

    return out
