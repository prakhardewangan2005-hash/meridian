#!/usr/bin/env bash
# One-shot local development bootstrap.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "==> generating dev certs"
./scripts/generate-certs.sh ./pki

echo "==> starting the stack"
docker compose up -d

echo "==> waiting for controller readiness"
for i in $(seq 1 30); do
  if curl -sk https://localhost:8443/readyz >/dev/null 2>&1; then
    echo "controller ready"; break
  fi
  sleep 2
done

echo "==> Grafana:    http://localhost:3000 (admin/admin)"
echo "==> Prometheus: http://localhost:9090"
echo "==> Alertmgr:   http://localhost:9093"
