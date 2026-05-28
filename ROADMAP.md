# Roadmap

Meridian is a portfolio reference implementation. This roadmap shows where it
would go next, framed as the tradeoffs a real team would weigh.

## Now (v0.1)
* Five probe types with a uniform schema
* Disk-backed buffering with at-least-once delivery
* SLO catalog as code + multi-window burn-rate alerting
* mTLS control plane, hardened agent
* Three deploy paths (compose / k8s+helm / ansible) + Terraform skeletons
* Chaos harness with auto-revert
* Runbooks linked from every alert; blameless postmortems

## Next (v0.2)
* **Push-down probe distribution**: agents pull their assignment set from the
  controller instead of loading local YAML.
* **MTU probe** as a first-class type (see INC-003 action item).
* **PSI-based agent alerts** (see INC-002 action item).
* **Cardinality guardrail** in CI (see INC-004 action item).
* **HA Prometheus / remote-write** to remove the alerting single point.

## Later (v0.3+)
* Go rewrite of the agent data plane for extreme probe density (architecture and
  wire contracts already support this — see ADR-0004).
* ASN/geo annotation of traceroute hops → path-change alerts.
* Constraint-based probe assignment (node selectors, regional sharding).
* Exactly-once delivery option for the buffer (currently at-least-once).
* Multi-tenancy (per-team SLO namespaces, RBAC scoping).

## Explicitly out of scope
* Being a metrics TSDB (we use Prometheus).
* Being an APM/tracing backend (we emit OTel; bring your own backend).
* Log storage (we ship to Loki).
