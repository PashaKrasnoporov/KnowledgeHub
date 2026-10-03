from functools import lru_cache

import numpy as np
from sentence_transformers import (
    SentenceTransformer,
)


EMBEDDING_MODEL_NAME = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)

CHUNK_SIZE_WORDS = 120
CHUNK_OVERLAP_WORDS = 30


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(
        EMBEDDING_MODEL_NAME
    )


def split_text_into_chunks(
    text: str,
) -> list[str]:
    words = text.split()

    if not words:
        return []

    step = (
        CHUNK_SIZE_WORDS
        - CHUNK_OVERLAP_WORDS
    )

    chunks: list[str] = []

    start = 0

    while start < len(words):
        end = (
            start
            + CHUNK_SIZE_WORDS
        )

        chunk = " ".join(
            words[start:end]
        ).strip()

        if chunk:
            chunks.append(
                chunk
            )

        start += step

    return chunks


def create_text_embeddings(
    texts: list[str],
) -> np.ndarray:
    if not texts:
        return np.empty(
            (0, 0),
            dtype=np.float32,
        )

    model = get_embedding_model()

    return model.encode(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )


def create_query_embedding(
    query: str,
) -> np.ndarray:
    model = get_embedding_model()

    return model.encode(
        query,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )