# meridian-chaos

Chaos engineering execution layer.

The chaos service receives experiment requests from the controller, executes them
on the local host using kernel-level tooling (`tc netem`, `iptables`, cgroup v2,
`stress-ng`), and **auto-reverts** them after the requested duration even if the
process crashes.

## Experiments

| Kind | Tool | Effect |
|---|---|---|
| `network_latency` | `tc qdisc netem delay` | Add latency on an interface |
| `network_loss`    | `tc qdisc netem loss`  | Drop a percentage of packets |
| `network_partition` | `iptables -A OUTPUT -d X -j DROP` | Block traffic to a peer |
| `cpu_pressure`    | `stress-ng --cpu N`    | Saturate CPU cores |
| `memory_pressure` | cgroup `memory.high`   | Squeeze available memory |
| `disk_fill`       | `fallocate`            | Consume disk space |

## Safety

* All experiments default to **dry-run**.
* Every experiment has a **mandatory duration** and is auto-reverted by a watchdog.
* The service tracks active experiments in memory; on shutdown it attempts to
  revert all in-flight experiments before exiting.
* Requires `CAP_NET_ADMIN` and/or `CAP_SYS_ADMIN`. The systemd unit and the
  k8s securityContext grant only the capabilities each experiment requires.
