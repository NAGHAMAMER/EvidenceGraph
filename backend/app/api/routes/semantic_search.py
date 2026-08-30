from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)

from app.schemas.paper import SemanticPaperSearchResponse
from app.services.paper_search import PaperSearchError
from app.services.semantic_search import (
    SemanticSearchService,
    get_semantic_search_service,
)


router = APIRouter(
    prefix="/papers",
    tags=["Scientific Papers"],
)


@router.get(
    "/semantic-search",
    response_model=SemanticPaperSearchResponse,
    summary="Search and semantically rank scientific papers",
)
async def semantic_search_papers(
    query: str = Query(
        min_length=2,
        max_length=300,
        description="Scientific research query",
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=20,
        description="Maximum number of ranked papers",
    ),
    semantic_service: SemanticSearchService = Depends(
        get_semantic_search_service
    ),
) -> SemanticPaperSearchResponse:
    try:
        return await semantic_service.search(
            query=query,
            limit=limit,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error

    except PaperSearchError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error
