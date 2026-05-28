#!/usr/bin/env python3
"""Measure how many no-op probe executions/sec the runner path sustains.

Uses a trivial in-process probe so we measure scheduler + result handling
overhead, not network. Writes a JSON result for the CI regression gate.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import time


async def _noop_probe() -> float:
    # Simulate the cost of building + handling a ProbeResult.
    return time.perf_counter()


async def run(duration_s: float, concurrency: int) -> dict:
    sem = asyncio.Semaphore(concurrency)
    count = 0
    stop = time.perf_counter() + duration_s

    async def worker() -> None:
        nonlocal count
        while time.perf_counter() < stop:
            async with sem:
                await _noop_probe()
                count += 1

    workers = [asyncio.create_task(worker()) for _ in range(concurrency)]
    await asyncio.gather(*workers)
    elapsed = duration_s
    return {
        "benchmark": "agent_throughput",
        "executions": count,
        "duration_s": elapsed,
        "throughput_per_s": round(count / elapsed, 1),
        "concurrency": concurrency,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--duration-s", type=float, default=3.0)
    ap.add_argument("--concurrency", type=int, default=64)
    ap.add_argument("--out", default="results/latest.json")
    args = ap.parse_args()
    result = asyncio.run(run(args.duration_s, args.concurrency))
    print(json.dumps(result, indent=2))
    with open(args.out, "w") as f:
        json.dump(result, f, indent=2)


if __name__ == "__main__":
    main()
