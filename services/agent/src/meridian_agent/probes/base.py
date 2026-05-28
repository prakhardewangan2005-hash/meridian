"""Probe ABC + ProbeResult.

Every probe returns the same shape. That uniformity is what lets the Prometheus
exporter, the buffer, and the controller all consume probe output without
probe-type-specific branching.
"""
from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from typing import Any, Literal

ProbeStatus = Literal["ok", "fail", "timeout", "error"]


@dataclass(slots=True, frozen=True)
class ProbeResult:
    """Uniform result shape across all probe types.

    metadata is intentionally untyped — probes attach what they need
    (DNS answers, traceroute hops, HTTP body length, etc.).
    """

    probe_name: str
    probe_type: str
    target: str
    status: ProbeStatus
    latency_s: float
    timestamp: float
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def success(self) -> bool:
        return self.status == "ok"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def ok(cls, probe: Probe, latency_s: float, **metadata: Any) -> ProbeResult:
        return cls(
            probe_name=probe.name,
            probe_type=probe.probe_type,
            target=probe.target,
            status="ok",
            latency_s=latency_s,
            timestamp=time.time(),
            metadata=metadata,
        )

    @classmethod
    def fail(
        cls, probe: Probe, latency_s: float, error: str, **metadata: Any
    ) -> ProbeResult:
        return cls(
            probe_name=probe.name,
            probe_type=probe.probe_type,
            target=probe.target,
            status="fail",
            latency_s=latency_s,
            timestamp=time.time(),
            error=error,
            metadata=metadata,
        )

    @classmethod
    def timeout(cls, probe: Probe) -> ProbeResult:
        return cls(
            probe_name=probe.name,
            probe_type=probe.probe_type,
            target=probe.target,
            status="timeout",
            latency_s=probe.timeout_s,
            timestamp=time.time(),
            error="timeout",
        )

    @classmethod
    def errored(cls, probe: Probe, error: str) -> ProbeResult:
        return cls(
            probe_name=probe.name,
            probe_type=probe.probe_type,
            target=probe.target,
            status="error",
            latency_s=0.0,
            timestamp=time.time(),
            error=error,
        )


class Probe(ABC):
    """Abstract probe.

    Subclasses must:
      * set probe_type as a class attribute
      * implement execute() returning a ProbeResult (and never raise)
    """

    probe_type: str = "abstract"

    def __init__(
        self,
        *,
        name: str,
        target: str,
        interval_s: float = 30.0,
        timeout_s: float = 5.0,
        jitter_s: float = 2.0,
        labels: dict[str, str] | None = None,
    ) -> None:
        self.name = name
        self.target = target
        self.interval_s = interval_s
        self.timeout_s = timeout_s
        self.jitter_s = jitter_s
        self.labels = labels or {}

    @abstractmethod
    async def execute(self) -> ProbeResult:
        """Single execution. MUST NOT raise — convert all errors to ProbeResult."""
        ...

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {self.name!r} target={self.target!r}>"
