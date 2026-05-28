"""Linux system metrics aggregator."""
from __future__ import annotations

from typing import Any

import structlog

from meridian_agent.system import cpu, memory, network

log = structlog.get_logger(__name__)


async def collect_system_metrics(*, include_cgroups: bool = True) -> dict[str, Any]:
    """Gather a single snapshot of all configured system metrics."""
    scalar: dict[str, float] = {}
    for name, mod in (("cpu", cpu), ("memory", memory)):
        try:
            scalar.update(mod.collect())
        except Exception:
            log.exception(f"system.{name}.collect_failed")

    net_snapshot: dict[str, dict] = {"per_interface": {}, "tcp": {}}
    try:
        net_snapshot = network.collect()
    except Exception:
        log.exception("system.network.collect_failed")

    if include_cgroups:
        try:
            from meridian_agent.system import cgroups
            scalar.update({f"cgroup_{k}": float(v) for k, v in cgroups.collect().items()})
        except Exception:
            log.exception("system.cgroups.collect_failed")

    for k, v in net_snapshot["tcp"].items():
        scalar[f"net_{k}"] = float(v)
    return {"scalar": scalar, "network": net_snapshot["per_interface"]}
