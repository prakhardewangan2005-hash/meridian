"""System metric wire schema."""
from __future__ import annotations

from pydantic import BaseModel, Field


class SystemMetricMessage(BaseModel):
    node_id: str
    timestamp: float
    scalar: dict[str, float] = Field(default_factory=dict)
    network: dict[str, dict[str, float]] = Field(default_factory=dict)
