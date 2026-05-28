# Automation Guide

Everything in Meridian is driven from declarative source.

## Probes as code

Probe definitions live in YAML and are applied via the CLI:

```bash
meridianctl probes apply -f config/agent/probes.example.yaml
```

The controller distributes them to agents. No imperative "add this probe to that
box" — you change the file, apply, and the distributor reconciles.

## SLOs as code

[config/slo/slo-catalog.yaml](../config/slo/slo-catalog.yaml) is the source of
truth. CI renders it to [docs/slo-catalog.md](slo-catalog.md) and the burn-rate
recording rules are generated from it. Changing an objective is a reviewed PR,
not a console click.

## Deployment as code

Three paths, same artifacts:

* **Kubernetes**: `kubectl apply -k deploy/k8s/overlays/<env>` or
  `helm install meridian deploy/helm/meridian`
* **Bare metal**: `ansible-playbook deploy/ansible/playbooks/deploy-agent.yml`
* **Infra**: `terraform -chdir=deploy/terraform/environments/<env> apply`

## CI-driven operations

| Workflow | Triggers | Gate |
|---|---|---|
| `ci.yml` | PR | tests must pass |
| `lint.yml` | PR | ruff + mypy + yamllint + hadolint + shellcheck |
| `chaos-test.yml` | nightly | chaos scenarios must hold SLOs |
| `perf-regression.yml` | PR | fails on >10% throughput regression |
| `trivy.yml` / `codeql.yml` | PR + schedule | no high-severity findings |

## Rolling upgrades

The Ansible `upgrade-agent.yml` playbook upgrades 25% of the fleet at a time
(`serial: 25%`) with a health gate (`max_fail_percentage: 10`) and a post-task
that waits for the metrics endpoint to return 200 before proceeding.
