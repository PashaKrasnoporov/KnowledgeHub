from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modeli.collection import Collection


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
) -> list[Collection]:
    query = (
        select(Collection)
        .where(
            Collection.user_id == user_id
        )
        .order_by(
            Collection.created_at.desc()
        )
    )

    return list(
        session.scalars(query).all()
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