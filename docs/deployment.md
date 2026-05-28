# Deployment

Three supported paths. Same container artifacts throughout.

## Local (docker-compose)

```bash
make dev      # = generate certs + docker compose up
make down     # tear down
```

Brings up agent, controller, Postgres, Prometheus, Alertmanager, Loki, Grafana.

## Kubernetes

Kustomize:
```bash
kubectl apply -k deploy/k8s/overlays/dev
```

Helm:
```bash
helm install meridian deploy/helm/meridian -f deploy/helm/meridian/values-prod.yaml
```

The agent is a DaemonSet (one per node), the controller a 2–3 replica Deployment
with a PodDisruptionBudget, Postgres a StatefulSet, with NetworkPolicies locking
down controller ingress to agents + monitoring.

## Bare metal (Ansible)

```bash
ansible-playbook -i inventory.yml deploy/ansible/playbooks/deploy-agent.yml
```

Installs the hardened systemd unit, creates the `meridian` user, renders config
from inventory, and starts the agent. Rolling upgrades via `upgrade-agent.yml`.

## Infrastructure (Terraform)

```bash
terraform -chdir=deploy/terraform/environments/prod init
terraform -chdir=deploy/terraform/environments/prod apply
```

Provisions the cluster + node pools + IAM. Cloud-agnostic module skeletons.

## Database migrations

Alembic migrations live in `services/controller/migrations`. Apply with:
```bash
alembic -c services/controller/alembic.ini upgrade head
```
