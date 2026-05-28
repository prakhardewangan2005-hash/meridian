"""Prometheus exporter.

Single registry, three core metric families:
  * meridian_probe_{success,latency_seconds,last_run_timestamp,executions_total}
  * meridian_system{metric=...}
  * meridian_network{interface=..., metric=...}
"""
from __future__ import annotations

from typing import Any

import structlog
from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    start_http_server,
)

from meridian_agent.config import ExporterConfig
from meridian_agent.probes.base import ProbeResult

log = structlog.get_logger(__name__)

PROBE_LABELS = ("probe", "target", "type")
LATENCY_BUCKETS = (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10, 30)


class MetricsExporter:
    def __init__(self, cfg: ExporterConfig) -> None:
        self._cfg = cfg
        self._registry = CollectorRegistry()
        self._server: Any = None

        self.probe_success = Gauge(
            "meridian_probe_success",
            "1 if last execution succeeded, else 0",
            PROBE_LABELS,
            registry=self._registry,
        )
        self.probe_latency = Histogram(
            "meridian_probe_latency_seconds",
            "Probe execution latency",
            PROBE_LABELS,
            buckets=LATENCY_BUCKETS,
            registry=self._registry,
        )
        self.probe_last_run = Gauge(
            "meridian_probe_last_run_timestamp",
            "Unix timestamp of last execution",
            PROBE_LABELS,
            registry=self._registry,
        )
        self.probe_total = Counter(
            "meridian_probe_executions_total",
            "Total probe executions",
            (*PROBE_LABELS, "status"),
            registry=self._registry,
        )
        self.system = Gauge(
            "meridian_system",
            "Linux system metric",
            ("metric",),
            registry=self._registry,
        )
        self.network = Gauge(
            "meridian_network",
            "Per-interface counter",
            ("interface", "metric"),
            registry=self._registry,
        )

    async def start(self) -> None:
        # prometheus_client.start_http_server is synchronous; safe at startup.
        self._server, _ = start_http_server(
            port=self._cfg.bind_port,
            addr=self._cfg.bind_host,
            registry=self._registry,
        )
        log.info("exporter.started", host=self._cfg.bind_host, port=self._cfg.bind_port)

    async def stop(self) -> None:
        if self._server is not None:
            self._server.shutdown()
            log.info("exporter.stopped")

    def record_probe(self, r: ProbeResult) -> None:
        labels = (r.probe_name, r.target, r.probe_type)
        self.probe_success.labels(*labels).set(1 if r.success else 0)
        self.probe_latency.labels(*labels).observe(r.latency_s)
        self.probe_last_run.labels(*labels).set(r.timestamp)
        self.probe_total.labels(*labels, r.status).inc()

    def record_system(self, snapshot: dict[str, Any]) -> None:
        for k, v in snapshot.get("scalar", {}).items():
            try:
                self.system.labels(k).set(float(v))
            except (TypeError, ValueError):
                continue
        for iface, metrics in snapshot.get("network", {}).items():
            for k, v in metrics.items():
                try:
                    self.network.labels(iface, k).set(float(v))
                except (TypeError, ValueError):
                    continue
