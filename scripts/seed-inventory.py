#!/usr/bin/env python3
"""Seed the controller with sample nodes, probes, and SLOs for demos/dev."""
from __future__ import annotations

import argparse
import os
import sys

try:
    import httpx
except ImportError:
    print("httpx required: pip install httpx", file=sys.stderr)
    sys.exit(1)

SAMPLE_PROBES = [
    {"name": "resolve-example", "probe_type": "dns", "target": "example.com",
     "interval_s": 30, "timeout_s": 5},
    {"name": "http-example", "probe_type": "http", "target": "https://example.com/",
     "interval_s": 30, "timeout_s": 5},
    {"name": "ping-gateway", "probe_type": "icmp", "target": "10.0.0.1",
     "interval_s": 15, "timeout_s": 5},
]

SAMPLE_SLOS = [
    {"name": "probe_success_ratio", "service": "probe-fleet",
     "sli_query": "sum(rate(meridian_probe_executions_total{status=\"ok\"}[5m]))/sum(rate(meridian_probe_executions_total[5m]))",
     "objective_pct": 99.0, "window_days": 30},
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=os.environ.get("MERIDIAN_CONTROLLER_URL", "https://localhost:8443"))
    args = ap.parse_args()

    with httpx.Client(base_url=args.url, verify=False, timeout=10.0) as c:
        for p in SAMPLE_PROBES:
            r = c.post("/api/v1/probes", json=p)
            print(f"probe {p['name']}: HTTP {r.status_code}")
        for s in SAMPLE_SLOS:
            r = c.post("/api/v1/slos", json=s)
            print(f"slo {s['name']}: HTTP {r.status_code}")


if __name__ == "__main__":
    main()
