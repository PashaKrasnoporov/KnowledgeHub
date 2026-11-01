from functools import lru_cache
import os

import numpy as np

from app.nalashtuvannia.parametry import (
    parametry,
)


EMBEDDING_MODEL_NAME = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)

CHUNK_SIZE_WORDS = 120
CHUNK_OVERLAP_WORDS = 30

FASTEMBED_CACHE_PATH = os.getenv(
    "FASTEMBED_CACHE_PATH",
    "/tmp/fastembed_cache",
)


def _use_fastembed() -> bool:
    return (
        parametry.deployment_profile
        == "railway-ml"
    )


@lru_cache(maxsize=1)
def get_embedding_model():
    """
    Local development keeps SentenceTransformer.
    Railway uses the same multilingual model through
    FastEmbed / ONNX Runtime to avoid the PyTorch stack.
    """
    if _use_fastembed():
        from fastembed import TextEmbedding

        return TextEmbedding(
            model_name=EMBEDDING_MODEL_NAME,
            cache_dir=FASTEMBED_CACHE_PATH,
            threads=2,
            providers=[
                "CPUExecutionProvider",
            ],
        )

    from sentence_transformers import (
        SentenceTransformer,
    )

    return SentenceTransformer(
        EMBEDDING_MODEL_NAME
    )


def _normalize_rows(
    values: np.ndarray,
) -> np.ndarray:
    matrix = np.asarray(
        values,
        dtype=np.float32,
    )

    if matrix.size == 0:
        return matrix

    if matrix.ndim == 1:
        norm = float(
            np.linalg.norm(
                matrix
            )
        )

        if norm > 0:
            matrix = (
                matrix
                / norm
            )

        return matrix.astype(
            np.float32,
            copy=False,
        )

    norms = np.linalg.norm(
        matrix,
        axis=1,
        keepdims=True,
    )

    norms = np.where(
        norms > 0,
        norms,
        1.0,
    )

    return (
        matrix
        / norms
    ).astype(
        np.float32,
        copy=False,
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

    if _use_fastembed():
        embeddings = np.asarray(
            list(
                model.embed(
                    texts
                )
            ),
            dtype=np.float32,
        )
    else:
        embeddings = model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )

    return _normalize_rows(
        embeddings
    )


def create_query_embedding(
    query: str,
) -> np.ndarray:
    model = get_embedding_model()

    if _use_fastembed():
        vectors = list(
            model.embed(
                [
                    query
                ]
            )
        )

        vector = np.asarray(
            vectors[0],
            dtype=np.float32,
        )
    else:
        vector = model.encode(
            query,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )

    return _normalize_rows(
        vector
    )
