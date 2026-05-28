"""Memory pressure via cgroup v2 memory.high squeeze."""
from __future__ import annotations

from pathlib import Path

from meridian_chaos.experiments.base import Experiment

CG = Path("/sys/fs/cgroup")


class MemoryPressureExperiment(Experiment):
    kind = "memory_pressure"
    _previous_high: str | None = None

    def validate(self) -> None:
        if "memory_high_bytes" not in self.spec.params:
            raise ValueError("memory_pressure requires params.memory_high_bytes")

    async def apply(self) -> None:
        cg_dir = Path(self.spec.params.get("cgroup_path", str(CG)))
        target = cg_dir / "memory.high"
        if self.spec.dry_run:
            return
        try:
            self._previous_high = target.read_text().strip()
        except OSError:
            self._previous_high = "max"
        target.write_text(str(self.spec.params["memory_high_bytes"]))
        self._applied = True

    async def revert(self) -> None:
        if not self._applied:
            return
        cg_dir = Path(self.spec.params.get("cgroup_path", str(CG)))
        try:
            (cg_dir / "memory.high").write_text(self._previous_high or "max")
        except OSError:
            pass
