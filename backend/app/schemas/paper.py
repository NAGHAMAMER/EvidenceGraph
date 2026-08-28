from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


ProviderName = Literal["openalex", "crossref"]


class PaperAuthor(BaseModel):
    name: str = Field(min_length=1)
    orcid: str | None = None


class Paper(BaseModel):
    id: str = Field(min_length=1)
    doi: str | None = None
    title: str = Field(min_length=1)
    abstract: str | None = None

    authors: list[PaperAuthor] = Field(default_factory=list)

    publication_year: int | None = Field(
        default=None,
        ge=1000,
        le=2100,
    )
    publication_date: date | None = None

    venue: str | None = None
    url: str | None = None
    pdf_url: str | None = None

    citation_count: int = Field(default=0, ge=0)
    is_open_access: bool | None = None

    topics: list[str] = Field(default_factory=list)
    providers: list[ProviderName] = Field(default_factory=list)


class PaperSearchResponse(BaseModel):
    query: str = Field(min_length=1)
    total: int = Field(ge=0)
    returned: int = Field(ge=0)

    providers: list[ProviderName] = Field(default_factory=list)
    papers: list[Paper] = Field(default_factory=list)
