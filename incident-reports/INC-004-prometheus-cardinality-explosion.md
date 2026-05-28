# INC-004: Prometheus Cardinality Explosion

* **Severity:** SEV2
* **Status:** Resolved
* **Date:** 2025-11-08
* **Authors:** on-call, observability-team
* **Duration:** 53 minutes (11:20 → 12:13 UTC)

## Summary
A well-intentioned change added a per-probe `resolved_ip` label to a metric. For
DNS probes resolving round-robin records, that produced thousands of new series
per probe. Prometheus head series ballooned, memory spiked, and it OOM-restarted
— briefly taking down the metrics/alerting path. Dropping the label via relabel
config restored it.

## Impact
* Prometheus OOM-restarted twice; ~9 minutes of gaps in metrics/alerting.
* During the gaps, burn-rate alerts couldn't evaluate — a monitoring blind spot.
* No probe data lost (agents buffered through it).

## Timeline (UTC)
| Time | Event |
|---|---|
| 11:05 | Change merged adding `resolved_ip` label to probe latency metric |
| 11:20 | `PrometheusHighMemory` fires; head series climbing steeply |
| 11:24 | On-call confirms via `topk(10, count by (__name__)(...))` |
| 11:31 | First Prometheus OOM restart; ~4 min alerting gap |
| 11:36 | Offending label identified (`resolved_ip`, unbounded for RR DNS) |
| 11:48 | `metric_relabel_configs` drop rule deployed for the label |
| 11:55 | Second restart to apply config; head series begins dropping |
| 12:08 | Series count back to baseline; memory stable |
| 12:13 | Resolved; the metric change reverted at source as well |

## Root cause (5 whys)
1. Why did Prometheus OOM? Active series count exploded.
2. Why? A new label (`resolved_ip`) had unbounded values for round-robin DNS.
3. Why did it ship? The uniform-schema discipline (ADR-0007) wasn't enforced in
   review; high-cardinality fields belong in metadata/logs, not labels.
4. Why no guard? No CI check on metric cardinality / label allow-list.
5. Why did it hurt alerting? Prometheus is a single point for the metrics path;
   when it OOMs, burn-rate evaluation stops. ← root causes

## Detection
`PrometheusHighMemory` did fire, but by then series were already climbing fast.
We were monitoring the symptom (RSS) more than the leading cause (series growth
rate).

## What went well
* The runbook's `topk` query pinpointed the label in minutes.
* Relabel-drop is a fast, low-risk mitigation.

## What went poorly
* A cardinality landmine passed review (violated ADR-0007 in spirit).
* No automated cardinality guardrail.
* Prometheus as a single point briefly blinded alerting.

## Action items
| Action | Owner | Tracking | Status |
|---|---|---|---|
| Add CI check: metric label allow-list per metric | @observability | #171 | done |
| Alert on series *growth rate*, not just RSS | @sre | #172 | done |
| Reinforce ADR-0007 in the PR template checklist | @platform | #173 | done |
| Evaluate HA Prometheus / remote-write for alerting resilience | @observability | #174 | planned |
