# Kubernetes Deployment

## With kustomize
```bash
kubectl apply -k deploy/k8s/overlays/dev
kubectl -n meridian get pods
```

## With Helm
```bash
helm install meridian deploy/helm/meridian \
  --namespace meridian --create-namespace \
  -f deploy/helm/meridian/values.yaml
```

Production values:
```bash
helm install meridian deploy/helm/meridian \
  -n meridian --create-namespace \
  -f deploy/helm/meridian/values-prod.yaml
```

## Prerequisites
* A Secret `meridian-db` with keys `dsn` and `password`
* Secrets `meridian-agent-pki` / `meridian-controller-pki` with the mTLS material
* A ConfigMap `meridian-agent-config` with `agent.yaml`

See [deploy/k8s/base](../../deploy/k8s/base) for the raw manifests.
