from typing import TypedDict

from app.schemas.paper import SemanticPaperSearchResponse
from app.schemas.research import (
    GeneratedResearchAnswer,
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