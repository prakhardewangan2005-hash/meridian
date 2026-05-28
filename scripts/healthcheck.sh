#!/usr/bin/env bash
# Quick end-to-end health check of a running stack.
set -uo pipefail

check() { printf "%-28s" "$1:"; if eval "$2" >/dev/null 2>&1; then echo "OK"; else echo "FAIL"; fi; }

check "agent metrics"      "curl -sf http://localhost:9101/metrics"
check "controller healthz" "curl -skf https://localhost:8443/healthz"
check "controller readyz"  "curl -skf https://localhost:8443/readyz"
check "prometheus"         "curl -sf http://localhost:9090/-/healthy"
check "alertmanager"       "curl -sf http://localhost:9093/-/healthy"
check "loki"               "curl -sf http://localhost:3100/ready"
check "grafana"            "curl -sf http://localhost:3000/api/health"
