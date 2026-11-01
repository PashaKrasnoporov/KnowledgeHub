from sqlalchemy import select

from app.baza_danykh.sesii import (
    FabrykaSesii,
)
from app.modeli.document import Document
from app.modeli.document_chunk import (
    DocumentChunk,
)
from app.nalashtuvannia.parametry import (
    parametry,
)
from app.services.document_index_service import (
    index_document_embeddings,
)


def main() -> None:
    if not parametry.ml_enabled:
        print(
            "Embedding backfill: SKIPPED "
            "(ML_ENABLED=false)"
        )
        return

    session = FabrykaSesii()

    try:
        indexed_document_ids = set(
            session.scalars(
                select(
                    DocumentChunk.document_id
                ).distinct()
            ).all()
        )

        documents = list(
            session.scalars(
                select(
                    Document
                )
                .where(
                    Document.processing_status
                    == "ready"
                )
                .where(
                    Document.extracted_text
                    .is_not(None)
                )
                .order_by(
                    Document.id.asc()
                )
            ).all()
        )

        pending = [
            document
            for document in documents
            if (
                document.id
                not in indexed_document_ids
                and (
                    document.extracted_text
                    or ""
                ).strip()
            )
        ]

        if not pending:
            print(
                "Embedding backfill: UP TO DATE"
            )
            return

        print(
            "Embedding backfill: "
            f"{len(pending)} document(s)"
        )

        indexed = 0

        for document in pending:
            print(
                "Indexing document "
                f"{document.id}: "
                f"{document.original_name}"
            )

            chunk_count = (
                index_document_embeddings(
                    session=session,
                    document=document,
                )
            )

            indexed += 1

            print(
                f"  chunks: {chunk_count}"
            )

        print(
            "Embedding backfill: PASS "
            f"({indexed} document(s))"
        )

    finally:
        session.close()


if __name__ == "__main__":
    main()
