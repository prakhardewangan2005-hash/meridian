"""Chaos experiment trigger / list / abort."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field

from meridian_controller.config import ControllerSettings
from meridian_controller.services.chaos_orchestrator import ChaosOrchestrator


def _orchestrator_dep() -> ChaosOrchestrator:
    # Lazily resolved against the app's settings — overridden in tests.
    from meridian_controller.app import get_settings  # local to avoid circular import

    settings: ControllerSettings = get_settings()
    return ChaosOrchestrator(settings.chaos)


router = APIRouter()


class InjectPayload(BaseModel):
    kind: str = Field(
        pattern=r"^(network_latency|network_loss|network_partition|cpu_pressure|memory_pressure|disk_fill)$"
    )
    target_node: str
    duration_s: float = Field(ge=1.0, le=3600.0)
    params: dict[str, Any] = Field(default_factory=dict)
    dry_run: bool = True


@router.post("/inject", status_code=status.HTTP_202_ACCEPTED)
async def inject(
    payload: InjectPayload,
    orch: ChaosOrchestrator = Depends(_orchestrator_dep),
) -> dict[str, Any]:
    return await orch.inject(payload.model_dump())


@router.get("")
async def list_experiments(
    orch: ChaosOrchestrator = Depends(_orchestrator_dep),
) -> list[dict[str, Any]]:
    return await orch.list_active()


@router.delete("/{experiment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def abort(
    experiment_id: str,
    orch: ChaosOrchestrator = Depends(_orchestrator_dep),
) -> None:
    await orch.abort(experiment_id)
