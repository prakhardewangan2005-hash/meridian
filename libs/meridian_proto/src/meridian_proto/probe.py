"""Probe result wire schema — the contract between agent and any consumer."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

ProbeStatus = Literal["ok", "fail", "timeout", "error"]


class ProbeResultMessage(BaseModel):
    """Serialized probe result. Matches agent ProbeResult.to_dict()."""

    probe_name: str
    probe_type: str
    target: str
    status: ProbeStatus
    latency_s: float
    timestamp: float
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
