"""Alert payload schema (Alertmanager webhook shape, trimmed)."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

AlertStatus = Literal["firing", "resolved"]


class Alert(BaseModel):
    status: AlertStatus
    labels: dict[str, str] = Field(default_factory=dict)
    annotations: dict[str, str] = Field(default_factory=dict)
    starts_at: str = Field(alias="startsAt", default="")
    ends_at: str = Field(alias="endsAt", default="")
    generator_url: str = Field(alias="generatorURL", default="")


class AlertGroup(BaseModel):
    version: str = "4"
    status: AlertStatus
    receiver: str = ""
    group_labels: dict[str, str] = Field(alias="groupLabels", default_factory=dict)
    alerts: list[Alert] = Field(default_factory=list)
