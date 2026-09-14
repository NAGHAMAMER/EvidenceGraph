import logging
from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import delete, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_database_session
from app.models.research import ResearchSession, ResearchTurn
from app.schemas.paper import RankedPaper
from app.schemas.research import (
    EvidenceClaim,
    ResearchAgentResponse,
    ResearchHistoryResponse,
    ResearchSessionDetail,
    ResearchSessionSummary,
    StoredResearchTurn,
    WebSource,
)
from app.services.client_identity import get_client_id


logger = logging.getLogger(__name__)


class ResearchPersistenceError(RuntimeError):
    """Raised when research data cannot be persisted or loaded."""


class ResearchNotFoundError(RuntimeError):
    """Raised when a requested research session does not exist."""


class ResearchRepository:
    def __init__(
        self,
        database_session: AsyncSession,
        client_id: str,
    ) -> None:
        self.database_session = database_session
        self.client_id = client_id

    async def create_session(
        self,
        result: ResearchAgentResponse,
    ) -> None:
        research_session = ResearchSession(
            id=result.research_id,
            client_id=self.client_id,
            initial_question=result.question,
            detected_language=result.detected_language,
            language_code=result.language_code,
        )

        first_turn = self._result_to_turn(result)

        research_session.turns.append(first_turn)
        self.database_session.add(research_session)

        try:
            await self.database_session.commit()

        except SQLAlchemyError as error:
            await self.database_session.rollback()

            logger.exception(
                "Failed to persist research session."
            )

            raise ResearchPersistenceError(
                "The research result could not be saved."
            ) from error

    async def append_turn(
        self,
        result: ResearchAgentResponse,
    ) -> ResearchAgentResponse:
        try:
            session_result = (
                await self.database_session.execute(
                    select(ResearchSession)
                    .options(
                        selectinload(
                            ResearchSession.turns
                        )
                    )
                    .where(
                        ResearchSession.id
                        == result.research_id,
                        ResearchSession.client_id
                        == self.client_id,
                    )
                    .with_for_update()
                )
            )

            research_session = (
                session_result
                .scalars()
                .unique()
                .one_or_none()
            )

            if research_session is None:
                await self.database_session.rollback()

                raise ResearchNotFoundError(
                    "Research session not found."
                )

            next_turn_index = (
                max(
                    (
                        turn.turn_index
                        for turn in research_session.turns
                    ),
                    default=0,
                )
                + 1
            )

            saved_result = result.model_copy(
                update={
                    "turn_index": next_turn_index,
                }
            )

            research_turn = self._result_to_turn(
                saved_result
            )

            research_session.turns.append(research_turn)
            research_session.updated_at = datetime.now(
                timezone.utc
            )

            await self.database_session.commit()

            return saved_result

        except ResearchNotFoundError:
            raise

        except SQLAlchemyError as error:
            await self.database_session.rollback()

            logger.exception(
                "Failed to persist follow-up turn."
            )

            raise ResearchPersistenceError(
                "The follow-up result could not be saved."
            ) from error

    async def list_sessions(
        self,
        limit: int,
        offset: int,
    ) -> ResearchHistoryResponse:
        if limit < 1:
            raise ValueError("Limit must be at least 1.")

        if offset < 0:
            raise ValueError("Offset cannot be negative.")

        try:
            total_result = await self.database_session.execute(
                select(func.count())
                .select_from(ResearchSession)
                .where(
                    ResearchSession.client_id
                    == self.client_id
                )
            )
            total = total_result.scalar_one()

            sessions_result = (
                await self.database_session.execute(
                    select(ResearchSession)
                    .options(
                        selectinload(
                            ResearchSession.turns
                        )
                    )
                    .where(
                        ResearchSession.client_id
                        == self.client_id
                    )
                    .order_by(
                        ResearchSession.updated_at.desc()
                    )
                    .offset(offset)
                    .limit(limit)
                )
            )

            sessions = (
                sessions_result
                .scalars()
                .unique()
                .all()
            )

            return ResearchHistoryResponse(
                total=total,
                limit=limit,
                offset=offset,
                sessions=[
                    ResearchSessionSummary(
                        research_id=session.id,
                        initial_question=(
                            session.initial_question
                        ),
                        detected_language=(
                            session.detected_language
                        ),
                        language_code=session.language_code,
                        turn_count=len(session.turns),
                        created_at=session.created_at,
                        updated_at=session.updated_at,
                    )
                    for session in sessions
                ],
            )

        except SQLAlchemyError as error:
            logger.exception(
                "Failed to load research history."
            )

            raise ResearchPersistenceError(
                "The research history could not be loaded."
            ) from error

    async def get_session(
        self,
        research_id: UUID,
        turn_limit: int | None = None,
        before_turn_index: int | None = None,
    ) -> ResearchSessionDetail:
        if turn_limit is not None and turn_limit < 1:
            raise ValueError(
                "Turn limit must be at least 1."
            )

        if (
            before_turn_index is not None
            and before_turn_index < 1
        ):
            raise ValueError(
                "Before turn index must be at least 1."
            )

        try:
            session_result = (
                await self.database_session.execute(
                    select(ResearchSession)
                    .where(
                        ResearchSession.id == research_id,
                        ResearchSession.client_id
                        == self.client_id,
                    )
                )
            )

            research_session = (
                session_result
                .scalars()
                .one_or_none()
            )

            if research_session is None:
                raise ResearchNotFoundError(
                    "Research session not found."
                )

            total_result = await self.database_session.execute(
                select(func.count())
                .select_from(ResearchTurn)
                .where(
                    ResearchTurn.research_session_id
                    == research_id
                )
            )
            total_turns = total_result.scalar_one()

            turns_query = (
                select(ResearchTurn)
                .where(
                    ResearchTurn.research_session_id
                    == research_id
                )
                .order_by(
                    ResearchTurn.turn_index.desc()
                )
            )

            if before_turn_index is not None:
                turns_query = turns_query.where(
                    ResearchTurn.turn_index
                    < before_turn_index
                )

            if turn_limit is not None:
                turns_query = turns_query.limit(turn_limit)

            turns_result = (
                await self.database_session.execute(
                    turns_query
                )
            )

            descending_turns = (
                turns_result
                .scalars()
                .all()
            )

            ordered_turns = list(
                reversed(descending_turns)
            )

            has_more_turns = False
            next_before_turn_index = None

            if ordered_turns:
                oldest_loaded_turn_index = (
                    ordered_turns[0].turn_index
                )

                older_turns_result = (
                    await self.database_session.execute(
                        select(func.count())
                        .select_from(ResearchTurn)
                        .where(
                            ResearchTurn.research_session_id
                            == research_id,
                            ResearchTurn.turn_index
                            < oldest_loaded_turn_index,
                        )
                    )
                )

                has_more_turns = (
                    older_turns_result.scalar_one() > 0
                )

                if has_more_turns:
                    next_before_turn_index = (
                        oldest_loaded_turn_index
                    )

            return ResearchSessionDetail(
                research_id=research_session.id,
                initial_question=(
                    research_session.initial_question
                ),
                detected_language=(
                    research_session.detected_language
                ),
                language_code=(
                    research_session.language_code
                ),
                created_at=research_session.created_at,
                updated_at=research_session.updated_at,
                total_turns=total_turns,
                has_more_turns=has_more_turns,
                next_before_turn_index=(
                    next_before_turn_index
                ),
                turns=[
                    self._turn_to_schema(turn)
                    for turn in ordered_turns
                ],
            )

        except ResearchNotFoundError:
            raise

        except SQLAlchemyError as error:
            logger.exception(
                "Failed to load research session %s.",
                research_id,
            )

            raise ResearchPersistenceError(
                "The research session could not be loaded."
            ) from error

    async def delete_session(
        self,
        research_id: UUID,
    ) -> None:
        try:
            delete_result = (
                await self.database_session.execute(
                    delete(ResearchSession)
                    .where(
                        ResearchSession.id == research_id,
                        ResearchSession.client_id
                        == self.client_id,
                    )
                    .returning(ResearchSession.id)
                )
            )

            deleted_id = delete_result.scalar_one_or_none()

            if deleted_id is None:
                await self.database_session.rollback()

                raise ResearchNotFoundError(
                    "Research session not found."
                )

            await self.database_session.commit()

        except ResearchNotFoundError:
            raise

        except SQLAlchemyError as error:
            await self.database_session.rollback()

            logger.exception(
                "Failed to delete research session %s.",
                research_id,
            )

            raise ResearchPersistenceError(
                "The research session could not be deleted."
            ) from error

    @staticmethod
    def _result_to_turn(
        result: ResearchAgentResponse,
    ) -> ResearchTurn:
        return ResearchTurn(
            id=result.turn_id,
            research_session_id=result.research_id,
            turn_index=result.turn_index,
            question=result.question,
            detected_language=result.detected_language,
            language_code=result.language_code,
            english_query=result.english_query,
            answer=result.answer,
            evidence=[
                claim.model_dump(mode="json")
                for claim in result.evidence
            ],
            limitations=list(result.limitations),
            scientific_total=result.scientific_total,
            scientific_providers=list(
                result.scientific_providers
            ),
            papers=[
                paper.model_dump(mode="json")
                for paper in result.papers
            ],
            web_total=result.web_total,
            web_sources=[
                source.model_dump(mode="json")
                for source in result.web_sources
            ],
            errors=list(result.errors),
            used_existing_context=(
                result.used_existing_context
            ),
            performed_search=result.performed_search,
        )

    @staticmethod
    def _turn_to_schema(
        turn: ResearchTurn,
    ) -> StoredResearchTurn:
        return StoredResearchTurn(
            turn_id=turn.id,
            turn_index=turn.turn_index,
            question=turn.question,
            detected_language=turn.detected_language,
            language_code=turn.language_code,
            english_query=turn.english_query,
            answer=turn.answer,
            evidence=[
                EvidenceClaim.model_validate(claim)
                for claim in (turn.evidence or [])
            ],
            limitations=list(turn.limitations or []),
            scientific_total=turn.scientific_total,
            scientific_providers=list(
                turn.scientific_providers or []
            ),
            papers=[
                RankedPaper.model_validate(paper)
                for paper in (turn.papers or [])
            ],
            web_total=turn.web_total,
            web_sources=[
                WebSource.model_validate(source)
                for source in (turn.web_sources or [])
            ],
            used_existing_context=(
                turn.used_existing_context
            ),
            performed_search=turn.performed_search,
            errors=list(turn.errors or []),
            created_at=turn.created_at,
        )


def get_research_repository(
    database_session: Annotated[
        AsyncSession,
        Depends(get_database_session),
    ],
    client_id: Annotated[
        str,
        Depends(get_client_id),
    ],
) -> ResearchRepository:
    return ResearchRepository(
        database_session=database_session,
        client_id=client_id,
    )
