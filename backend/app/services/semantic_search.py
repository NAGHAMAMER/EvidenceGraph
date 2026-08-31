import asyncio
from functools import lru_cache

from app.schemas.paper import SemanticPaperSearchResponse
from app.services.paper_search import (
    PaperSearchService,
    get_paper_search_service,
)
from app.services.semantic_ranking import (
    SemanticRankingService,
    get_semantic_ranking_service,
)


class SemanticSearchService:
    def __init__(
        self,
        paper_search_service: PaperSearchService,
        semantic_ranking_service: SemanticRankingService,
    ) -> None:
        self.paper_search_service = paper_search_service
        self.semantic_ranking_service = semantic_ranking_service

    async def search(
        self,
        query: str,
        limit: int,
    ) -> SemanticPaperSearchResponse:
        candidate_limit = min(limit * 3, 50)

        search_result = await self.paper_search_service.search(
            query=query,
            limit=candidate_limit,
        )

        ranked_papers = await asyncio.to_thread(
            self.semantic_ranking_service.rank,
            query,
            search_result.papers,
            limit,
        )

        return SemanticPaperSearchResponse(
            query=query,
            total=search_result.total,
            returned=len(ranked_papers),
            providers=search_result.providers,
            papers=ranked_papers,
        )

@lru_cache
def get_semantic_search_service() -> SemanticSearchService:
    return SemanticSearchService(
        paper_search_service=get_paper_search_service(),
        semantic_ranking_service=get_semantic_ranking_service(),
    )
