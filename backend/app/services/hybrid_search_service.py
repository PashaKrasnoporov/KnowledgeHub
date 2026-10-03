from sqlalchemy.orm import Session

from app.modeli.collection import Collection
from app.repositories.document_repository import (
    get_documents_by_collection_id,
)
from app.schemas.search import (
    DocumentSearchResult,
)
from app.services.document_service import (
    search_collection_documents,
)
from app.services.semantic_search_service import (
    search_semantic_documents,
)


HYBRID_LEXICAL_WEIGHT = 0.30
HYBRID_SEMANTIC_WEIGHT = 0.70


def normalize_scores(
    scores: dict[int, float],
) -> dict[int, float]:
    if not scores:
        return {}

    values = list(
        scores.values()
    )

    minimum = min(values)
    maximum = max(values)

    if maximum == minimum:
        return {
            document_id: 1.0
            for document_id in scores
        }

    return {
        document_id: (
            (score - minimum)
            / (maximum - minimum)
        )
        for document_id, score
        in scores.items()
    }


def search_hybrid_documents(
    session: Session,
    collection: Collection,
    search_text: str,
    lexical_weight: float = (
        HYBRID_LEXICAL_WEIGHT
    ),
    semantic_weight: float = (
        HYBRID_SEMANTIC_WEIGHT
    ),
    limit: int = 10,
) -> list[DocumentSearchResult]:
    normalized_query = " ".join(
        search_text.strip().split()
    )

    if not normalized_query:
        return []

    if lexical_weight < 0:
        raise ValueError(
            "lexical_weight must be >= 0"
        )

    if semantic_weight < 0:
        raise ValueError(
            "semantic_weight must be >= 0"
        )

    total_weight = (
        lexical_weight
        + semantic_weight
    )

    if total_weight <= 0:
        raise ValueError(
            "At least one weight "
            "must be positive."
        )

    lexical_weight = (
        lexical_weight
        / total_weight
    )

    semantic_weight = (
        semantic_weight
        / total_weight
    )

    documents = (
        get_documents_by_collection_id(
            session=session,
            collection_id=collection.id,
        )
    )

    document_map = {
        document.id: document
        for document in documents
        if (
            document.processing_status
            == "ready"
            and document.extracted_text
        )
    }

    if not document_map:
        return []

    lexical_results = (
        search_collection_documents(
            session=session,
            collection=collection,
            search_text=normalized_query,
        )
    )

    semantic_results = (
        search_semantic_documents(
            session=session,
            collection=collection,
            search_text=normalized_query,
            limit=len(document_map),
        )
    )

    lexical_scores = {
        result.document.id:
            result.score
        for result in lexical_results
    }

    semantic_scores = {
        result.document.id:
            result.score
        for result in semantic_results
    }

    lexical_normalized = (
        normalize_scores(
            lexical_scores
        )
    )

    semantic_normalized = (
        normalize_scores(
            semantic_scores
        )
    )

    results: list[
        DocumentSearchResult
    ] = []

    for document_id, document in (
        document_map.items()
    ):
        lexical_score = (
            lexical_normalized.get(
                document_id,
                0.0,
            )
        )

        semantic_score = (
            semantic_normalized.get(
                document_id,
                0.0,
            )
        )

        hybrid_score = (
            lexical_weight
            * lexical_score
            + semantic_weight
            * semantic_score
        )

        results.append(
            DocumentSearchResult(
                document=document,
                score=hybrid_score,
            )
        )

    results.sort(
        key=lambda result: result.score,
        reverse=True,
    )

    return results[
        :max(1, limit)
    ]