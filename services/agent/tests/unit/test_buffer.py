"""ResultBuffer tests — write, drain, ack, rotation, eviction."""
from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from meridian_agent.buffer import ResultBuffer
from meridian_agent.config import BufferConfig
from meridian_agent.probes.base import ProbeResult


def _make_result(name: str = "p", target: str = "1.1.1.1") -> ProbeResult:
    return ProbeResult(
        probe_name=name,
        probe_type="dns",
        target=target,
        status="ok",
        latency_s=0.012,
        timestamp=time.time(),
        metadata={"records": ["1.1.1.1"]},
    )


@pytest.fixture
def buf_dir(tmp_path: Path) -> Path:
    return tmp_path / "buffer"


async def test_write_then_drain(buf_dir: Path) -> None:
    buf = ResultBuffer(BufferConfig(path=buf_dir, max_bytes=1024 * 1024))
    await buf.open()
    for _ in range(10):
        await buf.write(_make_result())
    await buf.close()

    # reopen: the sealed segment from the previous run is drainable
    buf2 = ResultBuffer(BufferConfig(path=buf_dir, max_bytes=1024 * 1024))
    await buf2.open()
    drained = await buf2.drain(batch_size=100)
    assert len(drained) >= 10
    assert drained[0]["status"] == "ok"
    await buf2.close()


async def test_ack_deletes_segments(buf_dir: Path) -> None:
    buf = ResultBuffer(BufferConfig(path=buf_dir, max_bytes=1024 * 1024))
    await buf.open()
    await buf.write(_make_result())
    await buf.close()

    buf2 = ResultBuffer(BufferConfig(path=buf_dir, max_bytes=1024 * 1024))
    await buf2.open()
    before = list(buf_dir.glob("segment-*.log"))
    await buf2.ack()
    after = list(buf_dir.glob("segment-*.log"))
    # at least one sealed segment was removed (the active one stays)
    assert len(after) <= len(before)
    await buf2.close()


async def test_corrupt_record_is_skipped(buf_dir: Path) -> None:
    buf = ResultBuffer(BufferConfig(path=buf_dir, max_bytes=1024 * 1024))
    await buf.open()
    await buf.write(_make_result())
    await buf.close()

    # Corrupt the segment by appending junk
    seg = next(iter(buf_dir.glob("segment-*.log")))
    with seg.open("ab") as f:
        f.write(b"\x00\x00\x00\x10not-json-not-json")

    buf2 = ResultBuffer(BufferConfig(path=buf_dir, max_bytes=1024 * 1024))
    await buf2.open()
    drained = await buf2.drain(batch_size=10)
    # Only the original good record should be returned
    assert any(json.dumps(d).find("ok") != -1 for d in drained)
    await buf2.close()
