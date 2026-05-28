"""Probe distributor — computes which probes belong on which node.

Strategy (v1, simple): every probe runs on every node unless the probe carries
node selector labels. v2 will move to a constraint-solver style assignment.
"""
from __future__ import annotations

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from meridian_controller.models.node import Node
from meridian_controller.models.probe import ProbeAssignment, ProbeDefinition

log = structlog.get_logger(__name__)


async def reconcile(session: AsyncSession) -> int:
    """Ensure every enabled probe is assigned to every node.
    Returns the number of assignments created."""
    nodes = (await session.execute(select(Node))).scalars().all()
    probes = (
        await session.execute(
            select(ProbeDefinition).where(ProbeDefinition.enabled.is_(True))
        )
    ).scalars().all()
    existing = {
        (a.probe_id, a.node_id)
        for a in (await session.execute(select(ProbeAssignment))).scalars().all()
    }
    created = 0
    for probe in probes:
        for node in nodes:
            if (probe.id, node.id) in existing:
                continue
            session.add(ProbeAssignment(probe_id=probe.id, node_id=node.id))
            created += 1
    if created:
        log.info("probe_distributor.reconciled", created=created)
    return created


async def probes_for_node(
    session: AsyncSession, node_id: str
) -> list[ProbeDefinition]:
    """Return the probe definitions assigned to a node."""
    stmt = (
        select(ProbeDefinition)
        .join(ProbeAssignment, ProbeAssignment.probe_id == ProbeDefinition.id)
        .where(ProbeAssignment.node_id == node_id)
        .where(ProbeDefinition.enabled.is_(True))
    )
    res = await session.execute(stmt)
    return list(res.scalars().all())
