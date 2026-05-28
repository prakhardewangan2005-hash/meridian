"""Add SLO tables.

Revision ID: 0002
Revises: 0001
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "slo_definitions",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(128), nullable=False, unique=True),
        sa.Column("service", sa.String(128), nullable=False),
        sa.Column("description", sa.Text, nullable=False, server_default=""),
        sa.Column("sli_query", sa.Text, nullable=False),
        sa.Column("objective_pct", sa.Float, nullable=False),
        sa.Column("window_days", sa.Integer, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_slo_definitions_name", "slo_definitions", ["name"])
    op.create_table(
        "slo_budget_snapshots",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("slo_id", sa.Integer, sa.ForeignKey("slo_definitions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sli_value", sa.Float, nullable=False),
        sa.Column("burn_rate_1h", sa.Float, nullable=False, server_default="0"),
        sa.Column("burn_rate_6h", sa.Float, nullable=False, server_default="0"),
        sa.Column("error_budget_remaining_pct", sa.Float, nullable=False, server_default="100"),
    )
    op.create_index("ix_slo_budget_snapshots_slo_id", "slo_budget_snapshots", ["slo_id"])


def downgrade() -> None:
    op.drop_index("ix_slo_budget_snapshots_slo_id", table_name="slo_budget_snapshots")
    op.drop_table("slo_budget_snapshots")
    op.drop_index("ix_slo_definitions_name", table_name="slo_definitions")
    op.drop_table("slo_definitions")
