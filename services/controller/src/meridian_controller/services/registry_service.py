"""Node registry: registration, heartbeat, healthy-set tracking."""
from __future__ import annotations

import datetime as dt
from typing import Any

import structlog
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from meridian_controller.models.node import Node

log = structlog.get_logger(__name__)


async def register_or_update(session: AsyncSession, payload: dict[str, Any]) -> Node:
    """Upsert a node record."""
    node_id = payload["node_id"]
    stmt = pg_insert(Node).values(
        id=node_id,
        hostname=payload.get("hostname", ""),
        kernel=payload.get("kernel", ""),
        arch=payload.get("arch", ""),
        python_version=payload.get("python_version", ""),
        labels=payload.get("labels", {}),
        registered_at=dt.datetime.now(dt.UTC),
        last_heartbeat=dt.datetime.now(dt.UTC),
        state="healthy",
    ).on_conflict_do_update(
        index_elements=[Node.id],
        set_={
            "hostname": payload.get("hostname", ""),
            "kernel": payload.get("kernel", ""),
            "arch": payload.get("arch", ""),
            "python_version": payload.get("python_version", ""),
            "last_heartbeat": dt.datetime.now(dt.UTC),
            "state": "healthy",
        },
    ).returning(Node)
    res = await session.execute(stmt)
    node = res.scalar_one()
    log.info("node.registered", node_id=node_id)
    return node


async def heartbeat(session: AsyncSession, node_id: str) -> bool:
    """Update last_heartbeat. Returns True if the node exists."""
    res = await session.execute(
        update(Node)
        .where(Node.id == node_id)
        .values(last_heartbeat=dt.datetime.now(dt.UTC), state="healthy")
    )
    return res.rowcount > 0


async def list_nodes(session: AsyncSession) -> list[Node]:
    res = await session.execute(select(Node).order_by(Node.id))
    return list(res.scalars().all())


async def mark_stale_nodes(session: AsyncSession, timeout_s: float) -> int:
    """Mark nodes that haven't heartbeated within timeout as unhealthy."""
    cutoff = dt.datetime.now(dt.UTC) - dt.timedelta(seconds=timeout_s)
    res = await session.execute(
        update(Node)
        .where(Node.last_heartbeat < cutoff)
        .where(Node.state == "healthy")
        .values(state="unhealthy")
    )
    if res.rowcount:
        log.warning("nodes.marked_stale", count=res.rowcount, timeout_s=timeout_s)
    return res.rowcount
