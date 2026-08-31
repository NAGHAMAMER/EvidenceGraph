import asyncio
import logging
from functools import lru_cache

from app.schemas.paper import (
    Paper,
    ProviderName,
    SemanticPaperSearchResponse,
)
from app.services.paper_search import (
    PaperSearchError,
    PaperSearchService,
    get_paper_search_service,
)
from app.services.semantic_ranking import (
    SemanticRankingService,
    get_semantic_ranking_service,
)


logger = logging.getLogger(__name__)


class MultilingualScientificSearchService:
    def __init__(
        self,
        paper_search_service: PaperSearchService,
        semantic_ranking_service: SemanticRankingService,
    ) -> None:
        self.paper_search_service = paper_search_service
        self.semantic_ranking_service = semantic_ranking_service

    async def search(
        self,
        original_query: str,
        english_query: str,
        limit: int,
    ) -> SemanticPaperSearchResponse:
        clean_original_query = original_query.strip()
        clean_english_query = english_query.strip()

        if not clean_original_query:
            raise ValueError(
                "Original query cannot be empty."
            )

        if not clean_english_query:
            raise ValueError(
                "English query cannot be empty."
            )

        if limit < 1:
            raise ValueError(
                "Limit must be at least 1."
            )

        candidate_limit = min(limit * 3, 50)

        queries = [clean_english_query]

        if (
            clean_original_query.casefold()
            != clean_english_query.casefold()
        ):
            queries.insert(0, clean_original_query)

        search_results = await asyncio.gather(
            *[
                self.paper_search_service.search(
                    query=query,
                    limit=candidate_limit,
                )
                for query in queries
            ],
            return_exceptions=True,
        )

        combined_papers: list[Paper] = []
        successful_providers: list[ProviderName] = []

        for query, result in zip(
            queries,
            search_results,
            strict=True,
        ):
            if isinstance(result, Exception):
                logger.warning(
                    "Scientific search failed for query %s: %s",
                    query,
                    result,
                )
                continue

            combined_papers.extend(result.papers)

            for provider in result.providers:
                if provider not in successful_providers:
                    successful_providers.append(provider)

        if not combined_papers:
            raise PaperSearchError(
                "All multilingual scientific searches failed."
            )

        unique_papers = (
            self.paper_search_service.deduplicate_papers(
                combined_papers
            )
        )

        ranked_papers = await asyncio.to_thread(
            self.semantic_ranking_service.rank,
            clean_english_query,
            unique_papers,
            limit,
        )

        return SemanticPaperSearchResponse(
            query=clean_original_query,
            total=len(unique_papers),
            returned=len(ranked_papers),
            providers=successful_providers,
            papers=ranked_papers,
        )


@lru_cache
def get_multilingual_scientific_search_service(
) -> MultilingualScientificSearchService:
    return MultilingualScientificSearchService(
        paper_search_service=get_paper_search_service(),
        semantic_ranking_service=get_semantic_ranking_service(),
    )