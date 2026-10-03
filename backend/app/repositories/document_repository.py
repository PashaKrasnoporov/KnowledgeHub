from sqlalchemy import (
    func,
    select,
)
from sqlalchemy.orm import Session

from app.modeli.document import Document


def add_document(
    session: Session,
    document: Document,
) -> Document:
    session.add(document)
    session.flush()
    session.refresh(document)

    return document


def get_documents_by_collection_id(
    session: Session,
    collection_id: int,
) -> list[Document]:
    query = (
        select(Document)
        .where(
            Document.collection_id
            == collection_id
        )
        .order_by(
            Document.created_at.desc()
        )
    )

    return list(
        session.scalars(query).all()
    )


def get_document_by_id_and_collection_id(
    session: Session,
    document_id: int,
    collection_id: int,
) -> Document | None:
    query = select(
        Document
    ).where(
        Document.id == document_id,
        Document.collection_id
        == collection_id,
    )

    return session.scalar(query)


def delete_document_record(
    session: Session,
    document: Document,
) -> None:
    session.delete(document)
    session.flush()


def search_documents_in_collection(
    session: Session,
    collection_id: int,
    search_text: str,
) -> list[
    tuple[
        Document,
        float,
    ]
]:
    searchable_text = func.concat(
        Document.original_name,
        " ",
        func.coalesce(
            Document.extracted_text,
            "",
        ),
    )

    search_vector = func.to_tsvector(
        "simple",
        searchable_text,
    )

    search_query = func.plainto_tsquery(
        "simple",
        search_text,
    )

    rank = func.ts_rank_cd(
        search_vector,
        search_query,
    ).label(
        "rank"
    )

    query = (
        select(
            Document,
            rank,
        )
        .where(
            Document.collection_id
            == collection_id
        )
        .where(
            Document.processing_status
            == "ready"
        )
        .where(
            search_vector.op("@@")(
                search_query
            )
        )
        .order_by(
            rank.desc(),
            Document.created_at.desc(),
        )
    )

    rows = session.execute(
        query
    ).all()

    return [
        (
            document,
            float(score or 0.0),
        )
        for document, score in rows
    ]