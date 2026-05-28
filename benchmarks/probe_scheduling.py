#!/usr/bin/env python3
"""Measure scheduler jitter: how far actual run times drift from the target
interval under load."""
from __future__ import annotations

import argparse
import asyncio
import json
import statistics
import time


async def run(interval_s: float, cycles: int) -> dict:
    drifts: list[float] = []
    loop = asyncio.get_running_loop()
    target = loop.time()
    for _ in range(cycles):
        target += interval_s
        now = loop.time()
        sleep_for = max(0.0, target - now)
        await asyncio.sleep(sleep_for)
        drifts.append(abs(loop.time() - target))
    return {
        "benchmark": "probe_scheduling",
        "interval_s": interval_s,
        "cycles": cycles,
        "mean_drift_ms": round(statistics.fmean(drifts) * 1000, 3),
        "p99_drift_ms": round(sorted(drifts)[int(len(drifts) * 0.99)] * 1000, 3),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--interval-s", type=float, default=0.01)
    ap.add_argument("--cycles", type=int, default=200)
    ap.add_argument("--out", default="results/latest-sched.json")
    args = ap.parse_args()
    result = asyncio.run(run(args.interval_s, args.cycles))
    print(json.dumps(result, indent=2))
    with open(args.out, "w") as f:
        json.dump(result, f, indent=2)


if __name__ == "__main__":
    main()
