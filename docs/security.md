# Security

## Threat model (abridged)

| Asset | Threat | Mitigation |
|---|---|---|
| Control-plane traffic | MITM, spoofed agents | mTLS, cert CN → RBAC |
| Agent host | privilege escalation | non-root user, single capability, systemd hardening |
| Postgres credentials | leakage | secrets via k8s Secret / Ansible vault, never in images |
| Container supply chain | vulnerable deps, malicious base | distroless base, Trivy + CodeQL in CI, pinned deps |
| Chaos service | accidental blast radius | dry-run default, mandatory duration, auto-revert watchdog |

## mTLS everywhere

Every control-plane hop is mutually authenticated. The controller requires a
client cert (`ssl_cert_reqs=CERT_REQUIRED`); the agent verifies the server cert
and checks hostname. Identity is the client cert CN, mapped to a role in
[config/controller/auth.yaml](../config/controller/auth.yaml). See
[ADR-0005](adr/0005-mtls-everywhere.md).

## Agent least privilege

The systemd unit
([services/agent/systemd/meridian-agent.service](../services/agent/systemd/meridian-agent.service)):

* runs as the `meridian` system user (no shell, no home)
* `AmbientCapabilities=CAP_NET_RAW` and `CapabilityBoundingSet=CAP_NET_RAW` —
  exactly one capability, for ICMP/traceroute
* `NoNewPrivileges`, `ProtectSystem=strict`, `ProtectHome`, `PrivateTmp`,
  `PrivateDevices`, `ProtectKernelTunables/Modules/ControlGroups`
* `MemoryDenyWriteExecute`, `RestrictNamespaces`, `LockPersonality`
* `SystemCallFilter=@system-service` minus `@privileged @resources`
* resource caps: `MemoryMax`, `TasksMax`, `LimitNOFILE`

The Kubernetes DaemonSet mirrors this: `runAsNonRoot`, `readOnlyRootFilesystem`,
`drop: ALL` then `add: NET_RAW`, `seccompProfile: RuntimeDefault`.

## Secrets handling

No secret is ever baked into an image. Postgres DSN and password come from a
Kubernetes Secret (`meridian-db`) or Ansible-templated file with `0600`. The
`gitleaks` pre-commit hook and CI step block accidental commits.

## Supply chain

Distroless runtime image (no shell, minimal attack surface). `trivy.yml` scans
images; `codeql.yml` does static analysis; Dependabot keeps deps current. All
third-party actions and base images are version-pinned.
