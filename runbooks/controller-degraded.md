# Runbook: Controller Degraded

**Alert:** `ControllerAPIFastBurn` · **Severity:** page

## Impact
Control-plane API returning 5xx. Registration, probe distribution, SLO
evaluation, incident ops are affected. **Measurement continues** — agents keep
probing and buffering (see [architecture](../docs/architecture.md)).

## Check
1. `kubectl -n meridian get pods -l app.kubernetes.io/component=controller`
2. Controller `/readyz` — 503 means Postgres unreachable.
3. Controller logs for stack traces / DB errors.
4. Postgres health (see [postgres-failover](postgres-failover.md)).

## Mitigate
* Unhealthy replica → it should be out of rotation via readiness; delete the pod
  to force reschedule.
* DB connection exhaustion → check `db_pool_size`; restart controller to reset
  the pool; investigate slow queries.
* Bad recent deploy → [deploy-rollback](deploy-rollback.md).

## Verify
5xx rate returns to baseline; `controller_api_availability` burn rate < 1;
`/readyz` 200.

## Escalate
If Postgres is the root cause and failover is needed, escalate to the DB owner.

## Related
[postgres-failover](postgres-failover.md), [deploy-rollback](deploy-rollback.md)
