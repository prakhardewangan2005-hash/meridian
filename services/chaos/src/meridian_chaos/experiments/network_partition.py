"""Block traffic to a peer via iptables."""
from __future__ import annotations

from meridian_chaos.experiments.base import Experiment


class NetworkPartitionExperiment(Experiment):
    kind = "network_partition"

    def validate(self) -> None:
        if "peer_ip" not in self.spec.params:
            raise ValueError("network_partition requires params.peer_ip")

    async def apply(self) -> None:
        rc, _, err = await self.run([
            "iptables", "-A", "OUTPUT",
            "-d", self.spec.params["peer_ip"], "-j", "DROP",
        ])
        if rc != 0:
            raise RuntimeError(f"iptables add failed: {err}")
        self._applied = True

    async def revert(self) -> None:
        if not self._applied:
            return
        await self.run([
            "iptables", "-D", "OUTPUT",
            "-d", self.spec.params["peer_ip"], "-j", "DROP",
        ])
