import logging

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    Response,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_api_user,
    require_api_csrf,
)
from app.baza_danykh.dependencies import (
    get_db_session,
)
from app.bezpeka.faily import (
    DocumentTooLargeError,
    InvalidDocumentError,
)
from app.modeli.user import User
from app.nalashtuvannia.parametry import (
    parametry,
)
from app.schemas.api import (
    DocumentAPIResponse,
)
from app.schemas.document_api import (
    DocumentDetailAPIResponse,
)
from app.services.collection_service import (
    get_user_collection,
)
from app.services.document_manage_service import (
    delete_document,
)
from app.services.document_pipeline_service import (
    process_and_index_document,
)
from app.services.document_service import (
    DuplicateDocumentError,
    save_document,
)
from app.services.document_view_service import (
    DocumentStorageError,
    get_document_file_path,
    get_owned_document,
)


router = APIRouter()

logger = logging.getLogger(__name__)


@router.post(
    "/collections/{collection_id}/documents",
    response_model=DocumentAPIResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload document",
    dependencies=[
        Depends(require_api_csrf)
    ],
)
def api_upload_document(
    collection_id: int,
    background_tasks: BackgroundTasks,
    document_file: UploadFile = File(...),
    user: User = Depends(
        get_api_user
    ),
    session: Session = Depends(
        get_db_session
    ),
):
    collection = get_user_collection(
        session=session,
        user=user,
        collection_id=collection_id,
    )

    if collection is None:
        raise HTTPException(
            status_code=404,
            detail="Collection not found.",
        )

    try:
        document = save_document(
            session=session,
            user=user,
            collection=collection,
            uploaded_file=document_file,
        )

    except DuplicateDocumentError as exc:
        existing = exc.existing_document

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "duplicate_document",
                "message": "Такий самий документ уже існує в цій колекції.",
                "existing_document_id": existing.id,
                "existing_document_name": existing.original_name,
            },
        ) from exc

    except DocumentTooLargeError as exc:
        raise HTTPException(
            status_code=413,
            detail="Document is too large.",
        ) from exc

    except InvalidDocumentError as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid document.",
        ) from exc

    except SQLAlchemyError as exc:
        logger.exception(
            "Database error while "
            "uploading API document."
        )

        raise HTTPException(
            status_code=500,
            detail="Database error.",
        ) from exc

    if document is None:
        raise HTTPException(
            status_code=500,
            detail="Document was not created.",
        )

    if (
        parametry.ml_enabled
        and document.processing_status != "error"
    ):
        try:
            document.processing_status = "processing"
            document.processing_error = None

            session.commit()
            session.refresh(document)

        except SQLAlchemyError as exc:
            session.rollback()

            raise HTTPException(
                status_code=500,
                detail="Database error.",
            ) from exc

        background_tasks.add_task(
            process_and_index_document,
            document.id,
        )

    return document


@router.get(
    "/collections/{collection_id}"
    "/documents/{document_id}",
    response_model=DocumentDetailAPIResponse,
    summary="Get document details",
)
def api_get_document(
    collection_id: int,
    document_id: int,
    user: User = Depends(
        get_api_user
    ),
    session: Session = Depends(
        get_db_session
    ),
):
    collection, document = (
        get_owned_document(
            session=session,
            user=user,
            collection_id=collection_id,
            document_id=document_id,
        )
    )

    if (
        collection is None
        or document is None
    ):
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    return document


@router.get(
    "/collections/{collection_id}"
    "/documents/{document_id}/content",
    summary="Open original document inline",
)
def api_document_content(
    collection_id: int,
    document_id: int,
    user: User = Depends(
        get_api_user
    ),
    session: Session = Depends(
        get_db_session
    ),
):
    collection, document = (
        get_owned_document(
            session=session,
            user=user,
            collection_id=collection_id,
            document_id=document_id,
        )
    )

    if (
        collection is None
        or document is None
    ):
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    try:
        file_path = get_document_file_path(
            document=document
        )

    except DocumentStorageError as exc:
        raise HTTPException(
            status_code=404,
            detail="Document file not found.",
        ) from exc

    return FileResponse(
        path=file_path,
        media_type=document.mime_type,
        filename=document.original_name,
        content_disposition_type="inline",
    )


@router.get(
    "/collections/{collection_id}"
    "/documents/{document_id}/download",
    summary="Download original document",
)
def api_download_document(
    collection_id: int,
    document_id: int,
    user: User = Depends(
        get_api_user
    ),
    session: Session = Depends(
        get_db_session
    ),
):
    collection, document = (
        get_owned_document(
            session=session,
            user=user,
            collection_id=collection_id,
            document_id=document_id,
        )
    )

    if (
        collection is None
        or document is None
    ):
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    try:
        file_path = get_document_file_path(
            document=document
        )

    except DocumentStorageError as exc:
        raise HTTPException(
            status_code=404,
            detail="Document file not found.",
        ) from exc

    return FileResponse(
        path=file_path,
        media_type=document.mime_type,
        filename=document.original_name,
        content_disposition_type="attachment",
    )


@router.delete(
    "/collections/{collection_id}"
    "/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete document",
    dependencies=[
        Depends(require_api_csrf)
    ],
)
def api_delete_document(
    collection_id: int,
    document_id: int,
    user: User = Depends(
        get_api_user
    ),
    session: Session = Depends(
        get_db_session
    ),
):
    collection, document = (
        get_owned_document(
            session=session,
            user=user,
            collection_id=collection_id,
            document_id=document_id,
        )
    )

    if (
        collection is None
        or document is None
    ):
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    try:
        delete_document(
            session=session,
            document=document,
        )

    except SQLAlchemyError as exc:
        logger.exception(
            "Database error while "
            "deleting API document."
        )

        raise HTTPException(
            status_code=500,
            detail="Database error.",
        ) from exc

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )
