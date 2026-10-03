import logging
import shutil
from pathlib import Path

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.bezpeka.faily import UPLOAD_ROOT
from app.modeli.collection import Collection
from app.modeli.user import User
from app.repositories.collection_repository import (
    delete_collection_record,
    update_collection_record,
)
from app.schemas.collection import (
    CollectionUpdate,
)


logger = logging.getLogger(__name__)


def update_user_collection(
    session: Session,
    collection: Collection,
    collection_data: CollectionUpdate,
) -> Collection:
    try:
        updated_collection = (
            update_collection_record(
                session=session,
                collection=collection,
                name=collection_data.name,
                description=(
                    collection_data.description
                ),
            )
        )

        session.commit()

        return updated_collection

    except SQLAlchemyError:
        session.rollback()
        raise


def delete_user_collection(
    session: Session,
    user: User,
    collection: Collection,
) -> None:
    collection_id = collection.id
    user_id = user.id

    try:
        delete_collection_record(
            session=session,
            collection=collection,
        )

        session.commit()

    except SQLAlchemyError:
        session.rollback()
        raise

    collection_storage = (
        UPLOAD_ROOT
        / Path(str(user_id))
        / Path(str(collection_id))
    )

    try:
        if collection_storage.exists():
            shutil.rmtree(
                collection_storage
            )

    except OSError:
        logger.exception(
            "Collection was deleted from "
            "the database, but its storage "
            "directory could not be removed."
        )