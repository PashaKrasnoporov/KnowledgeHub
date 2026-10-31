from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_api_user,
)
from app.baza_danykh.dependencies import (
    get_db_session,
)
from app.modeli.user import User
from app.nalashtuvannia.parametry import (
    parametry,
)
from app.repositories.document_repository import (
    search_documents_in_collection,
)
from app.services.collection_service import (
    get_user_collection,
)
from app.services.hybrid_search_service import (
    search_hybrid_documents,
)
from app.services.semantic_search_service import (
    search_semantic_documents,
)


router = APIRouter()


def build_search_snippet(
    document,
    query: str,
    max_length: int = 260,
) -> str | None:
    source = " ".join(
        (
            document.extracted_text
            or ""
        ).split()
    )

    if not source:
        return None

    lowered = source.casefold()

    terms = [
        term.casefold()
        for term in query.split()
        if len(term) >= 2
    ]

    positions = [
        lowered.find(term)
        for term in terms
    ]

    positions = [
        position
        for position in positions
        if position >= 0
    ]

    focus = (
        min(positions)
        if positions
        else 0
    )

    context_before = (
        max_length // 3
    )

    start = max(
        0,
        focus - context_before,
    )

    end = min(
        len(source),
        start + max_length,
    )

    if start > 0:
        space_position = (
            source.find(
                " ",
                start,
            )
        )

        if (
            space_position != -1
            and space_position < focus
        ):
            start = (
                space_position + 1
            )

    if end < len(source):
        space_position = (
            source.rfind(
                " ",
                start,
                end,
            )
        )

        if (
            space_position > start
        ):
            end = space_position

    snippet = (
        source[
            start:end
        ].strip()
    )

    if not snippet:
        return None

    if start > 0:
        snippet = (
            "... "
            + snippet
        )

    if end < len(source):
        snippet += " ..."

    return snippet


@router.get(
    "/collections/{collection_id}/search",
    summary="Search collection documents",
)
def api_search_documents(
    collection_id: int,
    q: str = Query(
        min_length=1,
        max_length=200,
    ),
    mode: str = Query(
        default="hybrid",
        pattern="^(lexical|semantic|hybrid)$",
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=50,
    ),
    user: User = Depends(
        get_api_user
    ),
    session: Session = Depends(
        get_db_session
    ),
):
    collection = get_user_collection(
        session=session,
        user=user,
        collection_id=collection_id,
    )

    if collection is None:
        raise HTTPException(
            status_code=404,
            detail="Collection not found.",
        )

    normalized_query = " ".join(
        q.strip().split()
    )

    if not normalized_query:
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty.",
        )

    if (
        not parametry.ml_enabled
        and mode != "lexical"
    ):
        raise HTTPException(
            status_code=503,
            detail=(
                "Semantic and hybrid search are disabled "
                "in the lightweight cloud deployment."
            ),
        )

    if mode == "lexical":
        raw_results = (
            search_documents_in_collection(
                session=session,
                collection_id=collection.id,
                search_text=normalized_query,
            )
        )

        results = [
            {
                "document": {
                    "id": document.id,
                    "collection_id": document.collection_id,
                    "original_name": document.original_name,
                    "mime_type": document.mime_type,
                    "size_bytes": document.size_bytes,
                    "processing_status": (
                        document.processing_status
                    ),
                    "processing_error": (
                        document.processing_error
                    ),
                    "created_at": document.created_at,
                },
                "score": float(score),
                "snippet": build_search_snippet(
                    document,
                    normalized_query,
                ),
            }
            for document, score
            in raw_results[:limit]
        ]

    elif mode == "semantic":
        raw_results = (
            search_semantic_documents(
                session=session,
                collection=collection,
                search_text=normalized_query,
                limit=limit,
            )
        )

        results = [
            {
                "document": {
                    "id": result.document.id,
                    "collection_id": (
                        result.document.collection_id
                    ),
                    "original_name": (
                        result.document.original_name
                    ),
                    "mime_type": (
                        result.document.mime_type
                    ),
                    "size_bytes": (
                        result.document.size_bytes
                    ),
                    "processing_status": (
                        result.document.processing_status
                    ),
                    "processing_error": (
                        result.document.processing_error
                    ),
                    "created_at": (
                        result.document.created_at
                    ),
                },
                "score": float(result.score),
                "snippet": build_search_snippet(
                    result.document,
                    normalized_query,
                ),
            }
            for result in raw_results
        ]

    else:
        raw_results = (
            search_hybrid_documents(
                session=session,
                collection=collection,
                search_text=normalized_query,
                limit=limit,
            )
        )

        results = [
            {
                "document": {
                    "id": result.document.id,
                    "collection_id": (
                        result.document.collection_id
                    ),
                    "original_name": (
                        result.document.original_name
                    ),
                    "mime_type": (
                        result.document.mime_type
                    ),
                    "size_bytes": (
                        result.document.size_bytes
                    ),
                    "processing_status": (
                        result.document.processing_status
                    ),
                    "processing_error": (
                        result.document.processing_error
                    ),
                    "created_at": (
                        result.document.created_at
                    ),
                },
                "score": float(result.score),
                "snippet": build_search_snippet(
                    result.document,
                    normalized_query,
                ),
            }
            for result in raw_results
        ]

    return {
        "query": normalized_query,
        "mode": mode,
        "count": len(results),
        "results": results,
    }
