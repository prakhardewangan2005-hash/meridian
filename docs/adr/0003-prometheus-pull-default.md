# ADR-0003: Prometheus pull model as the metrics default

* Status: Accepted
* Date: 2025-07-03

## Context

Metrics can be pushed (agent → collector) or pulled (collector scrapes agent).

## Decision

Use the Prometheus pull model for metrics. The agent exposes `:9101/metrics` and
Prometheus scrapes it. Logs use push (Loki) because that's their natural model.

## Consequences

* Free liveness signal: a failed scrape *is* a monitoring signal (`up == 0`).
* No agent-side push buffering for metrics; the buffer is for the logs/results
  path only.
* Service discovery needed at scale (handled by k8s annotations / SD configs).
* Pushgateway remains available for the rare batch-job case, but is not default.
