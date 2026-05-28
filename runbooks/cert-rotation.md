# Runbook: Certificate Rotation

**Severity:** scheduled / operational

## Impact
Expired or rotated mTLS certs break agent↔controller communication. The agent's
cert-watcher detects on-disk rotation and reloads, but a fully expired cert
needs intervention.

## Check
1. Inspect expiry: `openssl x509 -enddate -noout -in /etc/meridian/pki/agent.pem`
2. Agent logs showing TLS handshake failures.
3. CA validity (if the CA expired, everything fails at once).

## Mitigate
* Scheduled rotation: run the Ansible playbook
  `ansible-playbook deploy/ansible/playbooks/rotate-certs.yml -e new_cert_path=... -e new_key_path=...`
  which copies new certs and restarts agents.
* In k8s: update the `meridian-agent-pki` / `meridian-controller-pki` Secret;
  pods pick it up on restart (or via cert-manager if installed).
* Emergency: regenerate with `scripts/generate-certs.sh` (dev) and redistribute.

## Verify
Handshakes succeed; agents `healthy`; no TLS errors in logs.

## Prevent
Alert on cert expiry < 14 days; automate rotation via cert-manager/step-ca.

## Related
[ADR-0005](../docs/adr/0005-mtls-everywhere.md), [agent-down](agent-down.md)
