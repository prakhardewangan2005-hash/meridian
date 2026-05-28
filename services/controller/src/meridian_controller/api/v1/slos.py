"""SLO CRUD + burn-rate query."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from meridian_controller.db import get_session
from meridian_controller.models.slo import SLOBudgetSnapshot, SLODefinition

router = APIRouter()


class SLOPayload(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    service: str
    description: str = ""
    sli_query: str
    objective_pct: float = Field(ge=0.0, le=100.0)
    window_days: int = Field(ge=1, le=365)


class SLOView(SLOPayload):
    id: int


class BurnRateView(BaseModel):
    slo_id: int
    sli_value: float
    burn_rate_1h: float
    burn_rate_6h: float
    error_budget_remaining_pct: float
    captured_at: str


def _to_view(s: SLODefinition) -> SLOView:
    return SLOView(
        id=s.id,
        name=s.name,
        service=s.service,
        description=s.description,
        sli_query=s.sli_query,
        objective_pct=s.objective_pct,
        window_days=s.window_days,
    )


@router.get("")
async def list_slos(session: AsyncSession = Depends(get_session)) -> list[SLOView]:
    res = await session.execute(select(SLODefinition).order_by(SLODefinition.id))
    return [_to_view(s) for s in res.scalars()]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_slo(
    payload: SLOPayload,
    session: AsyncSession = Depends(get_session),
) -> SLOView:
    s = SLODefinition(**payload.model_dump())
    session.add(s)
    await session.commit()
    await session.refresh(s)
    return _to_view(s)


@router.get("/{slo_id}/burn-rate")
async def burn_rate(
    slo_id: int,
    session: AsyncSession = Depends(get_session),
) -> BurnRateView:
    snap = (
        await session.execute(
            select(SLOBudgetSnapshot)
            .where(SLOBudgetSnapshot.slo_id == slo_id)
            .order_by(desc(SLOBudgetSnapshot.captured_at))
            .limit(1)
        )
    ).scalar_one_or_none()
    if snap is None:
        raise HTTPException(status_code=404, detail="no burn-rate snapshots yet")
    return BurnRateView(
        slo_id=snap.slo_id,
        sli_value=snap.sli_value,
        burn_rate_1h=snap.burn_rate_1h,
        burn_rate_6h=snap.burn_rate_6h,
        error_budget_remaining_pct=snap.error_budget_remaining_pct,
        captured_at=snap.captured_at.isoformat(),
    )
