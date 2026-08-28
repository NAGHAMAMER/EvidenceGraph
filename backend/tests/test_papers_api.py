from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.api.routes.papers import (
    get_paper_search_service,
)
from app.main import app
from app.schemas.paper import (
    Paper,
    PaperSearchResponse,
)


class FakePaperSearchService:
    async def search(
        self,
        query: str,
        limit: int = 10,
    ) -> PaperSearchResponse:
        paper = Paper(
            id="10.1234/api.test",
            doi="10.1234/api.test",
            title="API Test Scientific Paper",
            abstract="A paper returned by the fake service.",
            publication_year=2026,
            citation_count=5,
            providers=["openalex", "crossref"],
        )

        return PaperSearchResponse(
            query=query,
            total=1,
            returned=1,
            providers=["openalex", "crossref"],
            papers=[paper],
        )


@pytest.fixture
def client() -> Iterator[TestClient]:
    app.dependency_overrides[
        get_paper_search_service
    ] = lambda: FakePaperSearchService()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_search_papers_endpoint(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/papers/search",
        params={
            "query": "evidence extraction",
            "limit": 5,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["query"] == "evidence extraction"
    assert data["total"] == 1
    assert data["returned"] == 1
    assert data["providers"] == [
        "openalex",
        "crossref",
    ]
    assert len(data["papers"]) == 1

    paper = data["papers"][0]

    assert paper["doi"] == "10.1234/api.test"
    assert paper["title"] == "API Test Scientific Paper"
    assert paper["citation_count"] == 5


def test_search_papers_endpoint_validates_input(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/papers/search",
        params={
            "query": "a",
            "limit": 0,
        },
    )

    assert response.status_code == 422
