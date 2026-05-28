"""Add incidents table.

Revision ID: 0003
Revises: 0002
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "incidents",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(32), nullable=False, unique=True),
        sa.Column("title", sa.String(256), nullable=False),
        sa.Column("severity", sa.String(8), nullable=False, server_default="SEV3"),
        sa.Column("status", sa.String(16), nullable=False, server_default="open"),
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("postmortem_url", sa.String(512), nullable=False, server_default=""),
        sa.Column("description", sa.Text, nullable=False, server_default=""),
    )
    op.create_index("ix_incidents_code", "incidents", ["code"])


def downgrade() -> None:
    op.drop_index("ix_incidents_code", table_name="incidents")
    op.drop_table("incidents")
