"""ChaosRunner unit tests (dry-run only — never executes real tc/iptables)."""
from __future__ import annotations

import asyncio

import pytest

from meridian_chaos.experiments import ExperimentSpec
from meridian_chaos.runner import ChaosRunner


@pytest.mark.asyncio
async def test_inject_dry_run_latency() -> None:
    runner = ChaosRunner()
    spec = ExperimentSpec(
        kind="network_latency",
        target_node="n1",
        duration_s=2.0,
        params={"delay_ms": 50, "interface": "eth0"},
        dry_run=True,
    )
    exp = await runner.inject(spec)
    assert exp.spec.id in {e["id"] for e in runner.list_active()}
    await runner.abort(exp.spec.id)
    assert runner.list_active() == []


@pytest.mark.asyncio
async def test_watchdog_auto_reverts() -> None:
    runner = ChaosRunner()
    spec = ExperimentSpec(
        kind="network_latency",
        target_node="n1",
        duration_s=0.2,
        params={"delay_ms": 1, "interface": "eth0"},
        dry_run=True,
    )
    await runner.inject(spec)
    # wait for watchdog
    await asyncio.sleep(0.5)
    assert runner.list_active() == []


@pytest.mark.asyncio
async def test_unknown_kind_raises() -> None:
    runner = ChaosRunner()
    with pytest.raises(ValueError):
        await runner.inject(
            ExperimentSpec(kind="not-a-thing", target_node="n1", duration_s=1.0)
        )


@pytest.mark.asyncio
async def test_validation_catches_missing_params() -> None:
    runner = ChaosRunner()
    with pytest.raises(ValueError):
        await runner.inject(
            ExperimentSpec(
                kind="network_latency",
                target_node="n1",
                duration_s=1.0,
                params={},  # missing delay_ms
            )
        )
