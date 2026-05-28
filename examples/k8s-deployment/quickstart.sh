#!/usr/bin/env bash
set -euo pipefail
NS=meridian
kubectl create namespace "$NS" --dry-run=client -o yaml | kubectl apply -f -
echo "Create the required secrets (db, pki) then:"
echo "  kubectl apply -k deploy/k8s/overlays/dev"
