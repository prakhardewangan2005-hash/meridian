# ADR-0007: One result schema for all probe types

* Status: Accepted
* Date: 2025-07-07

## Context

DNS, ICMP, TCP, HTTP, and traceroute probes produce different details. Without
discipline, each would grow its own metrics and need its own dashboards/alerts.

## Decision

All probes return a single `ProbeResult` shape: status ∈ {ok, fail, timeout,
error}, latency, timestamp, and a free-form `metadata` dict for type-specific
fields. The Prometheus exporter emits the same metric families for every type,
labeled by `type`.

## Consequences

* One dashboard and one alert rule generalize across all probe types.
* Bounded label cardinality (probe, target, type, status) — protects Prometheus.
* Type-specific richness lives in `metadata` / logs, not in metric labels.
* New probe types are additive: implement the ABC, register, done.
