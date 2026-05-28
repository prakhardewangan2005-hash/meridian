"""Agent scheduler + lifecycle.

Single event loop, one task per probe, bounded concurrency via Semaphore.
Probes that raise are converted to ProbeResult(status="error") — never crash the runner.
"""
from __future__ import annotations

import asyncio
import random
import signal
from contextlib import suppress
from typing import Iterable

import structlog

from meridian_agent.buffer import ResultBuffer
from meridian_agent.config import AgentSettings
from meridian_agent.exporter import MetricsExporter
from meridian_agent.heartbeat import HeartbeatClient
from meridian_agent.log_shipper import LogShipper
from meridian_agent.probes.base import Probe, ProbeResult
from meridian_agent.system import collect_system_metrics

log = structlog.get_logger(__name__)


class AgentRunner:
    def __init__(self, settings: AgentSettings, probes: Iterable[Probe]) -> None:
        self._settings = settings
        self._probes = list(probes)
        self._buffer = ResultBuffer(settings.buffer)
        self._exporter = MetricsExporter(settings.exporter)
        self._heartbeat = HeartbeatClient(settings.controller, node_id=settings.node_id)
        self._log_shipper = LogShipper(settings.logs) if settings.logs.enabled else None
        self._probe_sem = asyncio.Semaphore(settings.probes.max_concurrent)
        self._shutdown = asyncio.Event()

    async def run(self) -> None:
        log.info(
            "agent.starting",
            node_id=self._settings.node_id,
            probes=len(self._probes),
        )

        await self._buffer.open()
        await self._exporter.start()
        if self._log_shipper is not None:
            await self._log_shipper.start()

        loop = asyncio.get_running_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, self._on_signal, sig)

        tasks: list[asyncio.Task] = [
            asyncio.create_task(
                self._heartbeat.run(self._shutdown), name="heartbeat"
            ),
        ]
        if self._settings.system_metrics.enabled:
            tasks.append(
                asyncio.create_task(self._run_system(), name="system-metrics")
            )
        for p in self._probes:
            tasks.append(
                asyncio.create_task(self._run_probe(p), name=f"probe:{p.name}")
            )

        await self._shutdown.wait()
        log.info("agent.stopping", tasks=len(tasks))

        for t in tasks:
            t.cancel()
        for t in tasks:
            with suppress(asyncio.CancelledError):
                await t

        if self._log_shipper is not None:
            await self._log_shipper.stop()
        await self._exporter.stop()
        await self._buffer.close()
        log.info("agent.stopped")

    def _on_signal(self, sig: signal.Signals) -> None:
        log.info("agent.signal_received", signal=sig.name)
        self._shutdown.set()

    async def _run_probe(self, probe: Probe) -> None:
        # cold-start jitter so probes don't synchronize on agent startup
        await asyncio.sleep(random.uniform(0.0, probe.interval_s))
        loop = asyncio.get_running_loop()
        while not self._shutdown.is_set():
            jitter = random.uniform(-probe.jitter_s, probe.jitter_s)
            next_at = loop.time() + probe.interval_s + jitter
            await self._execute_one(probe)
            sleep_for = max(0.0, next_at - loop.time())
            try:
                await asyncio.wait_for(self._shutdown.wait(), timeout=sleep_for)
                return
            except asyncio.TimeoutError:
                continue

    async def _execute_one(self, probe: Probe) -> None:
        async with self._probe_sem:
            try:
                result = await asyncio.wait_for(
                    probe.execute(), timeout=probe.timeout_s
                )
            except asyncio.TimeoutError:
                result = ProbeResult.timeout(probe)
                log.warning("probe.timeout", probe=probe.name, target=probe.target)
            except Exception as exc:  # noqa: BLE001
                result = ProbeResult.errored(probe, error=str(exc))
                log.exception("probe.crashed", probe=probe.name)
        await self._buffer.write(result)
        self._exporter.record_probe(result)

    async def _run_system(self) -> None:
        interval = self._settings.system_metrics.interval_s
        include_cg = self._settings.system_metrics.include_cgroups
        while not self._shutdown.is_set():
            try:
                snapshot = await collect_system_metrics(include_cgroups=include_cg)
                self._exporter.record_system(snapshot)
            except Exception:
                log.exception("system.collect_failed")
            try:
                await asyncio.wait_for(self._shutdown.wait(), timeout=interval)
                return
            except asyncio.TimeoutError:
                continue
