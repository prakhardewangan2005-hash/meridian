"""Jitter helpers for spreading scheduled work."""
from __future__ import annotations

import random


def full_jitter(base_s: float) -> float:
    """AWS-style full jitter: uniform(0, base)."""
    return random.uniform(0, base_s)


def equal_jitter(base_s: float) -> float:
    """Half fixed, half random."""
    return base_s / 2 + random.uniform(0, base_s / 2)


def decorrelated_jitter(prev_s: float, base_s: float, cap_s: float) -> float:
    """Decorrelated jitter — good for retry backoff."""
    return min(cap_s, random.uniform(base_s, prev_s * 3))
