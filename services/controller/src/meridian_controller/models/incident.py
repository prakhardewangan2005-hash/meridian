"""Incident lifecycle records."""
from __future__ import annotations

import datetime as dt

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from meridian_controller.db import Base


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)  # e.g. INC-001
    title: Mapped[str] = mapped_column(String(256))
    severity: Mapped[str] = mapped_column(String(8), default="SEV3")  # SEV1..SEV4
    status: Mapped[str] = mapped_column(String(16), default="open")     # open|mitigated|closed
    opened_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: dt.datetime.now(dt.UTC)
    )
    closed_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    postmortem_url: Mapped[str] = mapped_column(String(512), default="")
    description: Mapped[str] = mapped_column(Text, default="")
