# ADR-0004: Python for the control plane

* Status: Accepted
* Date: 2025-07-04

## Context

The control plane is I/O-bound (API, DB, Prometheus queries). We want fast
iteration and a strong async ecosystem.

## Decision

Implement the control plane and agent in Python 3.12 with asyncio, FastAPI,
SQLAlchemy, and structlog. Use uvloop where available.

## Consequences

* Rapid development, rich library ecosystem, easy to read for reviewers.
* GIL is a non-issue for I/O-bound work; CPU-bound paths (checksums) are trivial.
* If the data plane ever needs to scale to extreme probe densities, the agent
  could be rewritten in Go without changing the architecture or wire contracts
  (the schemas live in `meridian_proto`).
