# Monitoring

How alerting is wired, end to end.

## Multi-window burn-rate alerting

Meridian follows the Google SRE workbook multi-window, multi-burn-rate method.
Instead of "alert when error rate > X", we alert on **how fast the error budget
is burning**, across two windows simultaneously to balance sensitivity and
precision:

| Severity | Long window | Short window | Budget consumed | Action |
|---|---|---|---|---|
| Page | 1h burn > 14.4 | 5m burn > 14.4 | 2% in 1h | wake someone |
| Page | 6h burn > 6 | 1h burn > 6 | 5% in 6h | wake someone |
| Ticket | 1d burn > 3 | 2h burn > 3 | 10% in 1d | next business day |
| Ticket | 3d burn > 1 | 6h burn > 1 | 10% in 3d | next business day |

The short window prevents alerting on an already-resolved blip; the long window
prevents flapping. Both must exceed the threshold to fire.

Burn rate = `(1 - SLI) / (1 - objective)`. A burn rate of 1 means you'll exactly
exhaust the budget over the SLO window; 14.4 means you'll exhaust it 14.4× faster.

## Every alert links a runbook

Each alert in [config/prometheus/alerts.yml](../config/prometheus/alerts.yml)
carries a `runbook_url` annotation. `tools/ci-local.sh` fails the build if any
alert is missing one. The on-call's first click is always the runbook.

## Routing and inhibition

[config/alertmanager/alertmanager.yml](../config/alertmanager/alertmanager.yml):

* `severity=page` → pager receiver, 10s group wait, 1h repeat
* `severity=ticket` → tickets receiver, default cadence
* Inhibition: `AgentDown` suppresses that node's `ProbeStaleness` (one root
  cause, one page).

## Dashboards

Six provisioned Grafana dashboards: overview, SLO burn, probe health, network
telemetry, Linux fleet, incident response. See
[config/grafana/dashboards/](../config/grafana/dashboards/).
