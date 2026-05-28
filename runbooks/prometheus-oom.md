# Runbook: Prometheus High Memory / OOM

**Alert:** `PrometheusHighMemory` (RSS > 3GB) · **Severity:** ticket

## Impact
Prometheus memory is dominated by active series (cardinality). Unchecked, it OOMs
and you lose the metrics path — and thus alerting.

## Check
1. `prometheus_tsdb_head_series` — total active series, trending up?
2. Top metrics by cardinality:
   `topk(10, count by (__name__)({__name__=~".+"}))`
3. Which label is exploding? Often an unbounded label (user id, full URL, raw IP)
   sneaking into a metric.

## Mitigate
* Drop/relabel the offending label in the scrape config (`metric_relabel_configs`).
* If a probe/target is generating unbounded `target` values, fix the probe def.
* Short term: raise memory limit / restart to recover; reduce retention.

## Verify
`prometheus_tsdb_head_series` flattens; RSS drops and holds.

## Escalate
Structural cardinality growth → revisit metric design; consider sharding/remote
write (see [scaling.md](../docs/scaling.md)).

## Related
[INC-004 cardinality explosion](../incident-reports/INC-004-prometheus-cardinality-explosion.md),
[ADR-0007](../docs/adr/0007-uniform-probe-schema.md)
