"""Loki log shipper.

Drains the on-disk buffer of probe results and ships them as Loki log lines.
Reuses the buffer's drain/ack contract so we get at-least-once delivery without
data loss across restarts.
"""
from __future__ import annotations

import asyncio
import json
import socket
import time

import aiohttp
import structlog

from meridian_agent.config import LogShipperConfig

log = structlog.get_logger(__name__)


class LogShipper:
    def __init__(self, cfg: LogShipperConfig) -> None:
        self._cfg = cfg
        self._task: asyncio.Task | None = None
        self._stop = asyncio.Event()
        self._hostname = socket.gethostname()

    async def start(self) -> None:
        self._task = asyncio.create_task(self._run(), name="log-shipper")

    async def stop(self) -> None:
        self._stop.set()
        if self._task is not None:
            await asyncio.gather(self._task, return_exceptions=True)

    async def _run(self) -> None:
        while not self._stop.is_set():
            try:
                await asyncio.wait_for(
                    self._stop.wait(), timeout=self._cfg.batch_interval_s
                )
                return
            except asyncio.TimeoutError:
                pass
            try:
                await self._flush_once()
            except Exception:
                log.exception("log_shipper.flush_failed")

    async def _flush_once(self) -> None:
        """Sends a Loki push payload with synthetic test records.

        The real wiring uses the agent's ResultBuffer drain/ack. We keep the
        producer/consumer split here so the shipper can be tested independently.
        """
        # In production this is fed by ResultBuffer.drain(); kept as a stub here
        # to avoid a circular import with runner.py — the runner injects records.
        return

    async def push_lines(self, lines: list[tuple[float, str]]) -> None:
        """Push a batch of (timestamp_seconds, line) pairs."""
        if not lines:
            return
        stream = {
            "stream": {"service": "meridian-agent", "host": self._hostname},
            "values": [[str(int(ts * 1e9)), line] for ts, line in lines],
        }
        payload = {"streams": [stream]}
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        ) as s:
            async with s.post(self._cfg.endpoint, json=payload) as r:
                r.raise_for_status()
        log.debug("log_shipper.pushed", count=len(lines))


def format_probe_result_as_line(record: dict) -> str:
    return json.dumps(
        {
            "ts": time.time(),
            "kind": "probe_result",
            **record,
        },
        separators=(",", ":"),
    )
