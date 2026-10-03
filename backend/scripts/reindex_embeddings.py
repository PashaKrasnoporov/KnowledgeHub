from sqlalchemy import select

from app.baza_danykh.sesii import (
    FabrykaSesii,
)
from app.modeli.document import Document
from app.services.document_index_service import (
    index_document_embeddings,
)


def main() -> None:
    session = FabrykaSesii()

    try:
        documents = list(
            session.scalars(
                select(Document)
                .where(
                    Document.processing_status
                    == "ready"
                )
                .where(
                    Document.extracted_text
                    .is_not(None)
                )
                .order_by(
                    Document.id
                )
            ).all()
        )

        print(
            f"Documents: {len(documents)}"
        )

        total_chunks = 0

        for document in documents:
            chunk_count = (
                index_document_embeddings(
                    session=session,
                    document=document,
                )
            )

            total_chunks += chunk_count

            print(
                f"ID {document.id}: "
                f"{document.original_name}"
                f" -> {chunk_count} chunks"
            )

        print(
            ""
        )

        print(
            "INDEXING COMPLETED"
        )

        print(
            f"Total chunks: "
            f"{total_chunks}"
        )

    finally:
        session.close()


if __name__ == "__main__":
    main()