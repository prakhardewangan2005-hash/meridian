"""Fill disk space via fallocate."""
from __future__ import annotations

import os
from pathlib import Path

from meridian_chaos.experiments.base import Experiment


class DiskFillExperiment(Experiment):
    kind = "disk_fill"
    _file: Path | None = None

    def validate(self) -> None:
        if "size_bytes" not in self.spec.params:
            raise ValueError("disk_fill requires params.size_bytes")

    async def apply(self) -> None:
        target = Path(self.spec.params.get("path", "/tmp/meridian-chaos-fill"))
        size = self.spec.params["size_bytes"]
        rc, _, err = await self.run(["fallocate", "-l", str(size), str(target)])
        if rc != 0:
            raise RuntimeError(f"fallocate failed: {err}")
        self._file = target
        self._applied = True

    async def revert(self) -> None:
        if self._file is None or not self._applied:
            return
        try:
            os.unlink(self._file)
        except FileNotFoundError:
            pass
