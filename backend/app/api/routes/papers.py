from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)

from app.schemas.paper import PaperSearchResponse
from app.services.paper_search import (
    PaperSearchError,
    PaperSearchService,
)


router = APIRouter(
    prefix="/papers",
    tags=["Scientific Papers"],
)


def get_paper_search_service() -> PaperSearchService:
    return PaperSearchService()


@router.get(
    "/search",
    response_model=PaperSearchResponse,
    summary="Search for scientific papers",
)
async def search_papers(
    query: str = Query(
        min_length=2,
        max_length=300,
        description="Scientific research query",
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of papers to return",
    ),
    search_service: PaperSearchService = Depends(
        get_paper_search_service
    ),
) -> PaperSearchResponse:
    try:
        return await search_service.search(
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
