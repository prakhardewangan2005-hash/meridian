"""Node registration, heartbeat, listing."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from meridian_controller.db import get_session
from meridian_controller.services import registry_service

router = APIRouter()


class RegisterPayload(BaseModel):
    node_id: str = Field(min_length=1, max_length=128)
    hostname: str = ""
    kernel: str = ""
    arch: str = ""
    python_version: str = ""
    labels: dict[str, str] = Field(default_factory=dict)


class HeartbeatPayload(BaseModel):
    alive: bool = True


class NodeView(BaseModel):
    id: str
    hostname: str
    kernel: str
    arch: str
    state: str
    last_heartbeat: str
    labels: dict[str, Any]


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterPayload,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    node = await registry_service.register_or_update(session, payload.model_dump())
    await session.commit()
    return {"node_id": node.id, "state": node.state}


@router.post("/{node_id}/heartbeat")
async def heartbeat(
    node_id: str,
    _payload: HeartbeatPayload,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    ok = await registry_service.heartbeat(session, node_id)
    if not ok:
        raise HTTPException(status_code=404, detail="node not registered")
    await session.commit()
    return {"node_id": node_id, "ack": "ok"}


@router.get("")
async def list_nodes(
    session: AsyncSession = Depends(get_session),
) -> list[NodeView]:
    nodes = await registry_service.list_nodes(session)
    return [
        NodeView(
            id=n.id,
            hostname=n.hostname,
            kernel=n.kernel,
            arch=n.arch,
            state=n.state,
            last_heartbeat=n.last_heartbeat.isoformat(),
            labels=n.labels,
        )
        for n in nodes
    ]
