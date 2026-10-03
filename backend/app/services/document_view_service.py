from pathlib import Path

from sqlalchemy.orm import Session

from app.bezpeka.faily import UPLOAD_ROOT
from app.modeli.collection import Collection
from app.modeli.document import Document
from app.modeli.user import User
from app.repositories.document_repository import (
    get_document_by_id_and_collection_id,
)
from app.services.collection_service import (
    get_user_collection,
)


class DocumentStorageError(Exception):
    pass


def get_owned_document(
    session: Session,
    user: User,
    collection_id: int,
    document_id: int,
) -> tuple[
    Collection | None,
    Document | None,
]:
    collection = get_user_collection(
        session=session,
        user=user,
        collection_id=collection_id,
    )

    if collection is None:
        return (
            None,
            None,
        )

    document = (
        get_document_by_id_and_collection_id(
            session=session,
            document_id=document_id,
            collection_id=collection.id,
        )
    )

    return (
        collection,
        document,
    )


def get_document_file_path(
    document: Document,
) -> Path:
    upload_root = (
        UPLOAD_ROOT.resolve()
    )

    file_path = (
        UPLOAD_ROOT
        / document.storage_path
    ).resolve()

    if not file_path.is_relative_to(
        upload_root
    ):
        raise DocumentStorageError(
            "Некоректний шлях до файла."
        )

    if not file_path.is_file():
        raise DocumentStorageError(
            "Файл відсутній у сховищі."
        )

    return file_path