"""Lightweight integration test of the agent startup/shutdown path."""
from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from meridian_agent.config import AgentSettings, BufferConfig, ExporterConfig
from meridian_agent.probes.base import Probe, ProbeResult
from meridian_agent.runner import AgentRunner


class FakeProbe(Probe):
    probe_type = "fake"

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)  # type: ignore[arg-type]
        self.calls = 0

    async def execute(self) -> ProbeResult:
        self.calls += 1
        return ProbeResult.ok(self, latency_s=0.001, attempt=self.calls)


@pytest.mark.integration
async def test_runner_shuts_down_cleanly(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Disable heartbeat/log shipper by pointing to dummy unreachable URL
    monkeypatch.setenv("MERIDIAN_AGENT_NODE_ID", "test-node")
    settings = AgentSettings(
        node_id="test-node",
        buffer=BufferConfig(path=tmp_path / "buf"),
        exporter=ExporterConfig(bind_port=0),
    )
    # Skip the heartbeat by faking the ssl context dependencies — short-circuit via shutdown
    probe = FakeProbe(name="fp", target="x", interval_s=0.1, timeout_s=1.0, jitter_s=0.0)
    runner = AgentRunner(settings, [probe])

    async def stop_soon():
        await asyncio.sleep(0.5)
        runner._shutdown.set()

    # we don't actually expect heartbeat to succeed; we just want the loop to spin
    # and exit on the shutdown event without hanging
    try:
        await asyncio.wait_for(
            asyncio.gather(runner.run(), stop_soon(), return_exceptions=True),
            timeout=5.0,
        )
    except asyncio.TimeoutError:
        pytest.fail("runner did not shut down within 5s")
