"""Probe CRUD."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from meridian_controller.db import get_session
from meridian_controller.models.probe import ProbeDefinition

router = APIRouter()


class ProbePayload(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    probe_type: str
    target: str
    interval_s: float = 30.0
    timeout_s: float = 5.0
    jitter_s: float = 2.0
    params: dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True


class ProbeView(ProbePayload):
    id: int


def _to_view(p: ProbeDefinition) -> ProbeView:
    return ProbeView(
        id=p.id,
        name=p.name,
        probe_type=p.probe_type,
        target=p.target,
        interval_s=p.interval_s,
        timeout_s=p.timeout_s,
        jitter_s=p.jitter_s,
        params=p.params,
        enabled=p.enabled,
    )


@router.get("")
async def list_probes(
    session: AsyncSession = Depends(get_session),
) -> list[ProbeView]:
    res = await session.execute(
        select(ProbeDefinition).order_by(ProbeDefinition.id)
    )
    return [_to_view(p) for p in res.scalars()]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_probe(
    payload: ProbePayload,
    session: AsyncSession = Depends(get_session),
) -> ProbeView:
    p = ProbeDefinition(**payload.model_dump())
    session.add(p)
    await session.commit()
    await session.refresh(p)
    return _to_view(p)


@router.put("/{probe_id}")
async def update_probe(
    probe_id: int,
    payload: ProbePayload,
    session: AsyncSession = Depends(get_session),
) -> ProbeView:
    p = await session.get(ProbeDefinition, probe_id)
    if p is None:
        raise HTTPException(status_code=404, detail="probe not found")
    for k, v in payload.model_dump().items():
        setattr(p, k, v)
    await session.commit()
    await session.refresh(p)
    return _to_view(p)


@router.delete("/{probe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_probe(
    probe_id: int,
    session: AsyncSession = Depends(get_session),
) -> None:
    res = await session.execute(
        delete(ProbeDefinition).where(ProbeDefinition.id == probe_id)
    )
    if res.rowcount == 0:
        raise HTTPException(status_code=404, detail="probe not found")
    await session.commit()
