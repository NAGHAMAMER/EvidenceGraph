"""Create research sessions and turns tables.

Revision ID: 20260911_0001
Revises:
Create Date: 2026-09-11
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260911_0001"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "research_sessions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "initial_question",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "detected_language",
            sa.String(length=80),
            nullable=False,
        ),
        sa.Column(
            "language_code",
            sa.String(length=20),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "research_turns",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "research_session_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "turn_index",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "question",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "detected_language",
            sa.String(length=80),
            nullable=False,
        ),
        sa.Column(
            "language_code",
            sa.String(length=20),
            nullable=False,
        ),
        sa.Column(
            "english_query",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "answer",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "evidence",
            postgresql.JSONB(),
            nullable=False,
        ),
        sa.Column(
            "limitations",
            postgresql.JSONB(),
            nullable=False,
        ),
        sa.Column(
            "scientific_total",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "scientific_providers",
            postgresql.JSONB(),
            nullable=False,
        ),
        sa.Column(
            "papers",
            postgresql.JSONB(),
            nullable=False,
        ),
        sa.Column(
            "web_total",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "web_sources",
            postgresql.JSONB(),
            nullable=False,
        ),
        sa.Column(
            "errors",
            postgresql.JSONB(),
            nullable=False,
        ),
        sa.Column(
            "used_existing_context",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "performed_search",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["research_session_id"],
            ["research_sessions.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "research_session_id",
            "turn_index",
            name="uq_research_turn_session_index",
        ),
    )

    op.create_index(
        "ix_research_turns_research_session_id",
        "research_turns",
        ["research_session_id"],
        unique=False,
    )

    op.create_index(
        "ix_research_turns_session_created",
        "research_turns",
        [
            "research_session_id",
            "created_at",
        ],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_research_turns_session_created",
        table_name="research_turns",
    )

    op.drop_index(
        "ix_research_turns_research_session_id",
        table_name="research_turns",
    )

    op.drop_table("research_turns")
    op.drop_table("research_sessions")
