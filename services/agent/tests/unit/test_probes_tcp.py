"""TCPProbe tests against a local ephemeral server."""
from __future__ import annotations

import asyncio

import pytest

from meridian_agent.probes.tcp import TCPProbe


@pytest.fixture
async def echo_server():
    async def handle(_r: asyncio.StreamReader, w: asyncio.StreamWriter) -> None:
        w.write(b"meridian-test-banner\r\n")
        await w.drain()
        w.close()

    server = await asyncio.start_server(handle, "127.0.0.1", 0)
    port = server.sockets[0].getsockname()[1]
    async with server:
        yield port


async def test_tcp_probe_ok(echo_server: int) -> None:
    probe = TCPProbe(name="t", target=f"127.0.0.1:{echo_server}", timeout_s=2.0)
    r = await probe.execute()
    assert r.success
    assert r.latency_s > 0
    assert r.metadata["port"] == echo_server


async def test_tcp_banner_match(echo_server: int) -> None:
    probe = TCPProbe(
        name="t",
        target=f"127.0.0.1:{echo_server}",
        expect_banner="meridian",
        timeout_s=2.0,
    )
    r = await probe.execute()
    assert r.success
    assert "meridian" in r.metadata["banner"]


async def test_tcp_banner_mismatch(echo_server: int) -> None:
    probe = TCPProbe(
        name="t",
        target=f"127.0.0.1:{echo_server}",
        expect_banner="not-present",
        timeout_s=2.0,
    )
    r = await probe.execute()
    assert not r.success
    assert "banner mismatch" in (r.error or "")


async def test_tcp_connection_refused() -> None:
    probe = TCPProbe(name="t", target="127.0.0.1:1", timeout_s=1.0)
    r = await probe.execute()
    assert not r.success
