# Runbooks

Operational playbooks. Each alert in
[config/prometheus/alerts.yml](../config/prometheus/alerts.yml) links here via a
`runbook_url` annotation; CI (`tools/ci-local.sh`) fails if any alert lacks one.

## Severity matrix

| Severity | Meaning | Response time | Channel |
|---|---|---|---|
| page | user-impacting or SLO at imminent risk | minutes | pager |
| ticket | degraded, budget impact, not urgent | next business day | queue |

## Runbook structure

Every runbook follows the same shape: **Alert** → **Impact** → **Check** →
**Mitigate** → **Verify** → **Escalate** → **Related**. Mitigation comes before
root-cause: stop the bleeding first.

## Index

* [on-call-onboarding](on-call-onboarding.md)
* [alert-storm](alert-storm.md)
* [agent-down](agent-down.md)
* [controller-degraded](controller-degraded.md)
* [cert-rotation](cert-rotation.md)
* [disk-full](disk-full.md)
* [prometheus-oom](prometheus-oom.md)
* [dns-resolution-failure](dns-resolution-failure.md)
* [network-partition](network-partition.md)
* [high-error-budget-burn](high-error-budget-burn.md)
* [probe-storm](probe-storm.md)
* [deploy-rollback](deploy-rollback.md)
* [postgres-failover](postgres-failover.md)
* [tcp-retransmit-storm](tcp-retransmit-storm.md)
