import numpy as np
import pytest

from app.nlp.embeddings import EmbeddingService
from app.schemas.paper import Paper
from app.services.semantic_ranking import SemanticRankingService


class FakeEmbeddingService:
    def embed_text(self, text: str) -> np.ndarray:
        return np.array(
            [1.0, 0.0],
            dtype=np.float32,
        )

    def embed_texts(
        self,
        texts: list[str],
    ) -> np.ndarray:
        vectors = []

        for text in texts:
            if "Strong paper" in text:
                vector = [1.0, 0.0]
            elif "Related paper" in text:
                vector = [0.8, 0.2]
            else:
                vector = [0.0, 1.0]

            vectors.append(vector)

        return np.asarray(
            vectors,
            dtype=np.float32,
        )

    @staticmethod
    def cosine_similarities(
        query_vector: np.ndarray,
        document_vectors: np.ndarray,
    ) -> np.ndarray:
        return EmbeddingService.cosine_similarities(
            query_vector,
            document_vectors,
        )


def create_paper(
    paper_id: str,
    title: str,
    abstract: str | None = None,
    topics: list[str] | None = None,
) -> Paper:
    return Paper(
        id=paper_id,
        doi=None,
        title=title,
        abstract=abstract,
        authors=[],
        publication_year=2024,
        publication_date=None,
        venue=None,
        url=None,
        pdf_url=None,
        citation_count=0,
        is_open_access=False,
        topics=topics or [],
        providers=["openalex"],
    )


def create_ranking_service() -> SemanticRankingService:
    return SemanticRankingService(
        embedding_service=FakeEmbeddingService(),  # type: ignore[arg-type]
    )


def test_build_paper_text_combines_available_metadata() -> None:
    paper = create_paper(
        paper_id="paper-1",
        title="Paper title",
        abstract="Paper abstract",
        topics=["NLP", "AI"],
    )

    text = SemanticRankingService.build_paper_text(paper)

    assert text == (
        "Paper title\n\n"
        "Paper abstract\n\n"
        "Topics: NLP, AI"
    )


def test_rank_orders_papers_by_semantic_similarity() -> None:
    service = create_ranking_service()

    papers = [
        create_paper("paper-1", "Unrelated paper"),
        create_paper("paper-2", "Strong paper"),
        create_paper("paper-3", "Related paper"),
    ]

    results = service.rank(
        query="semantic search",
        papers=papers,
    )

    assert [paper.id for paper in results] == [
        "paper-2",
        "paper-3",
        "paper-1",
    ]

    assert results[0].semantic_score == pytest.approx(1.0)
    assert results[0].semantic_score > results[1].semantic_score
    assert results[1].semantic_score > results[2].semantic_score


def test_rank_applies_limit_after_sorting() -> None:
    service = create_ranking_service()

    papers = [
        create_paper("paper-1", "Unrelated paper"),
        create_paper("paper-2", "Strong paper"),
        create_paper("paper-3", "Related paper"),
    ]

    results = service.rank(
        query="semantic search",
        papers=papers,
        limit=2,
    )

    assert len(results) == 2
    assert [paper.id for paper in results] == [
        "paper-2",
        "paper-3",
    ]


def test_rank_returns_empty_list_for_no_papers() -> None:
    service = create_ranking_service()

    results = service.rank(
        query="semantic search",
        papers=[],
    )

    assert results == []


@pytest.mark.parametrize(
    ("query", "limit"),
    [
        ("", None),
        ("   ", None),
        ("valid query", 0),
    ],
)
def test_rank_rejects_invalid_arguments(
    query: str,
    limit: int | None,
) -> None:
    service = create_ranking_service()

    with pytest.raises(ValueError):
        service.rank(
            query=query,
            papers=[],
            limit=limit,
        )
