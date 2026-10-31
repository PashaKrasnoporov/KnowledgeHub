from typing import Literal

from sqlalchemy import (
    func,
    or_,
    select,
)
from sqlalchemy.orm import Session

from app.modeli.collection import Collection


CollectionSortField = Literal[
    "created_at",
    "updated_at",
    "name",
]

CollectionSortOrder = Literal[
    "asc",
    "desc",
]


def add_collection(
    session: Session,
    collection: Collection,
) -> Collection:
    session.add(
        collection
    )

    session.flush()

    session.refresh(
        collection
    )

    return collection


def get_collections_by_user_id(
    session: Session,
    user_id: int,
    query_text: str | None = None,
    sort_by: CollectionSortField = "created_at",
    sort_order: CollectionSortOrder = "desc",
) -> list[Collection]:
    query = select(
        Collection
    ).where(
        Collection.user_id == user_id
    )

    if query_text:
        normalized_query = (
            query_text.strip()
        )

        if normalized_query:
            search_pattern = (
                f"%{normalized_query}%"
            )

            query = query.where(
                or_(
                    Collection.name.ilike(
                        search_pattern
                    ),
                    Collection.description.ilike(
                        search_pattern
                    ),
                )
            )

    sort_columns = {
        "created_at":
            Collection.created_at,
        "updated_at":
            Collection.updated_at,
        "name":
            func.lower(
                Collection.name
            ),
    }

    sort_column = sort_columns[
        sort_by
    ]

    if sort_order == "asc":
        sort_expression = (
            sort_column.asc()
        )
    else:
        sort_expression = (
            sort_column.desc()
        )

    query = query.order_by(
        sort_expression,
        Collection.id.desc(),
    )

    return list(
        session.scalars(
            query
        ).all()
    )


def get_collection_by_id_and_user_id(
    session: Session,
    collection_id: int,
    user_id: int,
) -> Collection | None:
    query = select(
        Collection
    ).where(
        Collection.id == collection_id,
        Collection.user_id == user_id,
    )

    return session.scalar(
        query
    )


def update_collection_record(
    session: Session,
    collection: Collection,
    name: str,
    description: str | None,
) -> Collection:
    collection.name = name
    collection.description = description

    session.flush()

    session.refresh(
        collection
    )

    return collection


def delete_collection_record(
    session: Session,
    collection: Collection,
) -> None:
    session.delete(
        collection
    )

    session.flush()