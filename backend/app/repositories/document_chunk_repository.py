from sqlalchemy import (
    delete,
    select,
)
from sqlalchemy.orm import Session

from app.modeli.document import Document
from app.modeli.document_chunk import (
    DocumentChunk,
)


def delete_document_chunks(
    session: Session,
    document_id: int,
) -> None:
    query = delete(
        DocumentChunk
    ).where(
        DocumentChunk.document_id
        == document_id
    )

    session.execute(
        query
    )


def add_document_chunks(
    session: Session,
    chunks: list[DocumentChunk],
) -> None:
    session.add_all(
        chunks
    )

    session.flush()


def get_collection_chunks(
    session: Session,
    collection_id: int,
) -> list[
    tuple[
        DocumentChunk,
        Document,
    ]
]:
    query = (
        select(
            DocumentChunk,
            Document,
        )
        .join(
            Document,
            Document.id
            == DocumentChunk.document_id,
        )
        .where(
            Document.collection_id
            == collection_id
        )
        .where(
            Document.processing_status
            == "ready"
        )
        .order_by(
            DocumentChunk.document_id,
            DocumentChunk.chunk_index,
        )
    )

    return list(
        session.execute(
            query
        ).all()
    )