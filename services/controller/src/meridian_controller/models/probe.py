"""Probe definition ORM model."""
from __future__ import annotations

import datetime as dt
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from meridian_controller.db import Base


class ProbeDefinition(Base):
    __tablename__ = "probe_definitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    probe_type: Mapped[str] = mapped_column(String(32))
    target: Mapped[str] = mapped_column(String(512))
    interval_s: Mapped[float] = mapped_column(Float, default=30.0)
    timeout_s: Mapped[float] = mapped_column(Float, default=5.0)
    jitter_s: Mapped[float] = mapped_column(Float, default=2.0)
    params: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: dt.datetime.now(dt.UTC)
    )


class ProbeAssignment(Base):
    """Many-to-many: which probe runs on which node."""
    __tablename__ = "probe_assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    probe_id: Mapped[int] = mapped_column(
        ForeignKey("probe_definitions.id", ondelete="CASCADE"), index=True,
    )
    node_id: Mapped[str] = mapped_column(
        ForeignKey("nodes.id", ondelete="CASCADE"), index=True,
    )
    assigned_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: dt.datetime.now(dt.UTC)
    )
