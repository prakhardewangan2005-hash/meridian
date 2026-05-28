"""Initial schema.

Revision ID: 0001
Revises:
Create Date: 2025-08-15 00:00:00
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "nodes",
        sa.Column("id", sa.String(128), primary_key=True),
        sa.Column("hostname", sa.String(256), nullable=False),
        sa.Column("kernel", sa.String(128), nullable=False, server_default=""),
        sa.Column("arch", sa.String(32), nullable=False, server_default=""),
        sa.Column("python_version", sa.String(32), nullable=False, server_default=""),
        sa.Column("labels", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("registered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_heartbeat", sa.DateTime(timezone=True), nullable=False),
        sa.Column("state", sa.String(32), nullable=False, server_default="healthy"),
    )
    op.create_table(
        "probe_definitions",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(128), nullable=False, unique=True),
        sa.Column("probe_type", sa.String(32), nullable=False),
        sa.Column("target", sa.String(512), nullable=False),
        sa.Column("interval_s", sa.Float, nullable=False, server_default="30.0"),
        sa.Column("timeout_s", sa.Float, nullable=False, server_default="5.0"),
        sa.Column("jitter_s", sa.Float, nullable=False, server_default="2.0"),
        sa.Column("params", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_probe_definitions_name", "probe_definitions", ["name"])


def downgrade() -> None:
    op.drop_index("ix_probe_definitions_name", table_name="probe_definitions")
    op.drop_table("probe_definitions")
    op.drop_table("nodes")
