# Security Policy

## Reporting a vulnerability

Please report security issues **privately** via GitHub Security Advisories
("Report a vulnerability" in the Security tab), not as public issues. We aim to
acknowledge within 3 business days.

Include: affected component/version, reproduction steps, and impact.

## Supported versions

| Version | Supported |
|---|---|
| 0.1.x | yes |

## Security posture

* mTLS on every control-plane hop; identity = client-cert CN → RBAC.
* Agent runs non-root with a single capability (`CAP_NET_RAW`) and a hardened
  systemd unit / restricted PodSecurity.
* Distroless runtime images; Trivy + CodeQL in CI; Dependabot for deps.
* No secrets in images or git (gitleaks pre-commit + CI).

See [docs/security.md](docs/security.md) for the threat model.
