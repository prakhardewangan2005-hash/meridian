# ADR-0005: mTLS on every control-plane hop

* Status: Accepted
* Date: 2025-07-05

## Context

Agents and operators talk to the controller over the network. We need
authentication of *both* ends and encryption in transit.

## Decision

Mutual TLS on every control-plane connection. The controller requires a client
certificate; identity is the cert CN, mapped to an RBAC role in
`config/controller/auth.yaml`. Agents verify the server cert and hostname.

## Consequences

* Strong, standard authentication with no shared secrets to leak.
* Certificate lifecycle becomes an operational concern → cert-rotation runbook +
  Ansible playbook + agent cert-watcher for hot reload.
* Slightly more setup in dev (cert generation via `scripts/generate-certs.sh`).
