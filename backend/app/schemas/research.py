from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.paper import ProviderName, RankedPaper


class QuestionAnalysis(BaseModel):
    detected_language: str = Field(
        min_length=2,
        max_length=80,
        description="Human-readable name of the detected language.",
    )

    language_code: str = Field(
        min_length=2,
        max_length=20,
        description="ISO or BCP-47 code of the detected language.",
    )

    english_query: str = Field(
        min_length=2,
        max_length=500,
        description="English query optimized for scientific search.",
    )


class WebSource(BaseModel):
    source_type: Literal["web"] = "web"
    title: str = Field(min_length=1, max_length=500)
    url: str = Field(min_length=1, max_length=2000)
    content: str = Field(default="", max_length=5000)
    score: float | None = None


class WebSearchResponse(BaseModel):
    query: str
    total: int
    results: list[WebSource]


class EvidenceClaim(BaseModel):
    claim: str = Field(min_length=1, max_length=2000)

    stance: Literal[
        "supports",
        "contradicts",
        "mixed",
        "uncertain",
    ]

    source_ids: list[str] = Field(default_factory=list)


class GeneratedResearchAnswer(BaseModel):
    answer: str = Field(min_length=1, max_length=10000)
    evidence: list[EvidenceClaim] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class ResearchAgentRequest(BaseModel):
    question: str = Field(min_length=2, max_length=1000)
    limit: int = Field(default=5, ge=1, le=10)


class ResearchAgentResponse(BaseModel):
    research_id: UUID
    turn_id: UUID
    turn_index: int = Field(ge=1)

    question: str
    detected_language: str
    language_code: str
    english_query: str

    answer: str
    evidence: list[EvidenceClaim]
    limitations: list[str]

    scientific_total: int = Field(ge=0)
    scientific_providers: list[ProviderName]
    papers: list[RankedPaper]

    web_total: int = Field(ge=0)
    web_sources: list[WebSource]

    used_existing_context: bool = False
    performed_search: bool = True
    errors: list[str] = Field(default_factory=list)


class StoredResearchTurn(BaseModel):
    turn_id: UUID
    turn_index: int = Field(ge=1)

    question: str
    detected_language: str
    language_code: str
    english_query: str

    answer: str
    evidence: list[EvidenceClaim]
    limitations: list[str]

    scientific_total: int = Field(ge=0)
    scientific_providers: list[ProviderName]
    papers: list[RankedPaper]

    web_total: int = Field(ge=0)
    web_sources: list[WebSource]

    used_existing_context: bool
    performed_search: bool
    errors: list[str]

    created_at: datetime


class ResearchSessionSummary(BaseModel):
    research_id: UUID
    initial_question: str

    detected_language: str
    language_code: str

    turn_count: int = Field(ge=0)

    created_at: datetime
    updated_at: datetime


class ResearchHistoryResponse(BaseModel):
    total: int = Field(ge=0)
    limit: int = Field(ge=1)
    offset: int = Field(ge=0)

    sessions: list[ResearchSessionSummary]


class ResearchSessionDetail(BaseModel):
    research_id: UUID
    initial_question: str

    detected_language: str
    language_code: str

    created_at: datetime
    updated_at: datetime

    total_turns: int = Field(ge=0)
    has_more_turns: bool = False
    next_before_turn_index: int | None = Field(
        default=None,
        ge=1,
    )

    turns: list[StoredResearchTurn]


class ResearchDeleteResponse(BaseModel):
    research_id: UUID
    message: str
