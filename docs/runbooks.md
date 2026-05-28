# Runbooks Index

Operational runbooks live in [`runbooks/`](../runbooks/) and are linked directly
from alert annotations. This page is the human index; see
[runbooks/README.md](../runbooks/README.md) for the severity matrix.

| Runbook | For alert |
|---|---|
| [agent-down](../runbooks/agent-down.md) | `AgentDown` |
| [controller-degraded](../runbooks/controller-degraded.md) | `ControllerAPIFastBurn` |
| [dns-resolution-failure](../runbooks/dns-resolution-failure.md) | `DNSResolutionFailing` |
| [tcp-retransmit-storm](../runbooks/tcp-retransmit-storm.md) | `HighTCPRetransmitRate` |
| [disk-full](../runbooks/disk-full.md) | `NodeDiskFillingUp` |
| [prometheus-oom](../runbooks/prometheus-oom.md) | `PrometheusHighMemory` |
| [high-error-budget-burn](../runbooks/high-error-budget-burn.md) | `SLO*Burn*` |
| [probe-storm](../runbooks/probe-storm.md) | `ProbeStaleness` |
| [alert-storm](../runbooks/alert-storm.md) | (operational) |
| [cert-rotation](../runbooks/cert-rotation.md) | (scheduled) |
| [deploy-rollback](../runbooks/deploy-rollback.md) | (operational) |
| [postgres-failover](../runbooks/postgres-failover.md) | (operational) |
| [network-partition](../runbooks/network-partition.md) | (operational) |
| [on-call-onboarding](../runbooks/on-call-onboarding.md) | (reference) |
