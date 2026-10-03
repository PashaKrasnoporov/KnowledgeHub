import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.modeli.document import Document
from app.repositories.document_repository import (
    delete_document_record,
)
from app.services.document_view_service import (
    DocumentStorageError,
    get_document_file_path,
)


logger = logging.getLogger(__name__)


def delete_document(
    session: Session,
    document: Document,
) -> None:
    file_path = None

    try:
        file_path = get_document_file_path(
            document=document,
        )

    except DocumentStorageError:
        logger.warning(
            "Document file was not found "
            "before database deletion. "
            "Document ID: %s",
            document.id,
        )

    try:
        delete_document_record(
            session=session,
            document=document,
        )

        session.commit()

    except SQLAlchemyError:
        session.rollback()
        raise

    if file_path is not None:
        try:
            file_path.unlink(
                missing_ok=True
            )

        except OSError:
            logger.exception(
                "Document record was deleted, "
                "but physical file could not "
                "be removed. Document ID: %s",
                document.id,
            )