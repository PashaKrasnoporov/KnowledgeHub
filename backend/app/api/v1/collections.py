from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_api_user,
    require_api_csrf,
)
from app.baza_danykh.dependencies import (
    get_db_session,
)
from app.modeli.collection import Collection
from app.modeli.user import User
from app.repositories.document_repository import (
    get_documents_by_collection_id,
)
from app.schemas.api import (
    CollectionAPIResponse,
    CollectionCreateAPI,
    CollectionUpdateAPI,
    DocumentAPIResponse,
)
from app.services.collection_manage_service import (
    delete_user_collection,
)
from app.services.collection_service import (
    get_user_collection,
    get_user_collections,
)


router = APIRouter()


@router.get(
    "/collections",
    response_model=list[
        CollectionAPIResponse
    ],
    summary="List user collections",
)
def api_list_collections(
    user: User = Depends(
        get_api_user
    ),
    session: Session = Depends(
        get_db_session
    ),
):
    return get_user_collections(
        session=session,
        user=user,
    )


@router.post(
    "/collections",
    response_model=CollectionAPIResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create collection",
    dependencies=[
        Depends(require_api_csrf)
    ],
)
def api_create_collection(
    payload: CollectionCreateAPI,
    user: User = Depends(
        get_api_user
    ),
    session: Session = Depends(
        get_db_session
    ),
):
    collection = Collection(
        user_id=user.id,
        name=payload.name,
        description=payload.description,
    )

    try:
        session.add(
            collection
        )

        session.commit()

        session.refresh(
            collection
        )

        return collection

    except SQLAlchemyError as exc:
        session.rollback()

        raise HTTPException(
            status_code=500,
            detail="Database error.",
        ) from exc


@router.get(
    "/collections/{collection_id}",
    response_model=CollectionAPIResponse,
    summary="Get collection",
)
def api_get_collection(
    collection_id: int,
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

    return collection


@router.patch(
    "/collections/{collection_id}",
    response_model=CollectionAPIResponse,
    summary="Update collection",
    dependencies=[
        Depends(require_api_csrf)
    ],
)
def api_update_collection(
    collection_id: int,
    payload: CollectionUpdateAPI,
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

    update_data = payload.model_dump(
        exclude_unset=True
    )

    if "name" in update_data:
        collection.name = (
            update_data["name"]
        )

    if "description" in update_data:
        collection.description = (
            update_data["description"]
        )

    try:
        session.commit()

        session.refresh(
            collection
        )

        return collection

    except SQLAlchemyError as exc:
        session.rollback()

        raise HTTPException(
            status_code=500,
            detail="Database error.",
        ) from exc


@router.delete(
    "/collections/{collection_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete collection",
    dependencies=[
        Depends(require_api_csrf)
    ],
)
def api_delete_collection(
    collection_id: int,
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

    try:
        delete_user_collection(
            session=session,
            user=user,
            collection=collection,
        )

    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=500,
            detail="Database error.",
        ) from exc

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )


@router.get(
    "/collections/{collection_id}/documents",
    response_model=list[
        DocumentAPIResponse
    ],
    summary="List collection documents",
)
def api_list_documents(
    collection_id: int,
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

    return get_documents_by_collection_id(
        session=session,
        collection_id=collection.id,
    )
