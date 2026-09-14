from pydantic import BaseModel, Field


class FollowUpResearchRequest(BaseModel):
    question: str = Field(
        min_length=2,
        max_length=1000,
    )
    limit: int = Field(
        default=5,
        ge=1,
        le=10,
    )


class FollowUpAnalysis(BaseModel):
    detected_language: str = Field(
        min_length=2,
        max_length=80,
    )
    language_code: str = Field(
        min_length=2,
        max_length=20,
    )
    english_query: str = Field(
        min_length=2,
        max_length=500,
        description=(
            "Standalone English query containing the context "
            "needed to research the follow-up question."
        ),
    )
    needs_search: bool
    decision_reason: str = Field(
        min_length=1,
        max_length=1000,
    )
