"""Add anonymous client identity to research sessions.

Revision ID: 20260912_0002
Revises: 20260911_0001
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "20260912_0002"
down_revision: str | None = "20260911_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "research_sessions",
        sa.Column(
            "client_id",
            sa.String(length=64),
            nullable=True,
        ),
    )

    op.execute(
        sa.text(
            """
            UPDATE research_sessions
            SET client_id = 'legacy-' || id::text
            WHERE client_id IS NULL
            """
        )
    )

    op.alter_column(
        "research_sessions",
        "client_id",
        existing_type=sa.String(length=64),
        nullable=False,
    )

    op.create_index(
        "ix_research_sessions_client_updated",
        "research_sessions",
        [
            "client_id",
            "updated_at",
        ],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_research_sessions_client_updated",
        table_name="research_sessions",
    )

    op.drop_column(
        "research_sessions",
        "client_id",
    )
