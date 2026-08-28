from datetime import date

import pytest
from pydantic import ValidationError

from app.schemas.paper import Paper, PaperAuthor, PaperSearchResponse


def test_paper_schema_accepts_valid_data() -> None:
    paper = Paper(
        id="https://openalex.org/W123456789",
        doi="10.1234/evidencegraph",
        title="Evidence extraction from scientific literature",
        abstract="An example scientific paper abstract.",
        authors=[
            PaperAuthor(
                name="Jane Doe",
                orcid="https://orcid.org/0000-0000-0000-0000",
            )
        ],
        publication_year=2026,
        publication_date=date(2026, 8, 27),
        venue="Example Journal",
        citation_count=12,
        is_open_access=True,
        topics=["Natural Language Processing", "Scientific Literature"],
        providers=["openalex"],
    )

    response = PaperSearchResponse(
        query="evidence extraction",
        total=1,
        returned=1,
        providers=["openalex"],
        papers=[paper],
    )

    assert response.returned == 1
    assert response.papers[0].title == paper.title
    assert response.papers[0].authors[0].name == "Jane Doe"
    assert response.papers[0].publication_date == date(2026, 8, 27)


def test_paper_schema_rejects_invalid_data() -> None:
    with pytest.raises(ValidationError) as error:
        Paper(
            id="",
            title="",
            citation_count=-1,
            providers=["unknown"],
        )

    error_locations = {
        tuple(item["loc"])
        for item in error.value.errors()
    }

    assert ("id",) in error_locations
    assert ("title",) in error_locations
    assert ("citation_count",) in error_locations
    assert ("providers", 0) in error_locations
