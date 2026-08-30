import numpy as np
import pytest

from app.nlp.embeddings import EmbeddingService


class FakeEmbeddingModel:
    def embed(self, texts: list[str]):
        vectors = {
            "first text": np.array([1.0, 0.0, 0.0], dtype=np.float32),
            "second text": np.array([0.0, 1.0, 0.0], dtype=np.float32),
        }

        for text in texts:
            yield vectors[text]


def create_test_service() -> EmbeddingService:
    service = EmbeddingService(
        model_name="fake-model",
        cache_dir="/tmp/fake-model",
    )
    service._model = FakeEmbeddingModel()  # type: ignore[assignment]

    return service


def test_embed_texts_returns_matrix() -> None:
    service = create_test_service()

    vectors = service.embed_texts(
        [" first text ", "second text"],
    )

    assert vectors.shape == (2, 3)
    assert vectors.dtype == np.float32

    np.testing.assert_array_equal(
        vectors,
        np.array(
            [
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
            ],
            dtype=np.float32,
        ),
    )


def test_embed_text_returns_one_vector() -> None:
    service = create_test_service()

    vector = service.embed_text("first text")

    assert vector.shape == (3,)

    np.testing.assert_array_equal(
        vector,
        np.array([1.0, 0.0, 0.0], dtype=np.float32),
    )


@pytest.mark.parametrize(
    "texts",
    [
        [],
        [""],
        ["   "],
        ["first text", ""],
    ],
)
def test_embed_texts_rejects_empty_inputs(texts: list[str]) -> None:
    service = create_test_service()

    with pytest.raises(ValueError):
        service.embed_texts(texts)


def test_cosine_similarities_returns_expected_scores() -> None:
    query = np.array([1.0, 0.0], dtype=np.float32)

    documents = np.array(
        [
            [1.0, 0.0],
            [0.0, 1.0],
            [-1.0, 0.0],
            [0.0, 0.0],
        ],
        dtype=np.float32,
    )

    scores = EmbeddingService.cosine_similarities(
        query,
        documents,
    )

    np.testing.assert_allclose(
        scores,
        np.array([1.0, 0.0, -1.0, 0.0], dtype=np.float32),
        atol=1e-6,
    )


def test_cosine_similarities_rejects_mismatched_dimensions() -> None:
    query = np.array([1.0, 0.0], dtype=np.float32)
    documents = np.array([[1.0, 0.0, 0.0]], dtype=np.float32)

    with pytest.raises(
        ValueError,
        match="dimensions must match",
    ):
        EmbeddingService.cosine_similarities(
            query,
            documents,
        )
