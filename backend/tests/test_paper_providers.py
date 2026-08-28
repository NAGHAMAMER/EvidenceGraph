import asyncio

import httpx

from app.services.providers.crossref import CrossrefProvider
from app.services.providers.openalex import OpenAlexProvider


def test_openalex_provider_maps_paper() -> None:
    def handle_request(
        request: httpx.Request,
    ) -> httpx.Response:
        assert request.url.path == "/works"
        assert request.url.params["search"] == "evidence extraction"
        assert request.url.params["per_page"] == "5"

        return httpx.Response(
            status_code=200,
            json={
                "results": [
                    {
                        "id": "https://openalex.org/W123456",
                        "doi": "https://doi.org/10.1234/openalex.paper",
                        "display_name": "OpenAlex Research Paper",
                        "publication_year": 2026,
                        "publication_date": "2026-08-27",
                        "authorships": [
                            {
                                "author": {
                                    "display_name": "Jane Doe",
                                    "orcid": (
                                        "https://orcid.org/"
                                        "0000-0000-0000-0001"
                                    ),
                                }
                            }
                        ],
                        "abstract_inverted_index": {
                            "Evidence": [0],
                            "supports": [1],
                            "research": [2],
                        },
                        "primary_location": {
                            "landing_page_url": (
                                "https://example.org/openalex-paper"
                            ),
                            "pdf_url": None,
                            "source": {
                                "display_name": "OpenAlex Journal"
                            },
                        },
                        "best_oa_location": {
                            "pdf_url": (
                                "https://example.org/openalex-paper.pdf"
                            )
                        },
                        "open_access": {
                            "is_oa": True,
                            "oa_url": (
                                "https://example.org/openalex-paper"
                            ),
                        },
                        "cited_by_count": 15,
                        "topics": [
                            {
                                "display_name": (
                                    "Natural Language Processing"
                                )
                            }
                        ],
                    }
                ]
            },
        )

    async def run_search():
        transport = httpx.MockTransport(handle_request)

        async with httpx.AsyncClient(
            transport=transport
        ) as client:
            provider = OpenAlexProvider(client=client)

            return await provider.search(
                query="evidence extraction",
                limit=5,
            )

    papers = asyncio.run(run_search())

    assert len(papers) == 1

    paper = papers[0]

    assert paper.id == "10.1234/openalex.paper"
    assert paper.doi == "10.1234/openalex.paper"
    assert paper.title == "OpenAlex Research Paper"
    assert paper.abstract == "Evidence supports research"
    assert paper.authors[0].name == "Jane Doe"
    assert paper.publication_year == 2026
    assert paper.venue == "OpenAlex Journal"
    assert paper.citation_count == 15
    assert paper.is_open_access is True
    assert paper.providers == ["openalex"]


def test_crossref_provider_maps_paper() -> None:
    def handle_request(
        request: httpx.Request,
    ) -> httpx.Response:
        assert request.url.path == "/works"
        assert (
            request.url.params["query.bibliographic"]
            == "machine learning"
        )
        assert request.url.params["rows"] == "4"

        return httpx.Response(
            status_code=200,
            json={
                "message": {
                    "items": [
                        {
                            "DOI": "10.5678/Crossref.Paper",
                            "title": [
                                "Crossref Research Paper"
                            ],
                            "abstract": (
                                "<jats:p>"
                                "Crossref scientific abstract"
                                "</jats:p>"
                            ),
                            "author": [
                                {
                                    "given": "John",
                                    "family": "Smith",
                                    "ORCID": (
                                        "https://orcid.org/"
                                        "0000-0000-0000-0002"
                                    ),
                                }
                            ],
                            "published-online": {
                                "date-parts": [
                                    [2025, 4, 12]
                                ]
                            },
                            "container-title": [
                                "Crossref Journal"
                            ],
                            "URL": (
                                "https://doi.org/"
                                "10.5678/Crossref.Paper"
                            ),
                            "link": [
                                {
                                    "URL": (
                                        "https://example.org/"
                                        "crossref-paper.pdf"
                                    ),
                                    "content-type": (
                                        "application/pdf"
                                    ),
                                }
                            ],
                            "is-referenced-by-count": 8,
                            "subject": [
                                "Artificial Intelligence"
                            ],
                        }
                    ]
                }
            },
        )

    async def run_search():
        transport = httpx.MockTransport(handle_request)

        async with httpx.AsyncClient(
            transport=transport
        ) as client:
            provider = CrossrefProvider(client=client)

            return await provider.search(
                query="machine learning",
                limit=4,
            )

    papers = asyncio.run(run_search())

    assert len(papers) == 1

    paper = papers[0]

    assert paper.id == "10.5678/crossref.paper"
    assert paper.doi == "10.5678/crossref.paper"
    assert paper.title == "Crossref Research Paper"
    assert paper.abstract == "Crossref scientific abstract"
    assert paper.authors[0].name == "John Smith"
    assert paper.publication_year == 2025
    assert paper.publication_date.isoformat() == "2025-04-12"
    assert paper.venue == "Crossref Journal"
    assert paper.pdf_url.endswith(".pdf")
    assert paper.citation_count == 8
    assert paper.is_open_access is None
    assert paper.providers == ["crossref"]
