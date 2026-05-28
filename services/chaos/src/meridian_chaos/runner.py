"""Chaos runner — manages experiment lifecycle with watchdog auto-revert."""
from __future__ import annotations

import asyncio
from contextlib import suppress

import structlog

from meridian_chaos.experiments import REGISTRY, Experiment, ExperimentSpec

log = structlog.get_logger(__name__)


class ChaosRunner:
    """Tracks active experiments. Each experiment gets a watchdog task that
    reverts it after its duration regardless of caller behavior."""

    def __init__(self, *, max_concurrent: int = 5) -> None:
        self._active: dict[str, Experiment] = {}
        self._tasks: dict[str, asyncio.Task] = {}
        self._sem = asyncio.Semaphore(max_concurrent)

    async def inject(self, spec: ExperimentSpec) -> Experiment:
        cls = REGISTRY.get(spec.kind)
        if cls is None:
            raise ValueError(f"unknown experiment kind: {spec.kind!r}")
        exp = cls(spec)
        exp.validate()
        await self._sem.acquire()
        try:
            await exp.apply()
        except Exception:
            self._sem.release()
            raise
        self._active[spec.id] = exp
        self._tasks[spec.id] = asyncio.create_task(
            self._watchdog(spec.id, spec.duration_s),
            name=f"chaos-watchdog:{spec.id}",
        )
        log.info(
            "chaos.injected",
            id=spec.id,
            kind=spec.kind,
            duration_s=spec.duration_s,
            dry_run=spec.dry_run,
        )
        return exp

    async def abort(self, experiment_id: str) -> bool:
        exp = self._active.get(experiment_id)
        if exp is None:
            return False
        task = self._tasks.pop(experiment_id, None)
        if task is not None:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task
        await self._revert(experiment_id)
        return True

    def list_active(self) -> list[dict]:
        return [
            {
                "id": e.spec.id,
                "kind": e.spec.kind,
                "target_node": e.spec.target_node,
                "duration_s": e.spec.duration_s,
                "params": e.spec.params,
                "dry_run": e.spec.dry_run,
            }
            for e in self._active.values()
        ]

    async def shutdown(self) -> None:
        """Revert everything still in flight."""
        for eid in list(self._active.keys()):
            await self.abort(eid)

    async def _watchdog(self, experiment_id: str, duration_s: float) -> None:
        try:
            await asyncio.sleep(duration_s)
        except asyncio.CancelledError:
            return
        await self._revert(experiment_id)

    async def _revert(self, experiment_id: str) -> None:
        exp = self._active.pop(experiment_id, None)
        if exp is None:
            return
        try:
            await exp.revert()
            log.info("chaos.reverted", id=experiment_id, kind=exp.spec.kind)
        except Exception:
            log.exception("chaos.revert_failed", id=experiment_id)
        finally:
            self._sem.release()
