"""CPU pressure via stress-ng."""
from __future__ import annotations

import asyncio

from meridian_chaos.experiments.base import Experiment


class CPUPressureExperiment(Experiment):
    kind = "cpu_pressure"

    def __init__(self, spec):  # type: ignore[no-untyped-def]
        super().__init__(spec)
        self._proc: asyncio.subprocess.Process | None = None

    async def apply(self) -> None:
        cores = self.spec.params.get("cores", 1)
        if self.spec.dry_run:
            return
        self._proc = await asyncio.create_subprocess_exec(
            "stress-ng", "--cpu", str(cores), "--timeout",
            f"{int(self.spec.duration_s)}s",
        )
        self._applied = True

    async def revert(self) -> None:
        if self._proc is not None and self._proc.returncode is None:
            self._proc.terminate()
            try:
                await asyncio.wait_for(self._proc.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                self._proc.kill()
