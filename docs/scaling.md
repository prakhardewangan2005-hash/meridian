# Scaling

## Agent

The agent's cost is bounded by probe count × frequency. Concurrency is capped by
a semaphore (`probes.max_concurrent`, default 64) so a burst of slow probes can't
exhaust file descriptors. Memory is bounded by the buffer size cap and
`MemoryMax` in the unit. A single agent comfortably runs hundreds of probes.

## Controller

The hot path (heartbeats + Prometheus scrapes of the agents) does not touch the
controller — agents are scraped directly. The controller handles registration,
probe distribution (periodic reconcile), SLO evaluation (periodic), and the API.
All of these are low-frequency relative to fleet size, so one replica scales to
thousands of nodes. Add replicas behind the service for HA, not throughput.

State lives entirely in Postgres; the controller process is stateless, which is
what makes horizontal scaling trivial.

## Prometheus

The usual scaling concern. Cardinality is the enemy: the uniform probe schema
keeps label sets bounded (probe, target, type, status), which is deliberate.
[INC-004](../incident-reports/INC-004-prometheus-cardinality-explosion.md) is a
postmortem of what happens when that discipline slips. For very large fleets,
shard Prometheus by region and federate, or move to a remote-write backend.

## Postgres

The schema is small (inventory + SLO snapshots + incidents). Snapshot rows grow
over time; a retention job trims `slo_budget_snapshots` beyond N days. For HA,
use a managed Postgres with a read replica and connection pooling.

## Numbers to keep in mind

| Dimension | Comfortable single-instance ceiling |
|---|---|
| Probes per agent | ~500 at 30s interval |
| Agents per controller replica | ~5,000 |
| Active series in Prometheus | depends on retention/hardware; keep cardinality bounded |
