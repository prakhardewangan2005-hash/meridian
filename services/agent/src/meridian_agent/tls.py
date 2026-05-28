"""TLS cert lifecycle helpers.

Provides a small utility to watch for cert file modification and rebuild the
SSLContext when the on-disk certificate is rotated by an external sidecar
(e.g. cert-manager, step-ca). This is intentionally not a full rotation system —
the system PKI integration tools own the actual cert lifecycle.
"""
from __future__ import annotations

import asyncio
import ssl
from pathlib import Path

import structlog

log = structlog.get_logger(__name__)


def build_mtls_context(
    *,
    ca_cert: Path,
    client_cert: Path,
    client_key: Path,
) -> ssl.SSLContext:
    ctx = ssl.create_default_context(cafile=str(ca_cert))
    ctx.load_cert_chain(certfile=str(client_cert), keyfile=str(client_key))
    ctx.verify_mode = ssl.CERT_REQUIRED
    ctx.check_hostname = True
    return ctx


class CertWatcher:
    """Watches client cert mtime and signals when rotation occurred."""

    def __init__(self, client_cert: Path, *, poll_interval_s: float = 30.0) -> None:
        self._path = client_cert
        self._interval = poll_interval_s
        self._last_mtime: float | None = None
        self._rotated = asyncio.Event()

    @property
    def rotated(self) -> asyncio.Event:
        return self._rotated

    async def run(self, shutdown: asyncio.Event) -> None:
        try:
            self._last_mtime = self._path.stat().st_mtime
        except OSError:
            pass
        while not shutdown.is_set():
            try:
                await asyncio.wait_for(shutdown.wait(), timeout=self._interval)
                return
            except asyncio.TimeoutError:
                pass
            try:
                m = self._path.stat().st_mtime
            except OSError:
                continue
            if self._last_mtime is not None and m != self._last_mtime:
                log.info("tls.cert_rotated", path=str(self._path))
                self._rotated.set()
                # one-shot — caller observes and rebuilds context
                return
            self._last_mtime = m
