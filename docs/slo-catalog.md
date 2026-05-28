# SLO Catalog (rendered)

> This file is generated from
> [config/slo/slo-catalog.yaml](../config/slo/slo-catalog.yaml) by CI
> (`tools/docs-build.sh`). Edit the YAML, not this page.

Burn-rate alerting follows the Google SRE multi-window method; see
[monitoring.md](monitoring.md).

| SLO | Service | Objective | Window | SLI |
|---|---|---|---|---|
| probe_success_ratio | probe-fleet | 99.0% | 30d | success ratio of all probe executions |
| dns_probe_success_ratio | dns | 99.5% | 30d | success ratio of DNS probes |
| http_probe_latency_slo | http-endpoints | 99.0% | 30d | fraction of HTTP probes < 1s |
| controller_api_availability | controller | 99.9% | 30d | non-5xx ratio of controller API |
| agent_heartbeat_freshness | agent-fleet | 99.0% | 7d | fraction of nodes heartbeating in time |
| icmp_loss_slo | network | 99.5% | 30d | fraction of ICMP probes with zero loss |

## Error budgets

| Objective | Monthly budget (30d) |
|---|---|
| 99.0% | 7h 18m of failure |
| 99.5% | 3h 39m |
| 99.9% | 43m 12s |

When budget is exhausted, the policy is: **freeze risky changes, prioritize
reliability work** until the budget recovers.
