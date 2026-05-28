# Runbook: Deploy Rollback

**Severity:** operational

## When
A recent deploy correlates with a regression (error rate, latency, crashes).
When in doubt, roll back first and investigate after — restoring service beats
root-causing live.

## Kubernetes
```bash
kubectl -n meridian rollout undo deployment/meridian-controller
kubectl -n meridian rollout status deployment/meridian-controller
```
For Helm: `helm rollback meridian <previous-revision>`.

## Bare metal (Ansible)
Re-run the upgrade playbook pinned to the previous version:
```bash
ansible-playbook deploy/ansible/playbooks/upgrade-agent.yml -e meridian_version=<prev>
```
The playbook upgrades 25% at a time with a health gate.

## Database migrations
If the bad deploy ran a migration, rolling back code is not enough. Check whether
the migration is backward-compatible. If not:
```bash
alembic -c services/controller/alembic.ini downgrade -1
```
Prefer expand/contract migrations precisely so code rollback is always safe.

## Verify
Regression clears; `/readyz` healthy; burn rate < 1.

## Related
[controller-degraded](controller-degraded.md)
