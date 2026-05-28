"""Async retry with exponential backoff + jitter."""
from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

import structlog

from meridian_common.jitter import full_jitter

log = structlog.get_logger(__name__)
T = TypeVar("T")


async def retry_async(
    fn: Callable[[], Awaitable[T]],
    *,
    attempts: int = 5,
    base_delay_s: float = 0.5,
    max_delay_s: float = 30.0,
    retry_on: tuple[type[Exception], ...] = (Exception,),
) -> T:
    """Retry an async callable with capped exponential backoff and full jitter."""
    last_exc: Exception | None = None
    delay = base_delay_s
    for attempt in range(1, attempts + 1):
        try:
            return await fn()
        except retry_on as exc:  # noqa: PERF203
            last_exc = exc
            if attempt == attempts:
                break
            sleep_for = full_jitter(min(delay, max_delay_s))
            log.warning(
                "retry.attempt_failed",
                attempt=attempt,
                max_attempts=attempts,
                retry_in_s=round(sleep_for, 2),
            )
            await asyncio.sleep(sleep_for)
            delay *= 2
    assert last_exc is not None
    raise last_exc
