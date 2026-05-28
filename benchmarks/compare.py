#!/usr/bin/env python3
"""Compare a benchmark result against a baseline; exit 1 on >10% regression."""
from __future__ import annotations

import argparse
import json
import sys

THRESHOLD = 0.10  # 10%


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("baseline")
    ap.add_argument("candidate")
    args = ap.parse_args()

    with open(args.baseline) as f:
        base = json.load(f)
    with open(args.candidate) as f:
        cand = json.load(f)

    # Higher-is-better metric
    key = "throughput_per_s"
    if key not in base or key not in cand:
        print(f"no comparable '{key}' in both files; skipping gate")
        return 0

    b, c = base[key], cand[key]
    delta = (c - b) / b
    print(f"baseline={b} candidate={c} delta={delta:+.1%}")
    if delta < -THRESHOLD:
        print(f"REGRESSION: throughput dropped more than {THRESHOLD:.0%}")
        return 1
    print("OK: within threshold")
    return 0


if __name__ == "__main__":
    sys.exit(main())
