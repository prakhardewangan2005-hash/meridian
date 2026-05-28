"""Incident lifecycle."""
from __future__ import annotations

import datetime as dt

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from meridian_controller.db import get_session
from meridian_controller.models.incident import Incident

router = APIRouter()


class IncidentPayload(BaseModel):
    code: str = Field(pattern=r"^INC-\d+$")
    title: str
    severity: str = Field(pattern=r"^SEV[1-4]$")
    description: str = ""
    postmortem_url: str = ""


class IncidentView(IncidentPayload):
    id: int
    status: str
    opened_at: str
    closed_at: str | None


def _to_view(i: Incident) -> IncidentView:
    return IncidentView(
        id=i.id,
        code=i.code,
        title=i.title,
        severity=i.severity,
        status=i.status,
        description=i.description,
        postmortem_url=i.postmortem_url,
        opened_at=i.opened_at.isoformat(),
        closed_at=i.closed_at.isoformat() if i.closed_at else None,
    )


@router.get("")
async def list_incidents(
    session: AsyncSession = Depends(get_session),
) -> list[IncidentView]:
    res = await session.execute(select(Incident).order_by(Incident.id.desc()))
    return [_to_view(i) for i in res.scalars()]


@router.post("", status_code=status.HTTP_201_CREATED)
async def open_incident(
    payload: IncidentPayload,
    session: AsyncSession = Depends(get_session),
) -> IncidentView:
    i = Incident(**payload.model_dump())
    session.add(i)
    await session.commit()
    await session.refresh(i)
    return _to_view(i)


@router.put("/{incident_id}")
async def update_incident(
    incident_id: int,
    payload: IncidentPayload,
    session: AsyncSession = Depends(get_session),
) -> IncidentView:
    i = await session.get(Incident, incident_id)
    if i is None:
        raise HTTPException(status_code=404, detail="incident not found")
    for k, v in payload.model_dump().items():
        setattr(i, k, v)
    await session.commit()
    await session.refresh(i)
    return _to_view(i)


@router.post("/{incident_id}/close")
async def close_incident(
    incident_id: int,
    session: AsyncSession = Depends(get_session),
) -> IncidentView:
    i = await session.get(Incident, incident_id)
    if i is None:
        raise HTTPException(status_code=404, detail="incident not found")
    i.status = "closed"
    i.closed_at = dt.datetime.now(dt.UTC)
    await session.commit()
    await session.refresh(i)
    return _to_view(i)
