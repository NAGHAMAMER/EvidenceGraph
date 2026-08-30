
from functools import lru_cache

import numpy as np
from fastembed import TextEmbedding
from numpy.typing import NDArray

from app.core.config import settings


FloatArray = NDArray[np.float32]


class EmbeddingService:
    def __init__(
        self,
        model_name: str | None = None,
        cache_dir: str | None = None,
    ) -> None:
        self.model_name = model_name or settings.embedding_model
        self.cache_dir = cache_dir or settings.embedding_cache_dir
        self._model: TextEmbedding | None = None

    @property
    def model(self) -> TextEmbedding:
        if self._model is None:
            self._model = TextEmbedding(
                model_name=self.model_name,
                cache_dir=self.cache_dir,
            )

        return self._model

    def embed_text(self, text: str) -> FloatArray:
        return self.embed_texts([text])[0]

    def embed_texts(self, texts: list[str]) -> FloatArray:
        if not texts:
            raise ValueError("At least one text is required.")

        cleaned_texts = [text.strip() for text in texts]

        if any(not text for text in cleaned_texts):
            raise ValueError("Texts must not be empty.")

        vectors = list(self.model.embed(cleaned_texts))

        return np.asarray(vectors, dtype=np.float32)

    @staticmethod
    def cosine_similarities(
        query_vector: FloatArray,
        document_vectors: FloatArray,
    ) -> FloatArray:
        query = np.asarray(query_vector, dtype=np.float32)
        documents = np.asarray(document_vectors, dtype=np.float32)

        if query.ndim != 1:
            raise ValueError("Query vector must be one-dimensional.")

        if documents.ndim != 2:
            raise ValueError("Document vectors must be two-dimensional.")

        if documents.shape[1] != query.shape[0]:
            raise ValueError("Query and document dimensions must match.")

        query_norm = np.linalg.norm(query)
        document_norms = np.linalg.norm(documents, axis=1)
        denominators = document_norms * query_norm

        return np.divide(
            documents @ query,
            denominators,
            out=np.zeros(documents.shape[0], dtype=np.float32),
            where=denominators != 0,
        )


@lru_cache
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()
