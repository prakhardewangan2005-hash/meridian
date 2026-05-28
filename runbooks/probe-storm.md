# Runbook: Probe Staleness / Storm

**Alert:** `ProbeStaleness` (probe hasn't run in > 5m) · **Severity:** ticket

## Impact
A probe stopped executing. We're blind to whatever it measured. If many probes
go stale at once, suspect the runner/agent, not individual probes.

## Check
1. One probe or many on the same host? Many → agent issue
   ([agent-down](agent-down.md)).
2. `meridian:probe_staleness_seconds` by probe.
3. Agent logs for that probe: timeouts? exceptions? (probes never crash the
   runner — they return `status=error`, which is still "fresh", so staleness
   means the *scheduler* isn't running it).
4. Is `probes.max_concurrent` saturated by slow probes starving others?

## Mitigate
* Saturation → raise `max_concurrent` or lower the offending probe's frequency /
  fix its target.
* Agent scheduler wedged → restart the agent.

## Verify
`meridian_probe_last_run_timestamp` advancing again; staleness < interval.

## Related
[agent-down](agent-down.md), [disk-full](disk-full.md)
