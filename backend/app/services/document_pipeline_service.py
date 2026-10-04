import logging

from docx import Document as DocxDocument
from pypdf import PdfReader

from app.baza_danykh.sesii import FabrykaSesii
from app.modeli.document import Document
from app.nalashtuvannia.parametry import (
    parametry,
)
from app.services.document_index_service import (
    index_document_embeddings,
)
from app.services.document_view_service import (
    DocumentStorageError,
    get_document_file_path,
)


logger = logging.getLogger(__name__)


def extract_txt_text(
    file_path,
) -> str:
    raw = file_path.read_bytes()

    for encoding in (
        "utf-8-sig",
        "utf-8",
        "cp1251",
    ):
        try:
            return raw.decode(
                encoding
            )

        except UnicodeDecodeError:
            continue

    raise ValueError(
        "Не вдалося визначити "
        "кодування TXT-файла."
    )


def extract_docx_text(
    file_path,
) -> str:
    document = DocxDocument(
        file_path
    )

    paragraphs = [
        paragraph.text
        for paragraph
        in document.paragraphs
        if paragraph.text.strip()
    ]

    return "\n".join(
        paragraphs
    )


def extract_pdf_text(
    file_path,
) -> str:
    reader = PdfReader(
        str(file_path)
    )

    pages: list[str] = []

    for page in reader.pages:
        text = (
            page.extract_text()
            or ""
        ).strip()

        if text:
            pages.append(
                text
            )

    return "\n\n".join(
        pages
    )


def extract_document_text(
    document: Document,
) -> str:
    file_path = get_document_file_path(
        document=document,
    )

    extension = (
        document.original_name
        .rsplit(
            ".",
            maxsplit=1,
        )[-1]
        .lower()
    )

    if extension == "txt":
        return extract_txt_text(
            file_path
        )

    if extension == "docx":
        return extract_docx_text(
            file_path
        )

    if extension == "pdf":
        return extract_pdf_text(
            file_path
        )

    raise ValueError(
        "Непідтримуваний формат документа."
    )


def process_and_index_document(
    document_id: int,
) -> None:
    session = FabrykaSesii()

    try:
        document = session.get(
            Document,
            document_id,
        )

        if document is None:
            logger.warning(
                "Document ID %s "
                "was not found.",
                document_id,
            )
            return

        try:
            if (
                document.processing_status
                != "ready"
                or not document.extracted_text
            ):
                extracted_text = (
                    extract_document_text(
                        document=document,
                    )
                )

                if not extracted_text.strip():
                    raise ValueError(
                        "Не вдалося отримати "
                        "текст із документа."
                    )

                document.extracted_text = (
                    extracted_text
                )

                document.processing_status = (
                    "ready"
                )

                document.processing_error = None

                session.commit()

                session.refresh(
                    document
                )

            if not parametry.ml_enabled:
                logger.info(
                    "ML indexing is disabled. "
                    "Document ID %s remains available "
                    "for lexical search.",
                    document.id,
                )
                return

            chunk_count = (
                index_document_embeddings(
                    session=session,
                    document=document,
                )
            )

            logger.info(
                "Document ID %s processed. "
                "Chunks: %s",
                document.id,
                chunk_count,
            )

        except (
            DocumentStorageError,
            ValueError,
            OSError,
            Exception,
        ) as exc:
            session.rollback()

            document = session.get(
                Document,
                document_id,
            )

            if document is not None:
                document.processing_status = (
                    "error"
                )

                document.processing_error = (
                    str(exc)[:1000]
                )

                session.commit()

            logger.exception(
                "Document processing failed. "
                "Document ID: %s",
                document_id,
            )

    finally:
        session.close()