"""SLO definition wire schema — mirrors config/slo/slo-catalog.yaml entries."""
from __future__ import annotations

from pydantic import BaseModel, Field


class SLOObjective(BaseModel):
    name: str
    service: str
    description: str = ""
    sli_query: str
    objective_pct: float = Field(ge=0, le=100)
    window_days: int = Field(ge=1, le=365)


class SLOCatalog(BaseModel):
    version: int = 1
    objectives: list[SLOObjective] = Field(default_factory=list)
