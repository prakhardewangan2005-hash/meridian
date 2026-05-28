# Incident Reports

Blameless postmortems. The goal is to learn how the *system* and *process*
allowed an incident, never to assign individual fault. Every SEV1/SEV2 gets a
postmortem; SEV3 at the team's discretion.

## Index

| ID | Title | Severity | Theme |
|---|---|---|---|
| [INC-001](INC-001-cascading-dns-failure.md) | Cascading DNS failure | SEV2 | dependency blast radius, alert storm |
| [INC-002](INC-002-cgroup-memory-leak.md) | Agent cgroup memory leak | SEV3 | PSI vs raw memory, slow burn |
| [INC-003](INC-003-tcp-retransmit-mtu-mismatch.md) | TCP retransmit / MTU mismatch | SEV2 | tunnel MTU, PMTUD |
| [INC-004](INC-004-prometheus-cardinality-explosion.md) | Prometheus cardinality explosion | SEV2 | label hygiene, monitoring-the-monitor |

## Writing one

Copy [template.md](template.md). Required sections: summary, impact, timeline
(UTC), root cause (5 whys), what went well, what went poorly, action items (each
with an owner and a tracking link). Keep it blameless.
