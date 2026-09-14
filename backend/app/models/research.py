from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ResearchSession(Base):
    __tablename__ = "research_sessions"

    __table_args__ = (
        Index(
            "ix_research_sessions_client_updated",
            "client_id",
            "updated_at",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    client_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    initial_question: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    detected_language: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    language_code: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    turns: Mapped[list["ResearchTurn"]] = relationship(
        back_populates="research_session",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="ResearchTurn.turn_index",
        lazy="selectin",
    )


class ResearchTurn(Base):
    __tablename__ = "research_turns"

    __table_args__ = (
        UniqueConstraint(
            "research_session_id",
            "turn_index",
            name="uq_research_turn_session_index",
        ),
        Index(
            "ix_research_turns_session_created",
            "research_session_id",
            "created_at",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    research_session_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "research_sessions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    turn_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    question: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    detected_language: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    language_code: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    english_query: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    answer: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    evidence: Mapped[list[dict[str, object]]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    limitations: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    scientific_total: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    scientific_providers: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    papers: Mapped[list[dict[str, object]]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    web_total: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    web_sources: Mapped[list[dict[str, object]]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    errors: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    used_existing_context: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    performed_search: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    research_session: Mapped[ResearchSession] = relationship(
        back_populates="turns",
    )