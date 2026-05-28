# Runbook: Alert Storm

**Severity:** operational (no single alert)

## Impact
Many alerts firing at once. Risk: the real root cause is buried and on-call is
overwhelmed. Inhibition rules reduce this but can't eliminate it.

## Check
1. Group by time — what fired *first*? The earliest alert is usually closest to
   the root cause.
2. Common dependencies: DNS and the controller are upstream of many things —
   check [dns-resolution-failure](dns-resolution-failure.md) and
   [controller-degraded](controller-degraded.md) first.
3. Confirm inhibition is working (AgentDown should suppress that node's
   ProbeStaleness).

## Mitigate
* Identify and fix the root cause; downstream alerts clear on their own.
* If alerts are genuinely noisy, add/adjust inhibition rules in
  `config/alertmanager/alertmanager.yml` — but only after the incident.
* Silence known-downstream alerts temporarily to focus (document the silence).

## Verify
Alert count collapses to the root cause; downstream alerts resolve.

## Related
[INC-001](../incident-reports/INC-001-cascading-dns-failure.md) (a DNS failure
that cascaded into a storm)
