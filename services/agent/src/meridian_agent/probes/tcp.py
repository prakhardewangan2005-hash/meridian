"""TCP connect probe with optional banner verification."""
from __future__ import annotations

import asyncio
import socket
import time

from meridian_agent.probes.base import Probe, ProbeResult


def _parse_target(target: str, default_port: int | None) -> tuple[str, int]:
    if ":" in target:
        host, port_s = target.rsplit(":", 1)
        return host, int(port_s)
    if default_port is None:
        raise ValueError(f"{target!r}: no port and no default")
    return target, default_port


class TCPProbe(Probe):
    probe_type = "tcp"

    def __init__(
        self,
        *,
        port: int | None = None,
        expect_banner: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(**kwargs)  # type: ignore[arg-type]
        self.host, self.port = _parse_target(self.target, default_port=port)
        self.expect_banner = expect_banner

    async def execute(self) -> ProbeResult:
        start = time.perf_counter()
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=self.timeout_s,
            )
        except asyncio.TimeoutError:
            return ProbeResult.timeout(self)
        except (ConnectionRefusedError, OSError) as e:
            return ProbeResult.fail(self, time.perf_counter() - start, error=str(e))

        connect_latency = time.perf_counter() - start
        banner: str | None = None
        try:
            sock = writer.get_extra_info("socket")
            if sock is not None:
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            if self.expect_banner:
                try:
                    data = await asyncio.wait_for(reader.read(256), timeout=self.timeout_s)
                except asyncio.TimeoutError:
                    return ProbeResult.fail(
                        self,
                        time.perf_counter() - start,
                        error="banner read timeout",
                        connect_latency_s=connect_latency,
                    )
                banner = data.decode("utf-8", errors="replace").strip()
                if self.expect_banner not in banner:
                    return ProbeResult.fail(
                        self,
                        time.perf_counter() - start,
                        error=f"banner mismatch: got {banner!r}",
                        connect_latency_s=connect_latency,
                        banner=banner,
                    )
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:  # noqa: BLE001
                pass

        return ProbeResult.ok(
            self,
            connect_latency,
            host=self.host,
            port=self.port,
            connect_latency_s=connect_latency,
            banner=banner,
        )
