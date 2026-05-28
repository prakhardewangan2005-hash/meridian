# ADR-0006: Disk-backed buffer on the agent

* Status: Accepted
* Date: 2025-07-06

## Context

Probe results must survive a collector/controller outage and an agent restart
without unbounded memory growth.

## Decision

A disk-backed ring buffer: length-prefixed NDJSON records in rotating 16 MiB
segments, fsync every 64 writes, evict oldest segments past a size cap, with a
drain/ack contract for at-least-once delivery.

## Consequences

* No data loss across restarts (segments are on disk).
* Bounded disk usage (size cap with oldest-first eviction).
* fsync-every-64 trades a tiny durability window for throughput; acceptable for
  telemetry where the newest data matters most.
* At-least-once (not exactly-once) delivery — consumers must tolerate duplicates.
