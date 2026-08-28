import asyncio
import logging

from app.schemas.paper import Paper, PaperSearchResponse, ProviderName
from app.services.providers.base import PaperProvider
from app.services.providers.crossref import CrossrefProvider
from app.services.providers.openalex import OpenAlexProvider


logger = logging.getLogger(__name__)


class PaperSearchError(RuntimeError):
    pass


class PaperSearchService:
    def __init__(
        self,
        providers: list[PaperProvider] | None = None,
    ) -> None:
        if providers is None:
            self._providers: list[PaperProvider] = [
                OpenAlexProvider(),
                CrossrefProvider(),
            ]
        else:
            self._providers = providers

    async def search(
        self,
        query: str,
        limit: int = 10,
    ) -> PaperSearchResponse:
        clean_query = query.strip()

        if not clean_query:
            raise ValueError("Search query cannot be empty.")

        safe_limit = max(1, min(limit, 100))

        results = await asyncio.gather(
            *[
                provider.search(
                    query=clean_query,
                    limit=safe_limit,
                )
                for provider in self._providers
            ],
            return_exceptions=True,
        )

        successful_providers: list[ProviderName] = []
        provider_papers: list[list[Paper]] = []

        for provider, result in zip(
            self._providers,
            results,
            strict=True,
        ):
            if isinstance(result, Exception):
                logger.warning(
                    "Paper provider %s failed: %s",
                    provider.name,
                    result,
                )
                continue

            successful_providers.append(provider.name)
            provider_papers.append(result)

        if not successful_providers:
            raise PaperSearchError(
                "All scientific paper providers failed."
            )

        combined_papers = self._interleave(provider_papers)
        unique_papers = self._deduplicate(combined_papers)
        returned_papers = unique_papers[:safe_limit]

        return PaperSearchResponse(
            query=clean_query,
            total=len(unique_papers),
            returned=len(returned_papers),
            providers=successful_providers,
            papers=returned_papers,
        )

    @staticmethod
    def _interleave(
        provider_papers: list[list[Paper]],
    ) -> list[Paper]:
        if not provider_papers:
            return []

        combined: list[Paper] = []

        maximum_length = max(
            len(papers)
            for papers in provider_papers
        )

        for index in range(maximum_length):
            for papers in provider_papers:
                if index < len(papers):
                    combined.append(papers[index])

        return combined

    @staticmethod
    def _deduplicate(
        papers: list[Paper],
    ) -> list[Paper]:
        unique_papers: list[Paper] = []
        key_positions: dict[str, int] = {}

        for paper in papers:
            keys = PaperSearchService._paper_keys(paper)

            existing_position = next(
                (
                    key_positions[key]
                    for key in keys
                    if key in key_positions
                ),
                None,
            )

            if existing_position is None:
                position = len(unique_papers)
                unique_papers.append(paper)

                for key in keys:
                    key_positions[key] = position

                continue

            merged_paper = PaperSearchService._merge_papers(
                unique_papers[existing_position],
                paper,
            )

            unique_papers[existing_position] = merged_paper

            for key in PaperSearchService._paper_keys(
                merged_paper
            ):
                key_positions[key] = existing_position

        return unique_papers

    @staticmethod
    def _paper_keys(paper: Paper) -> list[str]:
        keys: list[str] = []

        if paper.doi:
            normalized_doi = paper.doi.strip().lower()
            keys.append(f"doi:{normalized_doi}")

        normalized_title = "".join(
            character
            if character.isalnum() or character.isspace()
            else " "
            for character in paper.title.casefold()
        )

        normalized_title = " ".join(
            normalized_title.split()
        )

        if normalized_title:
            year = paper.publication_year or "unknown"
            keys.append(
                f"title:{normalized_title}:{year}"
            )

        return keys

    @staticmethod
    def _merge_papers(
        first: Paper,
        second: Paper,
    ) -> Paper:
        providers = list(
            dict.fromkeys(
                [
                    *first.providers,
                    *second.providers,
                ]
            )
        )

        topics = list(
            dict.fromkeys(
                [
                    *first.topics,
                    *second.topics,
                ]
            )
        )

        authors = (
            first.authors
            if len(first.authors) >= len(second.authors)
            else second.authors
        )

        abstracts = [
            abstract
            for abstract in [
                first.abstract,
                second.abstract,
            ]
            if abstract
        ]

        abstract = (
            max(abstracts, key=len)
            if abstracts
            else None
        )

        is_open_access = (
            True
            if (
                first.is_open_access is True
                or second.is_open_access is True
            )
            else (
                first.is_open_access
                if first.is_open_access is not None
                else second.is_open_access
            )
        )

        doi = first.doi or second.doi

        return first.model_copy(
            update={
                "id": doi or first.id,
                "doi": doi,
                "abstract": abstract,
                "authors": authors,
                "publication_year": (
                    first.publication_year
                    or second.publication_year
                ),
                "publication_date": (
                    first.publication_date
                    or second.publication_date
                ),
                "venue": first.venue or second.venue,
                "url": first.url or second.url,
                "pdf_url": (
                    first.pdf_url
                    or second.pdf_url
                ),
                "citation_count": max(
                    first.citation_count,
                    second.citation_count,
                ),
                "is_open_access": is_open_access,
                "topics": topics,
                "providers": providers,
            }
        )
