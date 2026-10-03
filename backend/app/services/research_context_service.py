import re

import numpy as np
from sqlalchemy.orm import Session

from app.modeli.collection import Collection
from app.repositories.document_chunk_repository import (
    get_collection_chunks,
)
from app.schemas.research import (
    ResearchAnswerPointAPI,
    ResearchResponseAPI,
    ResearchSourceAPI,
)
from app.services.embedding_service import (
    create_query_embedding,
)


RESEARCH_SEMANTIC_WEIGHT = 0.75
RESEARCH_LEXICAL_WEIGHT = 0.25
MAX_CHUNKS_PER_DOCUMENT = 2

TOKEN_PATTERN = re.compile(
    r"[0-9A-Za-zА-Яа-яІіЇїЄєҐґ_'-]{2,}"
)

SENTENCE_SPLIT_PATTERN = re.compile(
    r"(?<=[.!?])\s+|\n+"
)

STOP_WORDS = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "this",
    "from",
    "what",
    "how",
    "which",
    "are",
    "was",
    "were",
    "have",
    "has",
    "про",
    "для",
    "що",
    "як",
    "який",
    "яка",
    "які",
    "це",
    "та",
    "і",
    "або",
    "до",
    "від",
    "на",
    "у",
    "в",
    "з",
    "із",
    "за",
}


def _tokenize(
    text: str,
) -> list[str]:
    return [
        token.lower()
        for token in TOKEN_PATTERN.findall(
            text
        )
    ]


def _informative_tokens(
    text: str,
) -> set[str]:
    tokens = set(
        _tokenize(
            text
        )
    )

    informative = {
        token
        for token in tokens
        if token not in STOP_WORDS
    }

    return informative or tokens


def _lexical_score(
    query: str,
    chunk_text: str,
) -> float:
    query_tokens = _informative_tokens(
        query
    )

    if not query_tokens:
        return 0.0

    chunk_tokens = set(
        _tokenize(
            chunk_text
        )
    )

    overlap = (
        len(
            query_tokens
            & chunk_tokens
        )
        / len(
            query_tokens
        )
    )

    normalized_query = (
        " ".join(
            query.lower().split()
        )
    )

    phrase_bonus = 0.0

    if (
        normalized_query
        and normalized_query
        in chunk_text.lower()
    ):
        phrase_bonus = 0.15

    return min(
        1.0,
        overlap + phrase_bonus,
    )


def _semantic_score(
    chunk_embedding: list[float],
    query_embedding: np.ndarray,
) -> float:
    embedding = np.asarray(
        chunk_embedding,
        dtype=np.float32,
    )

    raw_score = float(
        np.dot(
            embedding,
            query_embedding,
        )
    )

    return max(
        0.0,
        min(
            1.0,
            raw_score,
        ),
    )


def _excerpt(
    text: str,
    max_length: int = 700,
) -> str:
    normalized = " ".join(
        text.split()
    )

    if len(normalized) <= max_length:
        return normalized

    shortened = normalized[
        :max_length
    ].rsplit(
        " ",
        1,
    )[0]

    return (
        shortened.rstrip(
            " ,.;:"
        )
        + "…"
    )


def _sentence_candidates(
    text: str,
) -> list[str]:
    sentences = []

    for part in SENTENCE_SPLIT_PATTERN.split(
        text
    ):
        sentence = " ".join(
            part.split()
        ).strip()

        if len(sentence) < 35:
            continue

        if len(sentence) > 420:
            sentence = _excerpt(
                sentence,
                max_length=420,
            )

        sentences.append(
            sentence
        )

    return sentences


def _build_answer_points(
    question: str,
    sources: list[ResearchSourceAPI],
    max_points: int = 4,
) -> list[ResearchAnswerPointAPI]:
    query_tokens = _informative_tokens(
        question
    )

    candidates = []

    for source in sources:
        sentences = _sentence_candidates(
            source.excerpt
        )

        if not sentences:
            sentences = [
                source.excerpt
            ]

        for sentence in sentences:
            sentence_tokens = set(
                _tokenize(
                    sentence
                )
            )

            if query_tokens:
                overlap = (
                    len(
                        query_tokens
                        & sentence_tokens
                    )
                    / len(
                        query_tokens
                    )
                )
            else:
                overlap = 0.0

            score = (
                0.65 * overlap
                + 0.35 * source.score
            )

            candidates.append(
                (
                    score,
                    sentence,
                    source.source_number,
                )
            )

    candidates.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    answer_points = []
    seen = set()

    for _, sentence, source_number in candidates:
        normalized = sentence.lower()

        if normalized in seen:
            continue

        seen.add(
            normalized
        )

        answer_points.append(
            ResearchAnswerPointAPI(
                text=sentence,
                source_number=source_number,
            )
        )

        if len(answer_points) >= max_points:
            break

    return answer_points


def build_research_response(
    session: Session,
    collection: Collection,
    question: str,
    limit: int = 5,
) -> ResearchResponseAPI:
    normalized_question = " ".join(
        question.strip().split()
    )

    if not normalized_question:
        return ResearchResponseAPI(
            question="",
            mode="hybrid-chunks",
            count=0,
            answer_points=[],
            sources=[],
        )

    rows = get_collection_chunks(
        session=session,
        collection_id=collection.id,
    )

    if not rows:
        return ResearchResponseAPI(
            question=normalized_question,
            mode="hybrid-chunks",
            count=0,
            answer_points=[],
            sources=[],
        )

    query_embedding = create_query_embedding(
        normalized_question
    )

    ranked = []

    for chunk, document in rows:
        semantic_score = _semantic_score(
            chunk.embedding,
            query_embedding,
        )

        lexical_score = _lexical_score(
            normalized_question,
            chunk.chunk_text,
        )

        score = (
            RESEARCH_SEMANTIC_WEIGHT
            * semantic_score
            + RESEARCH_LEXICAL_WEIGHT
            * lexical_score
        )

        ranked.append(
            {
                "document": document,
                "chunk": chunk,
                "score": score,
                "semantic_score": semantic_score,
                "lexical_score": lexical_score,
            }
        )

    ranked.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    selected = []
    per_document: dict[int, int] = {}

    for item in ranked:
        document_id = (
            item["document"].id
        )

        used = per_document.get(
            document_id,
            0,
        )

        if used >= MAX_CHUNKS_PER_DOCUMENT:
            continue

        selected.append(
            item
        )

        per_document[
            document_id
        ] = used + 1

        if len(selected) >= limit:
            break

    sources = [
        ResearchSourceAPI(
            source_number=index,
            document_id=item[
                "document"
            ].id,
            original_name=item[
                "document"
            ].original_name,
            chunk_index=item[
                "chunk"
            ].chunk_index,
            excerpt=_excerpt(
                item[
                    "chunk"
                ].chunk_text
            ),
            score=round(
                float(
                    item["score"]
                ),
                6,
            ),
            semantic_score=round(
                float(
                    item[
                        "semantic_score"
                    ]
                ),
                6,
            ),
            lexical_score=round(
                float(
                    item[
                        "lexical_score"
                    ]
                ),
                6,
            ),
        )
        for index, item
        in enumerate(
            selected,
            start=1,
        )
    ]

    return ResearchResponseAPI(
        question=normalized_question,
        mode="hybrid-chunks",
        count=len(sources),
        answer_points=(
            _build_answer_points(
                normalized_question,
                sources,
            )
        ),
        sources=sources,
    )
