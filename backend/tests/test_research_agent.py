import asyncio

import pytest
from fastapi.testclient import TestClient

from app.agents import research_graph as graph_module
from app.agents.answer_generator import AnswerGenerator
from app.agents.question_analyzer import QuestionAnalyzer
from app.api.routes import research as research_route
from app.main import app
from app.schemas.paper import (
    Paper,
    PaperSearchResponse,
    RankedPaper,
    SemanticPaperSearchResponse,
)
from app.schemas.research import (
    GeneratedResearchAnswer,
    QuestionAnalysis,
    WebSearchResponse,
    WebSource,
)
from app.services.multilingual_scientific_search import (
    MultilingualScientificSearchService,
)
from app.services.paper_search import PaperSearchService
from app.services.web_search import (
    WebSearchError,
    WebSearchService,
)


class FakeRunnable:
    def __init__(
        self,
        response: dict,
        error: Exception | None = None,
    ) -> None:
        self.response = response
        self.error = error
        self.received_input = None

    async def ainvoke(self, received_input):
        self.received_input = received_input

        if self.error:
            raise self.error

        return self.response


def make_paper(
    provider: str = "openalex",
    paper_id: str = "paper-1",
) -> Paper:
    return Paper(
        id=paper_id,
        doi="10.1000/evidencegraph",
        title="Exercise and depression in adults",
        abstract=(
            "Regular physical activity may reduce symptoms "
            "of depression in adults."
        ),
        publication_year=2024,
        url="https://example.org/paper",
        citation_count=20,
        is_open_access=True,
        topics=["exercise", "depression"],
        providers=[provider],
    )


def make_scientific_result(
) -> SemanticPaperSearchResponse:
    paper = make_paper()

    ranked_paper = RankedPaper(
        **paper.model_dump(),
        semantic_score=0.91,
    )

    return SemanticPaperSearchResponse(
        query="هل تقلل الرياضة الاكتئاب؟",
        total=1,
        returned=1,
        providers=["openalex"],
        papers=[ranked_paper],
    )


def make_web_result() -> WebSearchResponse:
    return WebSearchResponse(
        query="exercise and depression in adults",
        total=1,
        results=[
            WebSource(
                title="Exercise and mental health",
                url="https://example.org/web",
                content=(
                    "Exercise can support mental health "
                    "and general well-being."
                ),
                score=0.88,
            )
        ],
    )


def make_generated_answer() -> GeneratedResearchAnswer:
    return GeneratedResearchAnswer.model_validate(
        {
            "answer": (
                "تشير الأدلة المتاحة إلى أن النشاط البدني "
                "قد يساعد في تقليل أعراض الاكتئاب [P1]."
            ),
            "evidence": [
                {
                    "claim": (
                        "قد يساعد النشاط البدني في تقليل "
                        "أعراض الاكتئاب."
                    ),
                    "stance": "supports",
                    "source_ids": ["P1", "W1"],
                }
            ],
            "limitations": [
                "تختلف النتائج بحسب نوع النشاط وحالة الشخص."
            ],
        }
    )


def test_question_analyzer_returns_structured_result() -> None:
    fake_model = FakeRunnable(
        {
            "detected_language": "Arabic",
            "language_code": "ar",
            "english_query": (
                "effects of regular exercise on depression "
                "in adults"
            ),
        }
    )

    analyzer = QuestionAnalyzer(
        structured_model=fake_model,
    )

    result = asyncio.run(
        analyzer.analyze(
            "هل تقلل ممارسة الرياضة الاكتئاب لدى البالغين؟"
        )
    )

    assert result.detected_language == "Arabic"
    assert result.language_code == "ar"
    assert "exercise" in result.english_query
    assert len(fake_model.received_input) == 2


def test_question_analyzer_rejects_empty_question() -> None:
    analyzer = QuestionAnalyzer(
        structured_model=FakeRunnable({}),
    )

    with pytest.raises(
        ValueError,
        match="Question cannot be empty",
    ):
        asyncio.run(analyzer.analyze("   "))


def test_web_search_normalizes_results() -> None:
    fake_tool = FakeRunnable(
        {
            "results": [
                {
                    "title": "WHO mental health",
                    "url": "https://example.org/valid",
                    "content": "Mental health information.",
                    "score": 0.95,
                },
                {
                    "title": "Missing URL",
                    "content": "This result must be ignored.",
                },
                "invalid result",
            ]
        }
    )

    service = WebSearchService(search_tool=fake_tool)

    result = asyncio.run(
        service.search("exercise and depression")
    )

    assert result.query == "exercise and depression"
    assert result.total == 1
    assert result.results[0].title == "WHO mental health"
    assert result.results[0].score == 0.95
    assert fake_tool.received_input == {
        "query": "exercise and depression"
    }


def test_web_search_rejects_empty_query() -> None:
    service = WebSearchService(
        search_tool=FakeRunnable({}),
    )

    with pytest.raises(
        ValueError,
        match="Web search query cannot be empty",
    ):
        asyncio.run(service.search("   "))


def test_web_search_converts_external_failure() -> None:
    service = WebSearchService(
        search_tool=FakeRunnable(
            {},
            error=RuntimeError("Tavily unavailable"),
        )
    )

    with pytest.raises(
        WebSearchError,
        match="General web search failed",
    ):
        asyncio.run(service.search("semantic search"))


def test_answer_generator_builds_source_context() -> None:
    context = AnswerGenerator.build_source_context(
        scientific_result=make_scientific_result(),
        web_result=make_web_result(),
    )

    assert "[P1] SCIENTIFIC PAPER" in context
    assert "[W1] GENERAL WEB SOURCE" in context
    assert "10.1000/evidencegraph" in context
    assert "https://example.org/web" in context


def test_answer_generator_removes_invalid_source_ids() -> None:
    fake_model = FakeRunnable(
        {
            "answer": "إجابة مدعومة بالمصادر [P1] و[W1].",
            "evidence": [
                {
                    "claim": "النشاط البدني مفيد.",
                    "stance": "supports",
                    "source_ids": [
                        "P1",
                        "W1",
                        "P999",
                        "W999",
                    ],
                }
            ],
            "limitations": ["الأدلة محدودة."],
        }
    )

    generator = AnswerGenerator(
        structured_model=fake_model,
    )

    result = asyncio.run(
        generator.generate(
            question="هل الرياضة مفيدة؟",
            detected_language="Arabic",
            language_code="ar",
            scientific_result=make_scientific_result(),
            web_result=make_web_result(),
        )
    )

    assert result.evidence[0].source_ids == ["P1", "W1"]

    human_prompt = fake_model.received_input[1].content

    assert "Required answer language: Arabic (ar)" in human_prompt
    assert "[P1]" in human_prompt
    assert "[W1]" in human_prompt


class FakePaperSearchService:
    def __init__(self) -> None:
        self.calls: list[tuple[str, int]] = []

    async def search(
        self,
        query: str,
        limit: int,
    ) -> PaperSearchResponse:
        self.calls.append((query, limit))

        provider = (
            "openalex"
            if any(ord(character) > 127 for character in query)
            else "crossref"
        )

        paper = make_paper(
            provider=provider,
            paper_id=f"{provider}-paper",
        )

        return PaperSearchResponse(
            query=query,
            total=1,
            returned=1,
            providers=[provider],
            papers=[paper],
        )

    @staticmethod
    def deduplicate_papers(
        papers: list[Paper],
    ) -> list[Paper]:
        return PaperSearchService.deduplicate_papers(
            papers
        )


class FakeRankingService:
    def __init__(self) -> None:
        self.received_query: str | None = None
        self.received_limit: int | None = None

    def rank(
        self,
        query: str,
        papers: list[Paper],
        limit: int,
    ) -> list[RankedPaper]:
        self.received_query = query
        self.received_limit = limit

        ranked = [
            RankedPaper(
                **paper.model_dump(),
                semantic_score=0.90,
            )
            for paper in papers
        ]

        return ranked[:limit]


def test_multilingual_search_uses_original_and_english() -> None:
    paper_service = FakePaperSearchService()
    ranking_service = FakeRankingService()

    service = MultilingualScientificSearchService(
        paper_search_service=paper_service,
        semantic_ranking_service=ranking_service,
    )

    result = asyncio.run(
        service.search(
            original_query="تأثير الرياضة على الاكتئاب",
            english_query=(
                "effects of exercise on depression"
            ),
            limit=2,
        )
    )

    assert len(paper_service.calls) == 2
    assert paper_service.calls[0][1] == 6
    assert paper_service.calls[1][1] == 6

    assert result.total == 1
    assert result.returned == 1
    assert result.providers == ["openalex", "crossref"]

    assert ranking_service.received_query == (
        "effects of exercise on depression"
    )
    assert ranking_service.received_limit == 2


def test_multilingual_search_avoids_duplicate_query() -> None:
    paper_service = FakePaperSearchService()
    ranking_service = FakeRankingService()

    service = MultilingualScientificSearchService(
        paper_search_service=paper_service,
        semantic_ranking_service=ranking_service,
    )

    asyncio.run(
        service.search(
            original_query="semantic search",
            english_query="semantic search",
            limit=1,
        )
    )

    assert len(paper_service.calls) == 1
    assert paper_service.calls[0] == (
        "semantic search",
        3,
    )


def test_research_graph_runs_all_nodes(
    monkeypatch,
) -> None:
    class FakeAnalyzer:
        async def analyze(self, question: str):
            return QuestionAnalysis(
                detected_language="Arabic",
                language_code="ar",
                english_query="exercise and depression",
            )

    class FakeScientificService:
        async def search(
            self,
            original_query: str,
            english_query: str,
            limit: int,
        ):
            return make_scientific_result()

    class FakeWebService:
        async def search(self, query: str):
            return make_web_result()

    class FakeAnswerService:
        async def generate(self, **kwargs):
            return make_generated_answer()

    monkeypatch.setattr(
        graph_module,
        "get_question_analyzer",
        lambda: FakeAnalyzer(),
    )
    monkeypatch.setattr(
        graph_module,
        "get_multilingual_scientific_search_service",
        lambda: FakeScientificService(),
    )
    monkeypatch.setattr(
        graph_module,
        "get_web_search_service",
        lambda: FakeWebService(),
    )
    monkeypatch.setattr(
        graph_module,
        "get_answer_generator",
        lambda: FakeAnswerService(),
    )

    graph = graph_module.build_research_graph()

    state = asyncio.run(
        graph.ainvoke(
            {
                "question": (
                    "هل تقلل الرياضة الاكتئاب؟"
                ),
                "limit": 2,
                "errors": [],
            }
        )
    )

    assert state["detected_language"] == "Arabic"
    assert state["english_query"] == (
        "exercise and depression"
    )
    assert state["scientific_result"].returned == 1
    assert state["web_result"].total == 1
    assert state["generated_answer"].evidence


def test_research_api_returns_agent_result(
    monkeypatch,
) -> None:
    async def fake_run_research_agent(
        question: str,
        limit: int,
    ):
        return {
            "question": question,
            "limit": limit,
            "detected_language": "Arabic",
            "language_code": "ar",
            "english_query": "exercise and depression",
            "scientific_result": (
                make_scientific_result()
            ),
            "web_result": make_web_result(),
            "generated_answer": (
                make_generated_answer()
            ),
            "errors": [],
        }

    monkeypatch.setattr(
        research_route,
        "run_research_agent",
        fake_run_research_agent,
    )

    client = TestClient(app)

    response = client.post(
        "/api/v1/research",
        json={
            "question": (
                "هل تقلل الرياضة الاكتئاب؟"
            ),
            "limit": 2,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["detected_language"] == "Arabic"
    assert data["scientific_total"] == 1
    assert data["web_total"] == 1
    assert len(data["papers"]) == 1
    assert len(data["web_sources"]) == 1


def test_research_api_validates_request() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/v1/research",
        json={
            "question": "",
            "limit": 2,
        },
    )

    assert response.status_code == 422


def test_research_api_returns_502_on_failure(
    monkeypatch,
) -> None:
    async def failing_agent(
        question: str,
        limit: int,
    ):
        raise RuntimeError("Unexpected agent failure")

    monkeypatch.setattr(
        research_route,
        "run_research_agent",
        failing_agent,
    )

    client = TestClient(app)

    response = client.post(
        "/api/v1/research",
        json={
            "question": "Does exercise reduce depression?",
            "limit": 2,
        },
    )

    assert response.status_code == 502
    assert response.json()["detail"] == (
        "The research agent could not complete the request."
    )
def test_research_api_returns_504_on_timeout(
    monkeypatch,
) -> None:
    async def timed_out_agent(
        question: str,
        limit: int,
    ):
        raise TimeoutError("Simulated upstream timeout")

    monkeypatch.setattr(
        research_route,
        "run_research_agent",
        timed_out_agent,
    )

    client = TestClient(app)

    response = client.post(
        "/api/v1/research",
        json={
            "question": "How does RAG affect hallucinations?",
            "limit": 2,
        },
    )

    assert response.status_code == 504
    assert response.json()["detail"] == (
        "An external research service timed out. "
        "Please try again later."
    )
