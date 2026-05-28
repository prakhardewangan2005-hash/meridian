#!/usr/bin/env python3
"""Hammer the controller API with concurrent clients and report latency.

Requires a running controller. In CI this runs against the compose stack.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import statistics
import time

try:
    import httpx
except ImportError:
    httpx = None


async def run(url: str, requests: int, concurrency: int) -> dict:
    if httpx is None:
        return {"benchmark": "controller_api_load", "skipped": "httpx not installed"}
    latencies: list[float] = []
    sem = asyncio.Semaphore(concurrency)

    async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
        async def one() -> None:
            async with sem:
                t = time.perf_counter()
                try:
                    await client.get(f"{url}/healthz")
                    latencies.append(time.perf_counter() - t)
                except Exception:
                    pass

        await asyncio.gather(*(one() for _ in range(requests)))

    if not latencies:
        return {"benchmark": "controller_api_load", "error": "no successful requests"}
    return {
        "benchmark": "controller_api_load",
        "requests": len(latencies),
        "p50_ms": round(statistics.median(latencies) * 1000, 2),
        "p99_ms": round(sorted(latencies)[int(len(latencies) * 0.99)] * 1000, 2),
        "concurrency": concurrency,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="https://localhost:8443")
    ap.add_argument("--requests", type=int, default=500)
    ap.add_argument("--concurrency", type=int, default=20)
    ap.add_argument("--out", default="results/latest-api.json")
    args = ap.parse_args()
    result = asyncio.run(run(args.url, args.requests, args.concurrency))
    print(json.dumps(result, indent=2))
    with open(args.out, "w") as f:
        json.dump(result, f, indent=2)


if __name__ == "__main__":
    main()
