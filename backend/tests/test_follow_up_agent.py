from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from app.agents.follow_up_graph import route_follow_up
from app.main import app
from app.schemas.follow_up import FollowUpAnalysis
from app.schemas.paper import SemanticPaperSearchResponse
from app.schemas.research import (
    GeneratedResearchAnswer,
    ResearchSessionDetail,
    StoredResearchTurn,
    WebSearchResponse,
    WebSource,
)


client = TestClient(app)


def create_session(
    with_sources: bool = True,
) -> ResearchSessionDetail:
    created_at = datetime.now(timezone.utc)

    web_sources = []

    if with_sources:
        web_sources = [
            WebSource(
                title="Exercise and sleep",
                url="https://example.com/exercise-sleep",
                content=(
                    "Regular physical activity may improve "
                    "sleep quality."
                ),
                score=0.9,
            )
        ]

    first_turn = StoredResearchTurn(
        turn_id=uuid4(),
        turn_index=1,
        question=(
            "هل تساعد التمارين الرياضية "
            "في تحسين جودة النوم؟"
        ),
        detected_language="Arabic",
        language_code="ar",
        english_query=(
            "Effects of exercise on sleep quality"
        ),
        answer=(
            "قد تساعد التمارين الرياضية المنتظمة "
            "في تحسين جودة النوم [W1]."
        ),
        evidence=[],
        limitations=[],
        scientific_total=0,
        scientific_providers=[],
        papers=[],
        web_total=len(web_sources),
        web_sources=web_sources,
        used_existing_context=False,
        performed_search=True,
        errors=[],
        created_at=created_at,
    )

    return ResearchSessionDetail(
        research_id=uuid4(),
        initial_question=first_turn.question,
        detected_language="Arabic",
        language_code="ar",
        created_at=created_at,
        updated_at=created_at,
        total_turns=1,
        has_more_turns=False,
        next_before_turn_index=None,
        turns=[first_turn],
    )


def create_analysis(
    needs_search: bool,
) -> FollowUpAnalysis:
    return FollowUpAnalysis(
        detected_language="Arabic",
        language_code="ar",
        english_query=(
            "How much exercise may improve sleep quality?"
        ),
        needs_search=needs_search,
        decision_reason=(
            "The saved context was evaluated."
        ),
    )


def test_follow_up_routes_to_memory_when_sources_are_sufficient(
) -> None:
    state = {
        "session": create_session(with_sources=True),
        "analysis": create_analysis(
            needs_search=False
        ),
    }

    assert route_follow_up(state) == "memory"


def test_follow_up_routes_to_search_when_analysis_requires_it(
) -> None:
    state = {
        "session": create_session(with_sources=True),
        "analysis": create_analysis(
            needs_search=True
        ),
    }

    assert route_follow_up(state) == "search"


def test_follow_up_routes_to_search_when_memory_has_no_sources(
) -> None:
    state = {
        "session": create_session(with_sources=False),
        "analysis": create_analysis(
            needs_search=False
        ),
    }

    assert route_follow_up(state) == "search"


def test_follow_up_endpoint_appends_second_turn(
    monkeypatch,
    override_research_repository,
) -> None:
    session = create_session(with_sources=True)

    override_research_repository.sessions[
        session.research_id
    ] = session

    async def fake_run_follow_up_agent(
        question,
        session,
        limit,
    ):
        assert question == (
            "وما المدة المناسبة يوميًا؟"
        )
        assert limit == 3
        assert len(session.turns) == 1

        return {
            "question": question,
            "limit": limit,
            "session": session,
            "analysis": create_analysis(
                needs_search=False
            ),
            "scientific_result": (
                SemanticPaperSearchResponse(
                    query=(
                        "How much exercise may improve "
                        "sleep quality?"
                    ),
                    total=0,
                    returned=0,
                    providers=[],
                    papers=[],
                )
            ),
            "web_result": WebSearchResponse(
                query=(
                    "How much exercise may improve "
                    "sleep quality?"
                ),
                total=1,
                results=session.turns[0].web_sources,
            ),
            "generated_answer": (
                GeneratedResearchAnswer(
                    answer=(
                        "يمكن الاستفادة من النشاط البدني "
                        "المنتظم، لكن المدة الدقيقة تعتمد "
                        "على الأدلة المتاحة [W1]."
                    ),
                    evidence=[],
                    limitations=[],
                )
            ),
            "used_existing_context": True,
            "performed_search": False,
            "errors": [],
        }

    monkeypatch.setattr(
        "app.api.routes.research.run_follow_up_agent",
        fake_run_follow_up_agent,
    )

    response = client.post(
        (
            f"/api/v1/research/"
            f"{session.research_id}/follow-up"
        ),
        json={
            "question": (
                "وما المدة المناسبة يوميًا؟"
            ),
            "limit": 3,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["research_id"] == str(
        session.research_id
    )
    assert body["turn_index"] == 2
    assert body["used_existing_context"] is True
    assert body["performed_search"] is False

    saved_session = (
        override_research_repository.sessions[
            session.research_id
        ]
    )

    assert saved_session.total_turns == 2
    assert len(saved_session.turns) == 2
    assert saved_session.turns[1].turn_index == 2
    assert saved_session.turns[1].question == (
        "وما المدة المناسبة يوميًا؟"
    )


def test_follow_up_for_unknown_session_returns_404(
    override_research_repository,
) -> None:
    missing_id = uuid4()

    response = client.post(
        f"/api/v1/research/{missing_id}/follow-up",
        json={
            "question": "What about the limitations?",
            "limit": 3,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Research session not found."
    )
