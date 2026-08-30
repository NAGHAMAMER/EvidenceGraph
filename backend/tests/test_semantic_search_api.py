from fastapi.testclient import TestClient

from app.main import app
from app.schemas.paper import (
    RankedPaper,
    SemanticPaperSearchResponse,
)
from app.services.semantic_search import (
    get_semantic_search_service,
)


client = TestClient(app)


class FakeSemanticSearchService:
    def __init__(self) -> None:
        self.received_query: str | None = None
        self.received_limit: int | None = None

    async def search(
        self,
        query: str,
        limit: int,
    ) -> SemanticPaperSearchResponse:
        self.received_query = query
        self.received_limit = limit

        paper = RankedPaper(
            id="paper-1",
            doi="10.1000/semantic-paper",
            title="Semantic Search for Scientific Literature",
            abstract="A paper about semantic scientific search.",
            authors=[],
            publication_year=2024,
            publication_date=None,
            venue="Test Journal",
            url=None,
            pdf_url=None,
            citation_count=10,
            is_open_access=True,
            topics=["semantic search"],
            providers=["openalex"],
            semantic_score=0.91,
        )

        return SemanticPaperSearchResponse(
            query=query,
            total=1,
            returned=1,
            providers=["openalex"],
            papers=[paper],
        )


def test_semantic_search_endpoint() -> None:
    fake_service = FakeSemanticSearchService()

    app.dependency_overrides[
        get_semantic_search_service
    ] = lambda: fake_service

    try:
        response = client.get(
            "/api/v1/papers/semantic-search",
            params={
                "query": "semantic search",
                "limit": 4,
            },
        )
    finally:
        app.dependency_overrides.pop(
            get_semantic_search_service,
            None,
        )

    assert response.status_code == 200

    body = response.json()

    assert fake_service.received_query == "semantic search"
    assert fake_service.received_limit == 4
    assert body["returned"] == 1
    assert body["papers"][0]["semantic_score"] == 0.91


def test_semantic_search_endpoint_validates_input() -> None:
    response = client.get(
        "/api/v1/papers/semantic-search",
        params={
            "query": "a",
            "limit": 21,
        },
    )

    assert response.status_code == 422
