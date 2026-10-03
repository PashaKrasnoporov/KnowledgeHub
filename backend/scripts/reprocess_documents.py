from pathlib import Path

from sqlalchemy import select

from app.baza_danykh.sesii import FabrykaSesii
from app.bezpeka.faily import UPLOAD_ROOT

# Ці моделі потрібно імпортувати,
# щоб SQLAlchemy знав усю пов'язану структуру таблиць.
from app.modeli.user import User
from app.modeli.collection import Collection
from app.modeli.document import Document

from app.parsers.document_text import (
    DocumentTextExtractionError,
    extract_document_text,
)


def main() -> None:
    session = FabrykaSesii()

    try:
        documents = session.scalars(
            select(Document).order_by(
                Document.id
            )
        ).all()

        if not documents:
            print(
                "Документів для обробки немає."
            )
            return

        for document in documents:
            file_path = (
                UPLOAD_ROOT
                / document.storage_path
            )

            print(
                f"\nID {document.id}: "
                f"{document.original_name}"
            )

            if not file_path.exists():
                document.processing_status = (
                    "error"
                )

                document.processing_error = (
                    "Файл відсутній у сховищі."
                )

                document.extracted_text = None

                print(
                    "ERROR: файл не знайдено."
                )

                continue

            extension = Path(
                document.original_name
            ).suffix.lower()

            try:
                text = extract_document_text(
                    file_path=file_path,
                    extension=extension,
                )

                document.extracted_text = text

                document.processing_status = (
                    "ready"
                )

                document.processing_error = None

                print(
                    "READY"
                )

                print(
                    "Text chars:",
                    len(text),
                )

            except DocumentTextExtractionError as exc:
                document.extracted_text = None

                document.processing_status = (
                    "error"
                )

                document.processing_error = (
                    str(exc)[:500]
                )

                print(
                    "ERROR:",
                    exc,
                )

        session.commit()

        print(
            "\nОбробку документів завершено."
        )

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


if __name__ == "__main__":
    main()