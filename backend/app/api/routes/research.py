import logging
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)

from app.agents.follow_up_graph import run_follow_up_agent
from app.agents.research_graph import run_research_agent
from app.schemas.follow_up import FollowUpResearchRequest
from app.schemas.research import (
    ResearchAgentRequest,
    ResearchAgentResponse,
    ResearchDeleteResponse,
    ResearchHistoryResponse,
    ResearchSessionDetail,
)
from app.services.research_repository import (
    ResearchNotFoundError,
    ResearchPersistenceError,
    ResearchRepository,
    get_research_repository,
)


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/research",
    tags=["Research Agent"],
)


@router.post(
    "",
    response_model=ResearchAgentResponse,
    summary="Run and save the multilingual research agent",
    responses={
        502: {
            "description": "Research agent execution failed.",
        },
        503: {
            "description": "Research result persistence failed.",
        },
        504: {
            "description": (
                "An external research service timed out."
            ),
        },
    },
)
async def run_research(
    request: ResearchAgentRequest,
    repository: Annotated[
        ResearchRepository,
        Depends(get_research_repository),
    ],
) -> ResearchAgentResponse:
    try:
        state = await run_research_agent(
            question=request.question,
            limit=request.limit,
        )

        scientific_result = state["scientific_result"]
        web_result = state["web_result"]
        generated_answer = state["generated_answer"]

        result = ResearchAgentResponse(
            research_id=uuid4(),
            turn_id=uuid4(),
            turn_index=1,
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
            used_existing_context=False,
            performed_search=True,
            errors=state.get("errors", []),
        )

        await repository.create_session(result)

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_CONTENT
            ),
            detail=str(error),
        ) from error

    except TimeoutError as error:
        logger.warning(
            "Research agent request timed out."
        )

        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=(
                "An external research service timed out. "
                "Please try again later."
            ),
        ) from error

    except ResearchPersistenceError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
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


@router.get(
    "/history",
    response_model=ResearchHistoryResponse,
    summary="List saved research sessions",
    responses={
        503: {
            "description": "Research history could not be loaded.",
        },
    },
)
async def list_research_history(
    repository: Annotated[
        ResearchRepository,
        Depends(get_research_repository),
    ],
    limit: Annotated[
        int,
        Query(
            ge=1,
            le=100,
            description=(
                "Maximum number of research sessions to return."
            ),
        ),
    ] = 20,
    offset: Annotated[
        int,
        Query(
            ge=0,
            description=(
                "Number of research sessions to skip."
            ),
        ),
    ] = 0,
) -> ResearchHistoryResponse:
    try:
        return await repository.list_sessions(
            limit=limit,
            offset=offset,
        )

    except ResearchPersistenceError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error


@router.post(
    "/{research_id}/follow-up",
    response_model=ResearchAgentResponse,
    summary="Ask a follow-up question in a research session",
    responses={
        404: {
            "description": "Research session not found.",
        },
        502: {
            "description": "Follow-up agent execution failed.",
        },
        503: {
            "description": "Follow-up result could not be saved.",
        },
        504: {
            "description": (
                "An external research service timed out."
            ),
        },
    },
)
async def run_research_follow_up(
    research_id: UUID,
    request: FollowUpResearchRequest,
    repository: Annotated[
        ResearchRepository,
        Depends(get_research_repository),
    ],
) -> ResearchAgentResponse:
    try:
        session = await repository.get_session(
            research_id
        )

        state = await run_follow_up_agent(
            question=request.question,
            session=session,
            limit=request.limit,
        )

        analysis = state["analysis"]
        scientific_result = state["scientific_result"]
        web_result = state["web_result"]
        generated_answer = state["generated_answer"]

        result = ResearchAgentResponse(
            research_id=research_id,
            turn_id=uuid4(),
            turn_index=len(session.turns) + 1,
            question=state["question"],
            detected_language=(
                analysis.detected_language
            ),
            language_code=analysis.language_code,
            english_query=analysis.english_query,
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
            used_existing_context=state.get(
                "used_existing_context",
                False,
            ),
            performed_search=state.get(
                "performed_search",
                False,
            ),
            errors=state.get("errors", []),
        )

        return await repository.append_turn(result)

    except ResearchNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_CONTENT
            ),
            detail=str(error),
        ) from error

    except TimeoutError as error:
        logger.warning(
            "Follow-up research request timed out."
        )

        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=(
                "An external research service timed out. "
                "Please try again later."
            ),
        ) from error

    except ResearchPersistenceError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error

    except Exception as error:
        logger.exception(
            "Follow-up research agent execution failed."
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "The follow-up research agent could not "
                "complete the request."
            ),
        ) from error


@router.get(
    "/{research_id}",
    response_model=ResearchSessionDetail,
    summary="Get turns from a saved research session",
    responses={
        404: {
            "description": "Research session not found.",
        },
        503: {
            "description": "Research session could not be loaded.",
        },
    },
)
async def get_research_session(
    research_id: UUID,
    repository: Annotated[
        ResearchRepository,
        Depends(get_research_repository),
    ],
    turn_limit: Annotated[
        int,
        Query(
            ge=1,
            le=20,
            description=(
                "Maximum number of conversation turns "
                "to return."
            ),
        ),
    ] = 1,
    before_turn_index: Annotated[
        int | None,
        Query(
            ge=1,
            description=(
                "Return turns older than this turn index."
            ),
        ),
    ] = None,
) -> ResearchSessionDetail:
    try:
        return await repository.get_session(
            research_id=research_id,
            turn_limit=turn_limit,
            before_turn_index=before_turn_index,
        )

    except ResearchNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_CONTENT
            ),
            detail=str(error),
        ) from error

    except ResearchPersistenceError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error


@router.delete(
    "/{research_id}",
    response_model=ResearchDeleteResponse,
    summary="Delete a saved research session",
    responses={
        404: {
            "description": "Research session not found.",
        },
        503: {
            "description": "Research session could not be deleted.",
        },
    },
)
async def delete_research_session(
    research_id: UUID,
    repository: Annotated[
        ResearchRepository,
        Depends(get_research_repository),
    ],
) -> ResearchDeleteResponse:
    try:
        await repository.delete_session(research_id)

        return ResearchDeleteResponse(
            research_id=research_id,
            message="Research session deleted successfully.",
        )

    except ResearchNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except ResearchPersistenceError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error
