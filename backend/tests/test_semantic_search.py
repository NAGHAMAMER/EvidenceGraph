import asyncio

from app.schemas.paper import (
    Paper,
    PaperSearchResponse,
    RankedPaper,
)
from app.services.semantic_search import SemanticSearchService


def create_paper(
    paper_id: str,
    title: str,
) -> Paper:
    return Paper(
        id=paper_id,
        doi=None,
        title=title,
        abstract=None,
        authors=[],
        publication_year=2024,
        publication_date=None,
        venue=None,
        url=None,
        pdf_url=None,
        citation_count=0,
        is_open_access=False,
        topics=[],
        providers=["openalex"],
    )


class FakePaperSearchService:
    def __init__(self) -> None:
        self.received_query: str | None = None
        self.received_limit: int | None = None

    async def search(
        self,
        query: str,
        limit: int,
    ) -> PaperSearchResponse:
        self.received_query = query
        self.received_limit = limit

        papers = [
            create_paper("paper-1", "First paper"),
            create_paper("paper-2", "Second paper"),
            create_paper("paper-3", "Third paper"),
        ]

        return PaperSearchResponse(
            query=query,
            total=3,
            returned=3,
            providers=["openalex", "crossref"],
            papers=papers,
        )


class FakeSemanticRankingService:
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

        return [
            RankedPaper(
                **paper.model_dump(),
                semantic_score=1.0 - (index * 0.1),
            )
            for index, paper in enumerate(papers[:limit])
        ]


def create_service() -> tuple[
    SemanticSearchService,
    FakePaperSearchService,
    FakeSemanticRankingService,
]:
    paper_service = FakePaperSearchService()
    ranking_service = FakeSemanticRankingService()

    service = SemanticSearchService(
        paper_search_service=paper_service,  # type: ignore[arg-type]
        semantic_ranking_service=ranking_service,  # type: ignore[arg-type]
    )

    return service, paper_service, ranking_service


def test_semantic_search_fetches_extra_candidates() -> None:
    service, paper_service, ranking_service = create_service()

    result = asyncio.run(
        service.search(
            query="semantic search",
            limit=2,
        )
    )

    assert paper_service.received_query == "semantic search"
    assert paper_service.received_limit == 6

    assert ranking_service.received_query == "semantic search"
    assert ranking_service.received_limit == 2

    assert result.total == 3
    assert result.returned == 2
    assert result.providers == ["openalex", "crossref"]
    assert len(result.papers) == 2


def test_semantic_search_caps_candidates_at_fifty() -> None:
    service, paper_service, ranking_service = create_service()

    result = asyncio.run(
        service.search(
            query="machine learning",
            limit=20,
        )
    )

    assert paper_service.received_limit == 50
    assert ranking_service.received_limit == 20
    assert result.returned == 3
