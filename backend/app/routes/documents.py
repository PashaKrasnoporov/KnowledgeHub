import logging

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    Request,
    UploadFile,
)
from fastapi.responses import (
    FileResponse,
    RedirectResponse,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.baza_danykh.dependencies import (
    get_db_session,
)
from app.bezpeka.csrf import (
    CSRF_COOKIE_MAX_AGE,
    CSRF_COOKIE_NAME,
    generate_csrf_token,
    validate_csrf_token,
)
from app.bezpeka.faily import (
    DocumentTooLargeError,
    InvalidDocumentError,
)
from app.bezpeka.sesii import (
    SESSION_COOKIE_NAME,
)
from app.core.templates import templates
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
    save_document,
)
from app.services.document_view_service import (
    DocumentStorageError,
    get_document_file_path,
    get_owned_document,
)
from app.services.session_service import (
    get_user_by_session_token,
)


router = APIRouter(
    tags=["documents"],
)

logger = logging.getLogger(__name__)


def get_current_user(
    request: Request,
    session: Session,
):
    session_token = request.cookies.get(
        SESSION_COOKIE_NAME
    )

    return get_user_by_session_token(
        session=session,
        session_token=session_token,
    )


def set_csrf_cookie(
    response,
    csrf_token: str,
):
    response.set_cookie(
        key=CSRF_COOKIE_NAME,
        value=csrf_token,
        max_age=CSRF_COOKIE_MAX_AGE,
        httponly=True,
        samesite="strict",
        secure=False,
        path="/",
    )

    return response


@router.post(
    "/collections/{collection_id}/documents"
)
def upload_document(
    collection_id: int,
    request: Request,
    background_tasks: BackgroundTasks,
    csrf_token: str = Form(...),
    document_file: UploadFile = File(...),
    session: Session = Depends(
        get_db_session
    ),
):
    user = get_current_user(
        request=request,
        session=session,
    )

    if user is None:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    collection = get_user_collection(
        session=session,
        user=user,
        collection_id=collection_id,
    )

    if collection is None:
        return RedirectResponse(
            url="/collections",
            status_code=303,
        )

    cookie_csrf_token = (
        request.cookies.get(
            CSRF_COOKIE_NAME
        )
    )

    if not validate_csrf_token(
        form_token=csrf_token,
        cookie_token=cookie_csrf_token,
    ):
        return RedirectResponse(
            url=(
                f"/collections/"
                f"{collection_id}"
                "?upload_error=csrf"
            ),
            status_code=303,
        )

    try:
        document = save_document(
            session=session,
            user=user,
            collection=collection,
            uploaded_file=document_file,
        )

        if document is not None:
            background_tasks.add_task(
                process_and_index_document,
                document.id,
            )

        else:
            logger.warning(
                "save_document returned None. "
                "Automatic indexing was skipped."
            )

    except DocumentTooLargeError:
        return RedirectResponse(
            url=(
                f"/collections/"
                f"{collection_id}"
                "?upload_error=too_large"
            ),
            status_code=303,
        )

    except InvalidDocumentError:
        return RedirectResponse(
            url=(
                f"/collections/"
                f"{collection_id}"
                "?upload_error=invalid"
            ),
            status_code=303,
        )

    except SQLAlchemyError:
        logger.exception(
            "Database error while "
            "uploading document."
        )

        return RedirectResponse(
            url=(
                f"/collections/"
                f"{collection_id}"
                "?upload_error=server"
            ),
            status_code=303,
        )

    except Exception:
        logger.exception(
            "Unexpected error while "
            "uploading document."
        )

        return RedirectResponse(
            url=(
                f"/collections/"
                f"{collection_id}"
                "?upload_error=server"
            ),
            status_code=303,
        )

    return RedirectResponse(
        url=(
            f"/collections/"
            f"{collection_id}"
            "?uploaded=1"
        ),
        status_code=303,
    )


@router.get(
    "/collections/{collection_id}"
    "/documents/{document_id}"
)
def document_page(
    collection_id: int,
    document_id: int,
    request: Request,
    session: Session = Depends(
        get_db_session
    ),
):
    user = get_current_user(
        request=request,
        session=session,
    )

    if user is None:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

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
        return RedirectResponse(
            url="/collections",
            status_code=303,
        )

    extension = (
        document.original_name
        .rsplit(
            ".",
            maxsplit=1,
        )[-1]
        .lower()
    )

    csrf_token = request.cookies.get(
        CSRF_COOKIE_NAME
    )

    new_cookie_needed = False

    if csrf_token is None:
        csrf_token = generate_csrf_token()
        new_cookie_needed = True

    response = templates.TemplateResponse(
        request=request,
        name="documents/detail.html",
        context={
            "user": user,
            "collection": collection,
            "document": document,
            "extension": extension,
            "csrf_token": csrf_token,
        },
    )

    if new_cookie_needed:
        return set_csrf_cookie(
            response=response,
            csrf_token=csrf_token,
        )

    return response


@router.get(
    "/collections/{collection_id}"
    "/documents/{document_id}/content"
)
def document_content(
    collection_id: int,
    document_id: int,
    request: Request,
    session: Session = Depends(
        get_db_session
    ),
):
    user = get_current_user(
        request=request,
        session=session,
    )

    if user is None:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

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
        return RedirectResponse(
            url="/collections",
            status_code=303,
        )

    try:
        file_path = get_document_file_path(
            document=document,
        )

    except DocumentStorageError:
        return RedirectResponse(
            url=(
                f"/collections/"
                f"{collection_id}"
                f"/documents/"
                f"{document_id}"
            ),
            status_code=303,
        )

    return FileResponse(
        path=file_path,
        media_type=document.mime_type,
        filename=document.original_name,
        content_disposition_type="inline",
    )


@router.get(
    "/collections/{collection_id}"
    "/documents/{document_id}/download"
)
def download_document(
    collection_id: int,
    document_id: int,
    request: Request,
    session: Session = Depends(
        get_db_session
    ),
):
    user = get_current_user(
        request=request,
        session=session,
    )

    if user is None:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

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
        return RedirectResponse(
            url="/collections",
            status_code=303,
        )

    try:
        file_path = get_document_file_path(
            document=document,
        )

    except DocumentStorageError:
        return RedirectResponse(
            url=(
                f"/collections/"
                f"{collection_id}"
                f"/documents/"
                f"{document_id}"
            ),
            status_code=303,
        )

    return FileResponse(
        path=file_path,
        media_type=document.mime_type,
        filename=document.original_name,
        content_disposition_type="attachment",
    )


@router.post(
    "/collections/{collection_id}"
    "/documents/{document_id}/delete"
)
def delete_document_submit(
    collection_id: int,
    document_id: int,
    request: Request,
    csrf_token: str = Form(...),
    session: Session = Depends(
        get_db_session
    ),
):
    user = get_current_user(
        request=request,
        session=session,
    )

    if user is None:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

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
        return RedirectResponse(
            url="/collections",
            status_code=303,
        )

    cookie_csrf_token = (
        request.cookies.get(
            CSRF_COOKIE_NAME
        )
    )

    if not validate_csrf_token(
        form_token=csrf_token,
        cookie_token=cookie_csrf_token,
    ):
        return RedirectResponse(
            url=(
                f"/collections/"
                f"{collection_id}"
                f"/documents/"
                f"{document_id}"
            ),
            status_code=303,
        )

    try:
        delete_document(
            session=session,
            document=document,
        )

    except SQLAlchemyError:
        logger.exception(
            "Database error while "
            "deleting document."
        )

        return RedirectResponse(
            url=(
                f"/collections/"
                f"{collection_id}"
                f"/documents/"
                f"{document_id}"
            ),
            status_code=303,
        )

    return RedirectResponse(
        url=f"/collections/{collection_id}",
        status_code=303,
    )