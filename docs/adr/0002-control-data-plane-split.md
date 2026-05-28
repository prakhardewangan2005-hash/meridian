# ADR-0002: Split control plane from data plane

* Status: Accepted
* Date: 2025-07-02

## Context

We need the fleet to keep measuring even when central management is unavailable.
A monolithic design where the agent depends on the controller for every action
would make the controller a single point of failure for *measurement*, not just
*management*.

## Decision

Separate a **control plane** (controller, Prometheus, Alertmanager, Loki,
Grafana, chaos) from a **data plane** of autonomous per-host agents. The agent
owns its execution loop and local buffer; the controller is advisory — it
distributes config and tracks state but is not on the measurement hot path.

## Consequences

* A controller outage degrades management but never measurement.
* Agents must hold enough local state (config + buffer) to run independently.
* Slightly more complex agent; this is the right tradeoff for reliability.
