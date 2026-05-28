# Observability

Meridian keeps **three separate observability paths** and does not conflate them.

## Metrics path

Agent exposes Prometheus metrics on `:9101/metrics`. Prometheus scrapes, applies
recording rules ([config/prometheus/recording-rules/](../config/prometheus/recording-rules/)),
evaluates alerts, and forwards to Alertmanager. Grafana reads from Prometheus.

Core metric families:

| Metric | Type | Meaning |
|---|---|---|
| `meridian_probe_success` | gauge | 1/0 last execution result |
| `meridian_probe_latency_seconds` | histogram | probe latency distribution |
| `meridian_probe_last_run_timestamp` | gauge | staleness detection |
| `meridian_probe_executions_total` | counter | rate + success-ratio SLIs |
| `meridian_system` | gauge | labeled Linux system metric |
| `meridian_network` | gauge | per-interface counters |
| `meridian_controller_requests_total` | counter | controller API SLI |

## Logs path

Agent ships structured JSON logs (via structlog) to Loki. Probe results are also
logged as structured events so they can be queried in Grafana's Loki explorer
without touching Prometheus. Logs and metrics share label conventions (host,
service) for correlation.

## Traces path

The controller is instrumented with OpenTelemetry (FastAPI auto-instrumentation,
optional). Traces capture request flow through the API and into Postgres. Traces
are kept separate from metrics/logs because their storage and retention profiles
differ fundamentally.

## Why not one pipeline

Forcing metrics, logs, and traces through a single agent/pipeline couples their
failure domains: a logging backpressure event shouldn't stall metric scraping.
Keeping them independent means each can fail without taking the others down.

## RED and USE

* Probes are monitored with **RED** (Rate, Errors, Duration) — execution rate,
  failure ratio, latency histogram.
* Hosts are monitored with **USE** (Utilization, Saturation, Errors) — CPU/mem
  utilization, PSI saturation, interface errors/drops.
