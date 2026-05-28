"""Chaos orchestrator — delegates to the chaos service over HTTP."""
from __future__ import annotations

from typing import Any

import httpx
import structlog

from meridian_controller.config import ChaosConfig

log = structlog.get_logger(__name__)


class ChaosOrchestrator:
    def __init__(self, cfg: ChaosConfig) -> None:
        self._cfg = cfg

    async def inject(self, experiment: dict[str, Any]) -> dict[str, Any]:
        experiment.setdefault("dry_run", self._cfg.default_dry_run)
        async with httpx.AsyncClient(timeout=10.0) as c:
            r = await c.post(
                f"{self._cfg.service_url}/inject", json=experiment
            )
            r.raise_for_status()
        log.info(
            "chaos.injected",
            kind=experiment.get("kind"),
            target_node=experiment.get("target_node"),
            dry_run=experiment["dry_run"],
        )
        return r.json()

    async def list_active(self) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=10.0) as c:
            r = await c.get(f"{self._cfg.service_url}/experiments")
            r.raise_for_status()
        return r.json()

    async def abort(self, experiment_id: str) -> None:
        async with httpx.AsyncClient(timeout=10.0) as c:
            r = await c.delete(f"{self._cfg.service_url}/experiments/{experiment_id}")
            r.raise_for_status()
