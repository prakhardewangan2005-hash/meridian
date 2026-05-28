"""Node ORM model."""
from __future__ import annotations

import datetime as dt
from typing import Any

from sqlalchemy import JSON, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from meridian_controller.db import Base


class Node(Base):
    __tablename__ = "nodes"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    hostname: Mapped[str] = mapped_column(String(256))
    kernel: Mapped[str] = mapped_column(String(128), default="")
    arch: Mapped[str] = mapped_column(String(32), default="")
    python_version: Mapped[str] = mapped_column(String(32), default="")
    labels: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    registered_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: dt.datetime.now(dt.UTC)
    )
    last_heartbeat: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: dt.datetime.now(dt.UTC)
    )
    state: Mapped[str] = mapped_column(String(32), default="healthy")
