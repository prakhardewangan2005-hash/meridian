# Runbook: Postgres Failover

**Severity:** operational (often underlies controller-degraded)

## Impact
Controller depends on Postgres for inventory, SLO snapshots, incidents. DB down →
controller `/readyz` 503 and out of rotation. **Agents are unaffected** and keep
probing/buffering.

## Check
1. `kubectl -n meridian get pods -l app.kubernetes.io/component=postgres`
2. `pg_isready -h <host> -U meridian`
3. Disk/CPU on the DB; connection count vs `max_connections`.
4. Replication lag if using a replica.

## Mitigate
* Primary down with a replica → promote the replica; repoint the controller DSN
  (Secret `meridian-db`).
* Connection exhaustion → kill idle connections; restart controller to reset its
  pool; lower `db_pool_size`/`db_max_overflow` if over-provisioned.
* Storage full → extend the PVC.

## Verify
`pg_isready` OK; controller `/readyz` 200; SLO evaluator resumes writing
snapshots.

## Escalate
Data corruption / failed promotion → DBA / managed-DB support.

## Related
[controller-degraded](controller-degraded.md)
