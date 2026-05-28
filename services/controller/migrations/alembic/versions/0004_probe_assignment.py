"""Add probe_assignments table.

Revision ID: 0004
Revises: 0003
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "probe_assignments",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "probe_id", sa.Integer,
            sa.ForeignKey("probe_definitions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "node_id", sa.String(128),
            sa.ForeignKey("nodes.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_probe_assignments_probe_id", "probe_assignments", ["probe_id"])
    op.create_index("ix_probe_assignments_node_id", "probe_assignments", ["node_id"])


def downgrade() -> None:
    op.drop_index("ix_probe_assignments_node_id", table_name="probe_assignments")
    op.drop_index("ix_probe_assignments_probe_id", table_name="probe_assignments")
    op.drop_table("probe_assignments")
