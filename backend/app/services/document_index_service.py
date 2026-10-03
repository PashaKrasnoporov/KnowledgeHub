from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.modeli.document import Document
from app.modeli.document_chunk import (
    DocumentChunk,
)
from app.repositories.document_chunk_repository import (
    add_document_chunks,
    delete_document_chunks,
)
from app.services.embedding_service import (
    EMBEDDING_MODEL_NAME,
    create_text_embeddings,
    split_text_into_chunks,
)


def index_document_embeddings(
    session: Session,
    document: Document,
) -> int:
    text = (
        document.extracted_text
        or ""
    ).strip()

    try:
        delete_document_chunks(
            session=session,
            document_id=document.id,
        )

        if not text:
            session.commit()
            return 0

        chunks = split_text_into_chunks(
            text
        )

        if not chunks:
            session.commit()
            return 0

        embeddings = (
            create_text_embeddings(
                chunks
            )
        )

        chunk_models: list[
            DocumentChunk
        ] = []

        for index, (
            chunk_text,
            embedding,
        ) in enumerate(
            zip(
                chunks,
                embeddings,
            )
        ):
            chunk_models.append(
                DocumentChunk(
                    document_id=document.id,
                    chunk_index=index,
                    chunk_text=chunk_text,
                    embedding=(
                        embedding
                        .astype(float)
                        .tolist()
                    ),
                    embedding_model=(
                        EMBEDDING_MODEL_NAME
                    ),
                )
            )

        add_document_chunks(
            session=session,
            chunks=chunk_models,
        )

        session.commit()

        return len(
            chunk_models
        )

    except SQLAlchemyError:
        session.rollback()
        raise