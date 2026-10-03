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
from app.schemas.research import (
    ResearchResponseAPI,
)
from app.services.collection_service import (
    get_user_collection,
)
from app.services.research_context_service import (
    build_research_response,
)


router = APIRouter()


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

    return build_research_response(
        session=session,
        collection=collection,
        question=q,
        limit=limit,
    )
