from typing import Literal

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.modeli.collection import Collection
from app.modeli.user import User
from app.repositories.collection_repository import (
    add_collection,
    get_collection_by_id_and_user_id,
    get_collections_by_user_id,
)
from app.schemas.collection import CollectionCreate


CollectionSortField = Literal[
    "created_at",
    "updated_at",
    "name",
]

CollectionSortOrder = Literal[
    "asc",
    "desc",
]


def create_collection(
    session: Session,
    user: User,
    collection_data: CollectionCreate,
) -> Collection:
    collection = Collection(
        user_id=user.id,
        name=collection_data.name,
        description=collection_data.description,
    )

    try:
        add_collection(
            session=session,
            collection=collection,
        )

        session.commit()

        return collection

    except SQLAlchemyError:
        session.rollback()
        raise


def get_user_collections(
    session: Session,
    user: User,
    query_text: str | None = None,
    sort_by: CollectionSortField = "created_at",
    sort_order: CollectionSortOrder = "desc",
) -> list[Collection]:
    return get_collections_by_user_id(
        session=session,
        user_id=user.id,
        query_text=query_text,
        sort_by=sort_by,
        sort_order=sort_order,
    )


def get_user_collection(
    session: Session,
    user: User,
    collection_id: int,
) -> Collection | None:
    return get_collection_by_id_and_user_id(
        session=session,
        collection_id=collection_id,
        user_id=user.id,
    )