"""Tiny health-check helpers usable by any service."""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass


@dataclass(slots=True)
class Check:
    name: str
    fn: Callable[[], Awaitable[bool]]


async def run_checks(checks: list[Check]) -> tuple[bool, dict[str, bool]]:
    results: dict[str, bool] = {}
    for c in checks:
        try:
            results[c.name] = await c.fn()
        except Exception:
            results[c.name] = False
    return all(results.values()), results
