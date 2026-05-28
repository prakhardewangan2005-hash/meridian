# Troubleshooting

Symptom-first index. For paging alerts, go straight to the linked runbook.

| Symptom | Likely cause | Where to look |
|---|---|---|
| Agent not in `nodes list` | registration failing (cert/url) | [runbooks/agent-down.md](../runbooks/agent-down.md) |
| Probe `status=error` "requires CAP_NET_RAW" | missing capability | grant `CAP_NET_RAW` (systemd/k8s) |
| All DNS probes failing | resolver outage | [runbooks/dns-resolution-failure.md](../runbooks/dns-resolution-failure.md) |
| Rising TCP retransmits | MTU / loss / congestion | [runbooks/tcp-retransmit-storm.md](../runbooks/tcp-retransmit-storm.md) |
| Prometheus RSS climbing | cardinality explosion | [runbooks/prometheus-oom.md](../runbooks/prometheus-oom.md) |
| Agent buffer not draining | collector/exporter issue | check `:9101/metrics`, disk space |
| Controller `/readyz` 503 | Postgres unreachable | [runbooks/postgres-failover.md](../runbooks/postgres-failover.md) |
| Alert storm | correlated failure | [runbooks/alert-storm.md](../runbooks/alert-storm.md) |
| Error budget burning fast | real regression | [runbooks/high-error-budget-burn.md](../runbooks/high-error-budget-burn.md) |

## General debugging flow

1. Is the agent being scraped? `curl localhost:9101/metrics`
2. Is it registered? `meridianctl nodes list`
3. What do its logs say? (structured JSON; filter by `event`)
4. Is the probe itself failing or the path? `meridianctl probes run-once --type <t> --target <x>`
5. Use the debug scripts: `scripts/network-diag.sh`, `tcp-debug.sh`, `dns-debug.sh`.
