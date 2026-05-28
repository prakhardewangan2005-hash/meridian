# meridian-controller

The central control plane. FastAPI app, PostgreSQL inventory, SLO evaluator.

## Responsibilities

* Agent registration and heartbeat tracking
* Probe definition CRUD; probe-to-node assignment
* SLO definition CRUD; periodic burn-rate computation by querying Prometheus
* Incident lifecycle (open, update, close, postmortem link)
* Chaos experiment orchestration (delegates execution to the chaos service)
* Self-observability (`/metrics`, OpenTelemetry traces)

## API

`GET /healthz` — process alive
`GET /readyz` — DB reachable
`GET /metrics` — Prometheus exposition

`POST /api/v1/nodes/register`
`POST /api/v1/nodes/{node_id}/heartbeat`
`GET  /api/v1/nodes`

`GET    /api/v1/probes`
`POST   /api/v1/probes`
`PUT    /api/v1/probes/{id}`
`DELETE /api/v1/probes/{id}`

`GET  /api/v1/slos`
`POST /api/v1/slos`
`GET  /api/v1/slos/{id}/burn-rate`

`POST /api/v1/incidents`
`GET  /api/v1/incidents`
`PUT  /api/v1/incidents/{id}`

`POST /api/v1/chaos/inject`
`GET  /api/v1/chaos`
`DELETE /api/v1/chaos/{id}`

## Authentication

mTLS. Client cert subject becomes the identity. RBAC policy in
[`config/controller/auth.yaml`](../../config/controller/auth.yaml).
