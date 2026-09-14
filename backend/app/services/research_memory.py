from functools import lru_cache

from app.schemas.paper import (
    ProviderName,
    RankedPaper,
    SemanticPaperSearchResponse,
)
from app.schemas.research import (
    ResearchSessionDetail,
    WebSearchResponse,
    WebSource,
)


class ResearchMemoryService:
    @staticmethod
    def has_sources(
        session: ResearchSessionDetail,
    ) -> bool:
        return any(
            turn.papers or turn.web_sources
            for turn in session.turns
        )

    def build_scientific_result(
        self,
        session: ResearchSessionDetail,
        query: str,
        limit: int,
    ) -> SemanticPaperSearchResponse:
        collected_papers = [
            paper
            for turn in reversed(session.turns)
            for paper in turn.papers
        ]

        unique_papers = self._deduplicate_papers(
            collected_papers
        )
        returned_papers = unique_papers[:limit]

        providers = self._collect_providers(
            returned_papers
        )

        return SemanticPaperSearchResponse(
            query=query,
            total=len(unique_papers),
            returned=len(returned_papers),
            providers=providers,
            papers=returned_papers,
        )

    def build_web_result(
        self,
        session: ResearchSessionDetail,
        query: str,
        limit: int,
    ) -> WebSearchResponse:
        collected_sources = [
            source
            for turn in reversed(session.turns)
            for source in turn.web_sources
        ]

        unique_sources = self._deduplicate_web_sources(
            collected_sources
        )
        returned_sources = unique_sources[:limit]

        return WebSearchResponse(
            query=query,
            total=len(unique_sources),
            results=returned_sources,
        )

    def merge_scientific_results(
        self,
        query: str,
        saved_result: SemanticPaperSearchResponse,
        new_result: SemanticPaperSearchResponse,
        limit: int,
    ) -> SemanticPaperSearchResponse:
        combined_papers = [
            *new_result.papers,
            *saved_result.papers,
        ]

        unique_papers = self._deduplicate_papers(
            combined_papers
        )
        returned_papers = unique_papers[:limit]

        providers = list(
            dict.fromkeys(
                [
                    *new_result.providers,
                    *saved_result.providers,
                    *self._collect_providers(
                        returned_papers
                    ),
                ]
            )
        )

        return SemanticPaperSearchResponse(
            query=query,
            total=len(unique_papers),
            returned=len(returned_papers),
            providers=providers,
            papers=returned_papers,
        )

    def merge_web_results(
        self,
        query: str,
        saved_result: WebSearchResponse,
        new_result: WebSearchResponse,
        limit: int,
    ) -> WebSearchResponse:
        combined_sources = [
            *new_result.results,
            *saved_result.results,
        ]

        unique_sources = self._deduplicate_web_sources(
            combined_sources
        )
        returned_sources = unique_sources[:limit]

        return WebSearchResponse(
            query=query,
            total=len(unique_sources),
            results=returned_sources,
        )

    @staticmethod
    def _paper_key(
        paper: RankedPaper,
    ) -> str:
        if paper.doi:
            return (
                "doi:"
                f"{paper.doi.strip().casefold()}"
            )

        normalized_title = " ".join(
            paper.title.casefold().split()
        )

        return (
            "title:"
            f"{normalized_title}:"
            f"{paper.publication_year or 'unknown'}"
        )

    def _deduplicate_papers(
        self,
        papers: list[RankedPaper],
    ) -> list[RankedPaper]:
        unique_papers: list[RankedPaper] = []
        key_positions: dict[str, int] = {}

        for paper in papers:
            key = self._paper_key(paper)

            if key not in key_positions:
                key_positions[key] = len(unique_papers)
                unique_papers.append(paper)
                continue

            position = key_positions[key]
            existing = unique_papers[position]

            providers = list(
                dict.fromkeys(
                    [
                        *existing.providers,
                        *paper.providers,
                    ]
                )
            )

            abstracts = [
                abstract
                for abstract in (
                    existing.abstract,
                    paper.abstract,
                )
                if abstract
            ]

            abstract = (
                max(abstracts, key=len)
                if abstracts
                else None
            )

            unique_papers[position] = existing.model_copy(
                update={
                    "abstract": abstract,
                    "authors": (
                        existing.authors
                        if len(existing.authors)
                        >= len(paper.authors)
                        else paper.authors
                    ),
                    "citation_count": max(
                        existing.citation_count,
                        paper.citation_count,
                    ),
                    "topics": list(
                        dict.fromkeys(
                            [
                                *existing.topics,
                                *paper.topics,
                            ]
                        )
                    ),
                    "providers": providers,
                    "semantic_score": max(
                        existing.semantic_score,
                        paper.semantic_score,
                    ),
                }
            )

        return unique_papers

    @staticmethod
    def _deduplicate_web_sources(
        sources: list[WebSource],
    ) -> list[WebSource]:
        unique_sources: list[WebSource] = []
        seen_urls: set[str] = set()

        for source in sources:
            normalized_url = (
                source.url.strip().casefold()
            )

            if normalized_url in seen_urls:
                continue

            seen_urls.add(normalized_url)
            unique_sources.append(source)

        return unique_sources

    @staticmethod
    def _collect_providers(
        papers: list[RankedPaper],
    ) -> list[ProviderName]:
        return list(
            dict.fromkeys(
                provider
                for paper in papers
                for provider in paper.providers
            )
        )


@lru_cache
def get_research_memory_service() -> ResearchMemoryService:
    return ResearchMemoryService()
