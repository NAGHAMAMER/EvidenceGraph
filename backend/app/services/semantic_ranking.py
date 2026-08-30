from functools import lru_cache

import numpy as np

from app.nlp.embeddings import (
    EmbeddingService,
    get_embedding_service,
)
from app.schemas.paper import Paper, RankedPaper


class SemanticRankingService:
    def __init__(
        self,
        embedding_service: EmbeddingService,
    ) -> None:
        self.embedding_service = embedding_service

    @staticmethod
    def build_paper_text(paper: Paper) -> str:
        parts = [paper.title]

        if paper.abstract:
            parts.append(paper.abstract)

        if paper.topics:
            parts.append(
                "Topics: " + ", ".join(paper.topics),
            )

        return "\n\n".join(parts)

    def rank(
        self,
        query: str,
        papers: list[Paper],
        limit: int | None = None,
    ) -> list[RankedPaper]:
        cleaned_query = query.strip()

        if not cleaned_query:
            raise ValueError("Query must not be empty.")

        if limit is not None and limit < 1:
            raise ValueError("Limit must be at least 1.")

        if not papers:
            return []

        paper_texts = [
            self.build_paper_text(paper)
            for paper in papers
        ]

        query_vector = self.embedding_service.embed_text(
            cleaned_query,
        )
        paper_vectors = self.embedding_service.embed_texts(
            paper_texts,
        )

        scores = self.embedding_service.cosine_similarities(
            query_vector,
            paper_vectors,
        )

        ranked_papers = [
            RankedPaper(
                **paper.model_dump(),
                semantic_score=float(
                    np.clip(score, -1.0, 1.0),
                ),
            )
            for paper, score in zip(
                papers,
                scores,
                strict=True,
            )
        ]

        ranked_papers.sort(
            key=lambda paper: paper.semantic_score,
            reverse=True,
        )

        if limit is not None:
            return ranked_papers[:limit]

        return ranked_papers


@lru_cache
def get_semantic_ranking_service() -> SemanticRankingService:
    return SemanticRankingService(
        embedding_service=get_embedding_service(),
    )
