import asyncio

from app.schemas.paper import Paper, PaperAuthor, ProviderName
from app.services.paper_search import PaperSearchService
from app.services.providers.base import (
    PaperProvider,
    ProviderRequestError,
)


class FakeProvider(PaperProvider):
    def __init__(
        self,
        name: ProviderName,
        papers: list[Paper] | None = None,
        error: Exception | None = None,
    ) -> None:
        self.name = name
        self._papers = papers or []
        self._error = error

    async def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[Paper]:
        if self._error is not None:
            raise self._error

        return self._papers[:limit]


def test_search_service_merges_duplicate_papers() -> None:
    openalex_paper = Paper(
        id="https://openalex.org/W123",
        doi="10.1000/shared.paper",
        title="Shared Scientific Paper",
        abstract="Detailed abstract from OpenAlex.",
        publication_year=2026,
        citation_count=12,
        is_open_access=True,
        topics=["Natural Language Processing"],
        providers=["openalex"],
    )

    crossref_paper = Paper(
        id="10.1000/shared.paper",
        doi="10.1000/shared.paper",
        title="Shared Scientific Paper",
        authors=[
            PaperAuthor(name="Jane Doe")
        ],
        publication_year=2026,
        venue="Example Journal",
        pdf_url="https://example.org/paper.pdf",
        citation_count=8,
        topics=["Artificial Intelligence"],
        providers=["crossref"],
    )

    service = PaperSearchService(
        providers=[
            FakeProvider(
                name="openalex",
                papers=[openalex_paper],
            ),
            FakeProvider(
                name="crossref",
                papers=[crossref_paper],
            ),
        ]
    )

    response = asyncio.run(
        service.search(
            query="shared paper",
            limit=10,
        )
    )

    assert response.total == 1
    assert response.returned == 1
    assert response.providers == [
        "openalex",
        "crossref",
    ]

    paper = response.papers[0]

    assert paper.doi == "10.1000/shared.paper"
    assert paper.abstract == (
        "Detailed abstract from OpenAlex."
    )
    assert paper.authors[0].name == "Jane Doe"
    assert paper.venue == "Example Journal"
    assert paper.pdf_url == "https://example.org/paper.pdf"
    assert paper.citation_count == 12
    assert paper.is_open_access is True
    assert paper.topics == [
        "Natural Language Processing",
        "Artificial Intelligence",
    ]
    assert paper.providers == [
        "openalex",
        "crossref",
    ]


def test_search_service_survives_one_provider_failure() -> None:
    openalex_paper = Paper(
        id="10.2000/available.paper",
        doi="10.2000/available.paper",
        title="Available Scientific Paper",
        providers=["openalex"],
    )

    service = PaperSearchService(
        providers=[
            FakeProvider(
                name="openalex",
                papers=[openalex_paper],
            ),
            FakeProvider(
                name="crossref",
                error=ProviderRequestError(
                    provider="crossref",
                    message="Service unavailable",
                ),
            ),
        ]
    )

    response = asyncio.run(
        service.search(
            query="available paper",
            limit=10,
        )
    )

    assert response.total == 1
    assert response.returned == 1
    assert response.providers == ["openalex"]
    assert response.papers[0].title == (
        "Available Scientific Paper"
    )
