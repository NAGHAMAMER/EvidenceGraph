import logging

from fastapi import (
    APIRouter,
    HTTPException,
    status,
)

from app.agents.research_graph import run_research_agent
from app.schemas.research import (
    ResearchAgentRequest,
    ResearchAgentResponse,
)


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/research",
    tags=["Research Agent"],
)


@router.post(
    "",
    response_model=ResearchAgentResponse,
    summary="Run the multilingual research agent",
    responses={
        502: {"description": "Research agent execution failed."},
        504: {"description": "An external research service timed out."},
    },
)
async def run_research(
    request: ResearchAgentRequest,
) -> ResearchAgentResponse:
    try:
        state = await run_research_agent(
            question=request.question,
            limit=request.limit,
        )

        scientific_result = state["scientific_result"]
        web_result = state["web_result"]
        generated_answer = state["generated_answer"]

        return ResearchAgentResponse(
            question=state["question"],
            detected_language=state["detected_language"],
            language_code=state["language_code"],
            english_query=state["english_query"],
            answer=generated_answer.answer,
            evidence=generated_answer.evidence,
            limitations=generated_answer.limitations,
            scientific_total=scientific_result.total,
            scientific_providers=(
                scientific_result.providers
            ),
            papers=scientific_result.papers,
            web_total=web_result.total,
            web_sources=web_result.results,
            errors=state.get("errors", []),
        )

    except ValueError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_CONTENT
            ),
            detail=str(error),
        ) from error

    except TimeoutError as error:
        logger.warning("Research agent request timed out.")

        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=(
                "An external research service timed out. "
                "Please try again later."
            ),
        ) from error

    except Exception as error:
        logger.exception(
            "Research agent execution failed."
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "The research agent could not complete "
                "the request."
            ),
        ) from error
