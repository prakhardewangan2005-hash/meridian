"""Chaos: network-partition lifecycle via the runner (dry-run)."""
from __future__ import annotations

import asyncio

import pytest

from meridian_chaos.experiments import ExperimentSpec
from meridian_chaos.runner import ChaosRunner

pytestmark = pytest.mark.asyncio


async def test_partition_injects_and_reverts() -> None:
    runner = ChaosRunner()
    spec = ExperimentSpec(
        kind="network_partition",
        target_node="node-a",
        duration_s=0.3,
        params={"peer_ip": "10.0.0.99"},
        dry_run=True,
    )
    exp = await runner.inject(spec)
    assert any(e["id"] == exp.spec.id for e in runner.list_active())
    # watchdog auto-reverts after duration
    await asyncio.sleep(0.6)
    assert runner.list_active() == []


async def test_partition_requires_peer_ip() -> None:
    runner = ChaosRunner()
    with pytest.raises(ValueError):
        await runner.inject(
            ExperimentSpec(
                kind="network_partition", target_node="node-a",
                duration_s=1.0, params={},  # missing peer_ip
            )
        )


async def test_concurrent_experiments_capped() -> None:
    runner = ChaosRunner(max_concurrent=2)
    specs = [
        ExperimentSpec(
            kind="network_latency", target_node=f"n{i}", duration_s=2.0,
            params={"interface": "eth0", "delay_ms": 10}, dry_run=True,
        )
        for i in range(2)
    ]
    for s in specs:
        await runner.inject(s)
    assert len(runner.list_active()) == 2
    await runner.shutdown()
    assert runner.list_active() == []
