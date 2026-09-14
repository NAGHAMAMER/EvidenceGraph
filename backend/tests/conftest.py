from datetime import datetime, timezone
from uuid import UUID

import pytest

from app.main import app
from app.schemas.research import (
    ResearchAgentResponse,
    ResearchHistoryResponse,
    ResearchSessionDetail,
    ResearchSessionSummary,
    StoredResearchTurn,
)
from app.services.research_repository import (
    ResearchNotFoundError,
    get_research_repository,
)


class FakeResearchRepository:
    def __init__(self) -> None:
        self.saved_results: list[
            ResearchAgentResponse
        ] = []

        self.sessions: dict[
            UUID,
            ResearchSessionDetail,
        ] = {}

        self.deleted_ids: list[UUID] = []

    async def create_session(
        self,
        result: ResearchAgentResponse,
    ) -> None:
        created_at = datetime.now(timezone.utc)

        self.saved_results.append(result)

        self.sessions[result.research_id] = (
            ResearchSessionDetail(
                research_id=result.research_id,
                initial_question=result.question,
                detected_language=(
                    result.detected_language
                ),
                language_code=result.language_code,
                created_at=created_at,
                updated_at=created_at,
                total_turns=1,
                has_more_turns=False,
                next_before_turn_index=None,
                turns=[
                    self._result_to_turn(
                        result=result,
                        created_at=created_at,
                    )
                ],
            )
        )

    async def append_turn(
        self,
        result: ResearchAgentResponse,
    ) -> ResearchAgentResponse:
        session = self.sessions.get(result.research_id)

        if session is None:
            raise ResearchNotFoundError(
                "Research session not found."
            )

        next_turn_index = (
            max(
                (
                    turn.turn_index
                    for turn in session.turns
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

        created_at = datetime.now(timezone.utc)

        new_turn = self._result_to_turn(
            result=saved_result,
            created_at=created_at,
        )

        self.sessions[result.research_id] = (
            session.model_copy(
                update={
                    "updated_at": created_at,
                    "total_turns": (
                        session.total_turns + 1
                    ),
                    "has_more_turns": False,
                    "next_before_turn_index": None,
                    "turns": [
                        *session.turns,
                        new_turn,
                    ],
                }
            )
        )

        self.saved_results.append(saved_result)

        return saved_result

    async def list_sessions(
        self,
        limit: int,
        offset: int,
    ) -> ResearchHistoryResponse:
        ordered_sessions = sorted(
            self.sessions.values(),
            key=lambda session: session.updated_at,
            reverse=True,
        )

        selected_sessions = ordered_sessions[
            offset:offset + limit
        ]

        return ResearchHistoryResponse(
            total=len(ordered_sessions),
            limit=limit,
            offset=offset,
            sessions=[
                ResearchSessionSummary(
                    research_id=session.research_id,
                    initial_question=(
                        session.initial_question
                    ),
                    detected_language=(
                        session.detected_language
                    ),
                    language_code=session.language_code,
                    turn_count=session.total_turns,
                    created_at=session.created_at,
                    updated_at=session.updated_at,
                )
                for session in selected_sessions
            ],
        )

    async def get_session(
        self,
        research_id: UUID,
        turn_limit: int | None = None,
        before_turn_index: int | None = None,
    ) -> ResearchSessionDetail:
        session = self.sessions.get(research_id)

        if session is None:
            raise ResearchNotFoundError(
                "Research session not found."
            )

        all_turns = sorted(
            session.turns,
            key=lambda turn: turn.turn_index,
        )

        eligible_turns = [
            turn
            for turn in all_turns
            if (
                before_turn_index is None
                or turn.turn_index < before_turn_index
            )
        ]

        if turn_limit is None:
            selected_turns = eligible_turns
        else:
            selected_turns = eligible_turns[
                -turn_limit:
            ]

        has_more_turns = False
        next_before_turn_index = None

        if selected_turns:
            oldest_loaded_index = (
                selected_turns[0].turn_index
            )

            has_more_turns = any(
                turn.turn_index < oldest_loaded_index
                for turn in all_turns
            )

            if has_more_turns:
                next_before_turn_index = (
                    oldest_loaded_index
                )

        return session.model_copy(
            update={
                "total_turns": len(all_turns),
                "has_more_turns": has_more_turns,
                "next_before_turn_index": (
                    next_before_turn_index
                ),
                "turns": selected_turns,
            }
        )

    async def delete_session(
        self,
        research_id: UUID,
    ) -> None:
        if research_id not in self.sessions:
            raise ResearchNotFoundError(
                "Research session not found."
            )

        self.sessions.pop(research_id)
        self.deleted_ids.append(research_id)

    @staticmethod
    def _result_to_turn(
        result: ResearchAgentResponse,
        created_at: datetime,
    ) -> StoredResearchTurn:
        return StoredResearchTurn(
            turn_id=result.turn_id,
            turn_index=result.turn_index,
            question=result.question,
            detected_language=result.detected_language,
            language_code=result.language_code,
            english_query=result.english_query,
            answer=result.answer,
            evidence=result.evidence,
            limitations=result.limitations,
            scientific_total=result.scientific_total,
            scientific_providers=(
                result.scientific_providers
            ),
            papers=result.papers,
            web_total=result.web_total,
            web_sources=result.web_sources,
            used_existing_context=(
                result.used_existing_context
            ),
            performed_search=result.performed_search,
            errors=result.errors,
            created_at=created_at,
        )


@pytest.fixture(autouse=True)
def override_research_repository():
    repository = FakeResearchRepository()

    app.dependency_overrides[
        get_research_repository
    ] = lambda: repository

    yield repository

    app.dependency_overrides.pop(
        get_research_repository,
        None,
    )
