"""Drop a percentage of packets via `tc qdisc netem loss`."""
from __future__ import annotations

from meridian_chaos.experiments.base import Experiment


class NetworkLossExperiment(Experiment):
    kind = "network_loss"

    def validate(self) -> None:
        loss = self.spec.params.get("loss_pct")
        if loss is None or not (0 < loss <= 100):
            raise ValueError("network_loss requires 0 < params.loss_pct <= 100")

    async def apply(self) -> None:
        iface = self.spec.params.get("interface", "eth0")
        rc, _, err = await self.run([
            "tc", "qdisc", "add", "dev", iface, "root", "netem",
            "loss", f"{self.spec.params['loss_pct']}%",
        ])
        if rc != 0:
            raise RuntimeError(f"tc netem loss failed: {err}")
        self._applied = True

    async def revert(self) -> None:
        if not self._applied:
            return
        iface = self.spec.params.get("interface", "eth0")
        await self.run(["tc", "qdisc", "del", "dev", iface, "root"])
