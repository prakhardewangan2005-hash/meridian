"""Example third-party probe: checks TLS certificate days-to-expiry.

Install via an entry point under the 'meridian_agent.probes' group, then
reference `type: tls_expiry` in your probe YAML.
"""
from __future__ import annotations

import asyncio
import datetime as dt
import socket
import ssl

from meridian_agent.probes.base import Probe, ProbeResult


class TLSExpiryProbe(Probe):
    probe_type = "tls_expiry"

    def __init__(self, *, warn_days: int = 14, **kwargs: object) -> None:
        super().__init__(**kwargs)  # type: ignore[arg-type]
        self.warn_days = warn_days

    async def execute(self) -> ProbeResult:
        host, _, port_s = self.target.partition(":")
        port = int(port_s or 443)
        loop = asyncio.get_running_loop()
        try:
            days = await loop.run_in_executor(None, self._days_left, host, port)
        except Exception as e:  # noqa: BLE001
            return ProbeResult.errored(self, f"tls check failed: {e}")

        meta = {"days_to_expiry": days, "warn_days": self.warn_days}
        if days < 0:
            return ProbeResult.fail(self, 0.0, error="certificate expired", **meta)
        if days < self.warn_days:
            return ProbeResult.fail(
                self, 0.0, error=f"expires in {days}d", **meta
            )
        return ProbeResult.ok(self, latency_s=0.0, **meta)

    @staticmethod
    def _days_left(host: str, port: int) -> int:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=5) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
        not_after = cert["notAfter"]  # type: ignore[index]
        expiry = dt.datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
        expiry = expiry.replace(tzinfo=dt.UTC)
        return (expiry - dt.datetime.now(dt.UTC)).days
