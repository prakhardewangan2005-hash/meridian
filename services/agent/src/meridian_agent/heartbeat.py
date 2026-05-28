"""mTLS heartbeat + initial registration with the controller."""
from __future__ import annotations

import asyncio
import platform
import random
import socket
import ssl

import aiohttp
import structlog

from meridian_agent.config import ControllerConfig

log = structlog.get_logger(__name__)


def _build_ssl_context(cfg: ControllerConfig) -> ssl.SSLContext:
    ctx = ssl.create_default_context(cafile=str(cfg.ca_cert))
    ctx.load_cert_chain(certfile=str(cfg.client_cert), keyfile=str(cfg.client_key))
    ctx.verify_mode = ssl.CERT_REQUIRED
    ctx.check_hostname = True
    return ctx


class HeartbeatClient:
    def __init__(self, cfg: ControllerConfig, *, node_id: str) -> None:
        self._cfg = cfg
        self._node_id = node_id
        self._ssl = _build_ssl_context(cfg)

    async def run(self, shutdown: asyncio.Event) -> None:
        await self._register_with_backoff(shutdown)
        while not shutdown.is_set():
            try:
                await asyncio.wait_for(
                    shutdown.wait(), timeout=self._cfg.heartbeat_interval_s
                )
                return
            except asyncio.TimeoutError:
                pass
            await self._beat()

    async def _register_with_backoff(self, shutdown: asyncio.Event) -> None:
        delay = self._cfg.register_retry_initial_s
        while not shutdown.is_set():
            try:
                await self._register()
                return
            except Exception:
                jittered = delay * random.uniform(0.5, 1.5)
                log.warning("heartbeat.register_failed", retry_in_s=round(jittered, 1))
                try:
                    await asyncio.wait_for(shutdown.wait(), timeout=jittered)
                    return
                except asyncio.TimeoutError:
                    pass
                delay = min(delay * 2, self._cfg.register_retry_max_s)

    async def _register(self) -> None:
        payload = {
            "node_id": self._node_id,
            "hostname": socket.gethostname(),
            "kernel": platform.release(),
            "arch": platform.machine(),
            "python_version": platform.python_version(),
        }
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=self._ssl)
        ) as s:
            async with s.post(
                f"{self._cfg.url}/api/v1/nodes/register", json=payload
            ) as r:
                r.raise_for_status()
        log.info("heartbeat.registered", node_id=self._node_id)

    async def _beat(self) -> None:
        try:
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=self._ssl),
                timeout=aiohttp.ClientTimeout(total=10),
            ) as s:
                async with s.post(
                    f"{self._cfg.url}/api/v1/nodes/{self._node_id}/heartbeat",
                    json={"alive": True},
                ) as r:
                    r.raise_for_status()
            log.debug("heartbeat.ok", node_id=self._node_id)
        except Exception:
            log.warning("heartbeat.failed", node_id=self._node_id)
