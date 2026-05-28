# Runbook: High Error-Budget Burn

**Alert:** `SLOFastBurnProbeSuccess` / `SLOSlowBurnProbeSuccess` · **Severity:** page

## Impact
An SLO is consuming its error budget faster than sustainable. Fast burn = 2% of
the 30d budget in 1h. This is a real, ongoing regression, not a blip (the
multi-window method already filtered out blips).

## Check
1. Which SLO? The alert's `slo` label.
2. `meridianctl slo status <id>` — current SLI, burn rates, budget remaining.
3. Drill into the SLI's components — for `probe_success_ratio`, break down by
   `type` to find which probe class is failing
   (`meridian:probe_success_ratio_by_type:5m`).
4. Correlate with operational alerts (AgentDown, DNS, retransmits) — the burn is
   usually a *symptom* of one of those.

## Mitigate
Treat the underlying failure (follow the relevant runbook). The burn alert is
the "this matters to users" signal; the operational alert tells you what to fix.

## Verify
Burn rate drops below 1; budget stops decreasing.

## Policy
If budget is exhausted: freeze risky changes, prioritize reliability work until
it recovers (see [slo-catalog.md](../docs/slo-catalog.md)).

## Related
[monitoring.md](../docs/monitoring.md), every operational runbook
