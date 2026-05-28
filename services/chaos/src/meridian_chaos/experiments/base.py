"""Chaos experiment base class.

Every experiment implements three methods: `apply`, `revert`, `validate`.
A watchdog auto-reverts after the requested duration regardless of process state.
"""
from __future__ import annotations

import asyncio
import subprocess
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ExperimentSpec:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    kind: str = ""
    target_node: str = ""
    duration_s: float = 60.0
    params: dict[str, Any] = field(default_factory=dict)
    dry_run: bool = True


class Experiment(ABC):
    kind: str = "abstract"

    def __init__(self, spec: ExperimentSpec) -> None:
        self.spec = spec
        self._applied = False

    @abstractmethod
    async def apply(self) -> None: ...

    @abstractmethod
    async def revert(self) -> None: ...

    def validate(self) -> None:
        """Optional: raise ValueError on invalid params."""

    async def run(self, command: list[str]) -> tuple[int, str, str]:
        """Run a subprocess (or a dry-run echo) and return (rc, stdout, stderr)."""
        if self.spec.dry_run:
            return 0, f"[dry-run] {' '.join(command)}", ""
        proc = await asyncio.create_subprocess_exec(
            *command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        return (
            proc.returncode or 0,
            stdout.decode("utf-8", errors="replace"),
            stderr.decode("utf-8", errors="replace"),
        )
