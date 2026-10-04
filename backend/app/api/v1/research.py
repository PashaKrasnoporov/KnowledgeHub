from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_api_user,
    require_api_csrf,
)
from app.baza_danykh.dependencies import (
    get_db_session,
)
from app.modeli.user import User
from app.schemas.research import (
    ResearchGenerateRequestAPI,
    ResearchGeneratedResponseAPI,
    ResearchResponseAPI,
)
from app.services.collection_service import (
    get_user_collection,
)
from app.services.rag_generation_service import (
    generate_grounded_answer,
)
from app.services.research_context_service import (
    build_research_response,
)


router = APIRouter()


def _get_collection_or_404(
    collection_id: int,
    user: User,
    session: Session,
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

    return collection


@router.get(
    "/collections/{collection_id}/research",
    response_model=ResearchResponseAPI,
    summary="Build research context for a collection",
)
def api_research_collection(
    collection_id: int,
    q: str = Query(
        min_length=3,
        max_length=500,
    ),
    limit: int = Query(
        default=5,
        ge=1,
        le=10,
    ),
    user: User = Depends(
        get_api_user
    ),
    session: Session = Depends(
        get_db_session
    ),
):
    collection = _get_collection_or_404(
        collection_id=collection_id,
        user=user,
        session=session,
    )

    return build_research_response(
        session=session,
        collection=collection,
        question=q,
        limit=limit,
    )


@router.post(
    "/collections/{collection_id}/research/answer",
    response_model=ResearchGeneratedResponseAPI,
    summary="Generate grounded RAG answer",
)
def api_generate_research_answer(
    collection_id: int,
    payload: ResearchGenerateRequestAPI,
    _csrf: None = Depends(
        require_api_csrf
    ),
    user: User = Depends(
        get_api_user
    ),
    session: Session = Depends(
        get_db_session
    ),
):
    collection = _get_collection_or_404(
        collection_id=collection_id,
        user=user,
        session=session,
    )

    research = build_research_response(
        session=session,
        collection=collection,
        question=payload.question,
        limit=payload.limit,
    )

    return generate_grounded_answer(
        research=research,
        max_new_tokens=(
            payload.max_new_tokens
        ),
        response_language=(
            payload.response_language
        ),
    )
