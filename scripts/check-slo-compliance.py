#!/usr/bin/env python3
"""Query current SLO compliance directly from Prometheus and print a table.

Reads the SLO catalog, runs each SLI query, prints SLI vs objective and whether
the SLO is currently met.
"""
from __future__ import annotations

import argparse
import sys

try:
    import httpx
    import yaml
except ImportError:
    print("requires httpx + pyyaml", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prometheus", default="http://localhost:9090")
    ap.add_argument("--catalog", default="config/slo/slo-catalog.yaml")
    args = ap.parse_args()

    with open(args.catalog) as f:
        catalog = yaml.safe_load(f)

    print(f"{'SLO':<32}{'SLI':>10}{'OBJ':>8}{'STATUS':>10}")
    print("-" * 60)
    with httpx.Client(timeout=10.0) as c:
        for obj in catalog.get("objectives", []):
            try:
                r = c.get(f"{args.prometheus}/api/v1/query",
                          params={"query": obj["sli_query"]})
                data = r.json()
                result = data.get("data", {}).get("result", [])
                sli = float(result[0]["value"][1]) * 100 if result else 0.0
            except Exception:
                sli = float("nan")
            status = "MET" if sli >= obj["objective_pct"] else "BREACH"
            print(f"{obj['name']:<32}{sli:>9.2f}%{obj['objective_pct']:>7.2f}%{status:>10}")


if __name__ == "__main__":
    main()
