import numpy as np
from sqlalchemy.orm import Session

from app.modeli.collection import Collection
from app.repositories.document_chunk_repository import (
    get_collection_chunks,
)
from app.schemas.search import (
    DocumentSearchResult,
)
from app.services.embedding_service import (
    create_query_embedding,
)


def search_semantic_documents(
    session: Session,
    collection: Collection,
    search_text: str,
    limit: int = 10,
) -> list[DocumentSearchResult]:
    normalized_query = " ".join(
        search_text.strip().split()
    )

    if not normalized_query:
        return []

    rows = get_collection_chunks(
        session=session,
        collection_id=collection.id,
    )

    if not rows:
        return []

    query_embedding = (
        create_query_embedding(
            normalized_query
        )
    )

    document_scores: dict[
        int,
        float,
    ] = {}

    documents = {}

    for chunk, document in rows:
        chunk_embedding = np.asarray(
            chunk.embedding,
            dtype=np.float32,
        )

        score = float(
            np.dot(
                chunk_embedding,
                query_embedding,
            )
        )

        previous_score = (
            document_scores.get(
                document.id
            )
        )

        if (
            previous_score is None
            or score > previous_score
        ):
            document_scores[
                document.id
            ] = score

        documents[
            document.id
        ] = document

    results = [
        DocumentSearchResult(
            document=documents[
                document_id
            ],
            score=score,
        )
        for document_id, score
        in document_scores.items()
    ]

    results.sort(
        key=lambda result: result.score,
        reverse=True,
    )

    return results[
        :max(
            1,
            limit,
        )
    ]