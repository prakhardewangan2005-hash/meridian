# Meridian — Terraform

Provisions the infrastructure substrate for a Meridian deployment: a managed
Kubernetes cluster, node pools sized for the agent DaemonSet + controller, and
the IAM/identity bindings the platform needs.

```bash
cd environments/dev
terraform init
terraform plan
terraform apply
```

Modules:
* `modules/meridian-cluster` — Kubernetes cluster + node pools
* `modules/meridian-iam`     — service accounts, roles, workload identity

These are written cloud-agnostically with variables; wire them to your provider
of choice (the examples use a generic `kubernetes`-style interface).
