from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.research import (
    ResearchSessionDetail,
    StoredResearchTurn,
)


client = TestClient(app)


def create_stored_turn(
    turn_index: int,
    created_at: datetime,
) -> StoredResearchTurn:
    return StoredResearchTurn(
        turn_id=uuid4(),
        turn_index=turn_index,
        question=(
            f"Research question number {turn_index}"
        ),
        detected_language="English",
        language_code="en",
        english_query=(
            f"Optimized research query {turn_index}"
        ),
        answer=(
            f"Research answer number {turn_index}."
        ),
        evidence=[],
        limitations=[],
        scientific_total=0,
        scientific_providers=[],
        papers=[],
        web_total=0,
        web_sources=[],
        used_existing_context=turn_index > 1,
        performed_search=turn_index == 1,
        errors=[],
        created_at=created_at,
    )


def create_session_detail(
    research_id: UUID | None = None,
    turn_count: int = 1,
) -> ResearchSessionDetail:
    session_id = research_id or uuid4()
    created_at = datetime.now(timezone.utc)

    turns = [
        create_stored_turn(
            turn_index=turn_index,
            created_at=created_at,
        )
        for turn_index in range(
            1,
            turn_count + 1,
        )
    ]

    return ResearchSessionDetail(
        research_id=session_id,
        initial_question=turns[0].question,
        detected_language=turns[0].detected_language,
        language_code=turns[0].language_code,
        created_at=created_at,
        updated_at=created_at,
        total_turns=len(turns),
        has_more_turns=False,
        next_before_turn_index=None,
        turns=turns,
    )


def test_research_history_is_empty(
    override_research_repository,
) -> None:
    response = client.get(
        "/api/v1/research/history"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 0
    assert body["limit"] == 20
    assert body["offset"] == 0
    assert body["sessions"] == []


def test_research_history_returns_saved_sessions(
    override_research_repository,
) -> None:
    session = create_session_detail(
        turn_count=3,
    )

    override_research_repository.sessions[
        session.research_id
    ] = session

    response = client.get(
        "/api/v1/research/history",
        params={
            "limit": 10,
            "offset": 0,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 1
    assert body["limit"] == 10
    assert body["offset"] == 0

    assert len(body["sessions"]) == 1

    saved_session = body["sessions"][0]

    assert saved_session["research_id"] == str(
        session.research_id
    )
    assert saved_session["initial_question"] == (
        session.initial_question
    )
    assert saved_session["turn_count"] == 3


def test_get_research_session(
    override_research_repository,
) -> None:
    session = create_session_detail()

    override_research_repository.sessions[
        session.research_id
    ] = session

    response = client.get(
        f"/api/v1/research/{session.research_id}"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["research_id"] == str(
        session.research_id
    )
    assert body["initial_question"] == (
        session.initial_question
    )
    assert body["total_turns"] == 1
    assert body["has_more_turns"] is False
    assert body["next_before_turn_index"] is None

    assert len(body["turns"]) == 1
    assert body["turns"][0]["turn_index"] == 1
    assert body["turns"][0]["performed_search"] is True


def test_session_returns_latest_turn_by_default(
    override_research_repository,
) -> None:
    session = create_session_detail(
        turn_count=4,
    )

    override_research_repository.sessions[
        session.research_id
    ] = session

    response = client.get(
        f"/api/v1/research/{session.research_id}"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["total_turns"] == 4
    assert body["has_more_turns"] is True
    assert body["next_before_turn_index"] == 4

    assert len(body["turns"]) == 1
    assert body["turns"][0]["turn_index"] == 4
    assert body["turns"][0]["question"] == (
        "Research question number 4"
    )


def test_session_loads_previous_turns(
    override_research_repository,
) -> None:
    session = create_session_detail(
        turn_count=4,
    )

    override_research_repository.sessions[
        session.research_id
    ] = session

    response = client.get(
        f"/api/v1/research/{session.research_id}",
        params={
            "turn_limit": 2,
            "before_turn_index": 4,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["total_turns"] == 4
    assert body["has_more_turns"] is True
    assert body["next_before_turn_index"] == 2

    assert [
        turn["turn_index"]
        for turn in body["turns"]
    ] == [2, 3]


def test_session_loads_oldest_remaining_turn(
    override_research_repository,
) -> None:
    session = create_session_detail(
        turn_count=4,
    )

    override_research_repository.sessions[
        session.research_id
    ] = session

    response = client.get(
        f"/api/v1/research/{session.research_id}",
        params={
            "turn_limit": 2,
            "before_turn_index": 2,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["total_turns"] == 4
    assert body["has_more_turns"] is False
    assert body["next_before_turn_index"] is None

    assert [
        turn["turn_index"]
        for turn in body["turns"]
    ] == [1]


def test_get_unknown_research_session_returns_404(
    override_research_repository,
) -> None:
    missing_id = uuid4()

    response = client.get(
        f"/api/v1/research/{missing_id}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Research session not found."
    )


def test_delete_research_session(
    override_research_repository,
) -> None:
    session = create_session_detail()

    override_research_repository.sessions[
        session.research_id
    ] = session

    response = client.delete(
        f"/api/v1/research/{session.research_id}"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["research_id"] == str(
        session.research_id
    )
    assert body["message"] == (
        "Research session deleted successfully."
    )

    assert session.research_id in (
        override_research_repository.deleted_ids
    )
    assert session.research_id not in (
        override_research_repository.sessions
    )


def test_delete_unknown_research_session_returns_404(
    override_research_repository,
) -> None:
    missing_id = uuid4()

    response = client.delete(
        f"/api/v1/research/{missing_id}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Research session not found."
    )


def test_research_history_validates_pagination() -> None:
    invalid_limit_response = client.get(
        "/api/v1/research/history",
        params={
            "limit": 0,
        },
    )

    invalid_offset_response = client.get(
        "/api/v1/research/history",
        params={
            "offset": -1,
        },
    )

    assert invalid_limit_response.status_code == 422
    assert invalid_offset_response.status_code == 422


def test_research_turn_pagination_is_validated() -> None:
    research_id = uuid4()

    invalid_limit_response = client.get(
        f"/api/v1/research/{research_id}",
        params={
            "turn_limit": 0,
        },
    )

    invalid_before_response = client.get(
        f"/api/v1/research/{research_id}",
        params={
            "before_turn_index": 0,
        },
    )

    assert invalid_limit_response.status_code == 422
    assert invalid_before_response.status_code == 422
