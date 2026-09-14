from typing import TypedDict

from app.schemas.follow_up import FollowUpAnalysis
from app.schemas.paper import SemanticPaperSearchResponse
from app.schemas.research import (
    GeneratedResearchAnswer,
    ResearchSessionDetail,
    WebSearchResponse,
)


class ResearchState(TypedDict, total=False):
    question: str
    limit: int

    detected_language: str
    language_code: str
    english_query: str

    scientific_result: SemanticPaperSearchResponse
    web_result: WebSearchResponse

    generated_answer: GeneratedResearchAnswer

    errors: list[str]


class FollowUpResearchState(TypedDict, total=False):
    question: str
    limit: int
    session: ResearchSessionDetail

    analysis: FollowUpAnalysis

    scientific_result: SemanticPaperSearchResponse
    web_result: WebSearchResponse

    generated_answer: GeneratedResearchAnswer

    used_existing_context: bool
    performed_search: bool

    errors: list[str]
