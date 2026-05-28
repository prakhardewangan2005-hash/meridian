"""CPU stats from /proc/stat with delta computation, plus /proc/loadavg."""
from __future__ import annotations

import os
from dataclasses import dataclass

from meridian_agent.system.procfs import PROC, read_lines


@dataclass(slots=True)
class CPUSnapshot:
    user: int
    nice: int
    system: int
    idle: int
    iowait: int
    irq: int
    softirq: int
    steal: int
    guest: int

    @property
    def total(self) -> int:
        return (self.user + self.nice + self.system + self.idle + self.iowait
                + self.irq + self.softirq + self.steal)

    @property
    def busy(self) -> int:
        return self.total - self.idle - self.iowait


def _snapshot() -> CPUSnapshot:
    for line in read_lines(PROC / "stat"):
        if line.startswith("cpu "):
            ints = [int(p) for p in line.split()[1:]]
            while len(ints) < 9:
                ints.append(0)
            return CPUSnapshot(*ints[:9])
    raise RuntimeError("/proc/stat: no aggregate cpu line")


_last: CPUSnapshot | None = None


def collect() -> dict[str, float]:
    """Percent-of-time deltas since previous call (zeros on first call)."""
    global _last
    curr = _snapshot()
    out: dict[str, float] = {"cpu_count": float(os.cpu_count() or 0)}

    try:
        load = (PROC / "loadavg").read_text().split()
        out["load_1m"], out["load_5m"], out["load_15m"] = (float(x) for x in load[:3])
    except (OSError, ValueError, IndexError):
        pass

    if _last is not None:
        total = curr.total - _last.total
        if total > 0:
            out["cpu_user_pct"] = 100 * (curr.user - _last.user) / total
            out["cpu_system_pct"] = 100 * (curr.system - _last.system) / total
            out["cpu_idle_pct"] = 100 * (curr.idle - _last.idle) / total
            out["cpu_iowait_pct"] = 100 * (curr.iowait - _last.iowait) / total
            out["cpu_steal_pct"] = 100 * (curr.steal - _last.steal) / total
            out["cpu_busy_pct"] = 100 * (curr.busy - _last.busy) / total
    _last = curr
    return out
