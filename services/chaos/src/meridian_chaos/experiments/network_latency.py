"""Add latency on an interface using `tc qdisc netem`."""
from __future__ import annotations

import structlog

from meridian_chaos.experiments.base import Experiment

log = structlog.get_logger(__name__)


class NetworkLatencyExperiment(Experiment):
    kind = "network_latency"

    def validate(self) -> None:
        if "delay_ms" not in self.spec.params:
            raise ValueError("network_latency requires params.delay_ms")
        if self.spec.params["delay_ms"] < 0:
            raise ValueError("delay_ms must be >= 0")

    async def apply(self) -> None:
        iface = self.spec.params.get("interface", "eth0")
        delay = self.spec.params["delay_ms"]
        jitter = self.spec.params.get("jitter_ms", 0)
        cmd = ["tc", "qdisc", "add", "dev", iface, "root", "netem",
               "delay", f"{delay}ms"]
        if jitter:
            cmd.append(f"{jitter}ms")
        rc, _, err = await self.run(cmd)
        if rc != 0:
            log.error("netem.add_failed", rc=rc, err=err)
            raise RuntimeError(f"tc netem add failed: {err}")
        self._applied = True

    async def revert(self) -> None:
        if not self._applied:
            return
        iface = self.spec.params.get("interface", "eth0")
        await self.run(["tc", "qdisc", "del", "dev", iface, "root"])
