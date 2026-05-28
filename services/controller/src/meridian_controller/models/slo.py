"""SLO definition + budget snapshot ORM models."""
from __future__ import annotations

import datetime as dt

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from meridian_controller.db import Base


class SLODefinition(Base):
    __tablename__ = "slo_definitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    service: Mapped[str] = mapped_column(String(128))
    description: Mapped[str] = mapped_column(Text, default="")
    sli_query: Mapped[str] = mapped_column(Text)
    objective_pct: Mapped[float] = mapped_column(Float)  # e.g. 99.9
    window_days: Mapped[int] = mapped_column(Integer)  # e.g. 30
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: dt.datetime.now(dt.UTC)
    )


class SLOBudgetSnapshot(Base):
    __tablename__ = "slo_budget_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slo_id: Mapped[int] = mapped_column(
        ForeignKey("slo_definitions.id", ondelete="CASCADE"), index=True,
    )
    captured_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: dt.datetime.now(dt.UTC)
    )
    sli_value: Mapped[float] = mapped_column(Float)
    burn_rate_1h: Mapped[float] = mapped_column(Float, default=0.0)
    burn_rate_6h: Mapped[float] = mapped_column(Float, default=0.0)
    error_budget_remaining_pct: Mapped[float] = mapped_column(Float, default=100.0)
