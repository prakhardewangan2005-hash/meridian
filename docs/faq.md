# FAQ

**Is this a Prometheus replacement?**
No. Meridian runs *on top of* Prometheus/Alertmanager/Loki/Grafana and adds the
per-host probe agent, controller, SLO catalog, incident tracking, and chaos
harness that those tools intentionally leave out.

**Why Python for the control plane?**
The control plane is I/O-bound and benefits from rapid iteration and a rich
async ecosystem. See [ADR-0004](adr/0004-python-for-control-plane.md). A
performance-critical data plane could later be rewritten in Go without changing
the architecture.

**Why pull-based metrics?**
Prometheus pull gives free liveness (a scrape failure *is* a signal) and avoids
agent-side push buffering for the metrics path. See
[ADR-0003](adr/0003-prometheus-pull-default.md). Logs use push (Loki) because
that's the natural model for them.

**Does the agent need root?**
No. It runs as a non-root system user with exactly one capability, `CAP_NET_RAW`,
needed for raw-socket ICMP and traceroute. Everything else is unprivileged.

**What happens if the controller dies?**
Agents keep probing and buffering; only management (config changes, SLO eval,
incident tracking) is affected. See [architecture.md](architecture.md).

**How are SLOs defined?**
As version-controlled YAML in
[config/slo/slo-catalog.yaml](../config/slo/slo-catalog.yaml). CI renders docs
and generates burn-rate alert rules from it.
