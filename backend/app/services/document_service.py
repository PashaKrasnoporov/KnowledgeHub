from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.bezpeka.faily import (
    ALLOWED_FILE_TYPES,
    FILE_CHUNK_SIZE,
    MAX_FILE_SIZE,
    UPLOAD_ROOT,
    DocumentTooLargeError,
    InvalidDocumentError,
    validate_file_header,
)
from app.modeli.collection import Collection
from app.modeli.document import Document
from app.modeli.user import User
from app.parsers.document_text import (
    DocumentTextExtractionError,
    extract_document_text,
)
from app.repositories.document_repository import (
    add_document,
    get_documents_by_collection_id,
    search_documents_in_collection,
)
from app.schemas.search import (
    DocumentSearchResult,
)


def save_document(
    session: Session,
    user: User,
    collection: Collection,
    uploaded_file: UploadFile,
) -> Document:
    if not uploaded_file.filename:
        raise InvalidDocumentError(
            "Не вдалося визначити назву файла."
        )

    original_name = Path(
        uploaded_file.filename
    ).name

    if not original_name:
        raise InvalidDocumentError(
            "Некоректна назва файла."
        )

    if len(original_name) > 255:
        raise InvalidDocumentError(
            "Назва файла занадто довга."
        )

    extension = Path(
        original_name
    ).suffix.lower()

    if extension not in ALLOWED_FILE_TYPES:
        raise InvalidDocumentError(
            "Дозволені лише PDF, DOCX та TXT файли."
        )

    mime_type = (
        uploaded_file.content_type
        or ""
    ).split(
        ";"
    )[0].strip().lower()

    if (
        mime_type
        not in ALLOWED_FILE_TYPES[
            extension
        ]
    ):
        raise InvalidDocumentError(
            "Тип файла не відповідає його розширенню."
        )

    stored_name = (
        f"{uuid4().hex}{extension}"
    )

    relative_directory = (
        Path(str(user.id))
        / str(collection.id)
    )

    relative_path = (
        relative_directory
        / stored_name
    )

    target_directory = (
        UPLOAD_ROOT
        / relative_directory
    )

    target_path = (
        UPLOAD_ROOT
        / relative_path
    )

    target_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    size_bytes = 0
    first_chunk = True

    try:
        with target_path.open(
            "wb"
        ) as destination:

            while True:
                chunk = (
                    uploaded_file.file.read(
                        FILE_CHUNK_SIZE
                    )
                )

                if not chunk:
                    break

                if first_chunk:
                    validate_file_header(
                        extension=extension,
                        first_chunk=chunk,
                    )

                    first_chunk = False

                size_bytes += len(
                    chunk
                )

                if size_bytes > MAX_FILE_SIZE:
                    raise DocumentTooLargeError(
                        "Максимальний розмір файла — 10 МБ."
                    )

                destination.write(
                    chunk
                )

        if size_bytes == 0:
            raise InvalidDocumentError(
                "Файл порожній."
            )

        extracted_text: str | None = None
        processing_status = "ready"
        processing_error: str | None = None

        try:
            extracted_text = (
                extract_document_text(
                    file_path=target_path,
                    extension=extension,
                )
            )

        except DocumentTextExtractionError as exc:
            processing_status = "error"
            processing_error = str(exc)[:500]

        document = Document(
            collection_id=collection.id,
            original_name=original_name,
            stored_name=stored_name,
            storage_path=(
                relative_path.as_posix()
            ),
            mime_type=mime_type,
            size_bytes=size_bytes,
            extracted_text=extracted_text,
            processing_status=(
                processing_status
            ),
            processing_error=(
                processing_error
            ),
        )

        add_document(
            session=session,
            document=document,
        )

        session.commit()

        return document

    except (
        InvalidDocumentError,
        DocumentTooLargeError,
    ):
        session.rollback()

        target_path.unlink(
            missing_ok=True
        )

        raise

    except SQLAlchemyError:
        session.rollback()

        target_path.unlink(
            missing_ok=True
        )

        raise

    except Exception:
        session.rollback()

        target_path.unlink(
            missing_ok=True
        )

        raise

    finally:
        uploaded_file.file.close()


def get_collection_documents(
    session: Session,
    collection: Collection,
) -> list[Document]:
    return get_documents_by_collection_id(
        session=session,
        collection_id=collection.id,
    )


def search_collection_documents(
    session: Session,
    collection: Collection,
    search_text: str,
) -> list[DocumentSearchResult]:
    normalized_search_text = (
        " ".join(
            search_text.strip().split()
        )
    )

    if not normalized_search_text:
        return []

    rows = search_documents_in_collection(
        session=session,
        collection_id=collection.id,
        search_text=normalized_search_text,
    )

    return [
        DocumentSearchResult(
            document=document,
            score=score,
        )
        for document, score in rows
    ]