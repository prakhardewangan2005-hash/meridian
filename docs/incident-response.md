# Incident Response

## Severity levels

| Sev | Definition | Response |
|---|---|---|
| SEV1 | Total outage / data loss | all-hands, page immediately, exec comms |
| SEV2 | Major degradation, SLO at risk | page on-call, incident channel |
| SEV3 | Minor degradation, budget impact | ticket, business-hours |
| SEV4 | Cosmetic / no user impact | backlog |

## Flow

1. **Detect** — alert fires (burn-rate or operational), linked runbook opens.
2. **Triage** — on-call assigns severity, opens an incident:
   `meridianctl incident open --code INC-NNN --title "..." --severity SEV2`
3. **Mitigate** — follow the runbook; stop the bleeding before root-causing.
4. **Resolve** — confirm SLI recovered; `meridianctl incident close <id>`.
5. **Learn** — write a blameless postmortem in
   [incident-reports/](../incident-reports/) using
   [the template](../incident-reports/template.md).

## Blameless postmortems

We have real examples:
[INC-001 cascading DNS failure](../incident-reports/INC-001-cascading-dns-failure.md),
[INC-002 cgroup memory leak](../incident-reports/INC-002-cgroup-memory-leak.md),
[INC-003 TCP retransmit / MTU mismatch](../incident-reports/INC-003-tcp-retransmit-mtu-mismatch.md),
[INC-004 Prometheus cardinality explosion](../incident-reports/INC-004-prometheus-cardinality-explosion.md).

Each has a timeline, root-cause analysis (5 whys), what went well/poorly, and
tracked action items. The focus is on systems and process, never individuals.
