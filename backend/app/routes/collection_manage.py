import logging

from fastapi import (
    APIRouter,
    Depends,
    Form,
    Request,
)
from fastapi.responses import (
    RedirectResponse,
)
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.baza_danykh.dependencies import (
    get_db_session,
)
from app.bezpeka.csrf import (
    CSRF_COOKIE_NAME,
    validate_csrf_token,
)
from app.bezpeka.sesii import (
    SESSION_COOKIE_NAME,
)
from app.schemas.collection import (
    CollectionUpdate,
)
from app.services.collection_manage_service import (
    delete_user_collection,
    update_user_collection,
)
from app.services.collection_service import (
    get_user_collection,
)
from app.services.session_service import (
    get_user_by_session_token,
)


router = APIRouter(
    tags=["collection-management"],
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


@router.post(
    "/collections/{collection_id}/edit"
)
def edit_collection(
    collection_id: int,
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
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

    cookie_csrf_token = request.cookies.get(
        CSRF_COOKIE_NAME
    )

    if not validate_csrf_token(
        form_token=csrf_token,
        cookie_token=cookie_csrf_token,
    ):
        return RedirectResponse(
            url=(
                f"/collections/"
                f"{collection_id}"
                "?manage_error=csrf"
            ),
            status_code=303,
        )

    try:
        collection_data = CollectionUpdate(
            name=name,
            description=description,
        )

    except ValidationError:
        return RedirectResponse(
            url=(
                f"/collections/"
                f"{collection_id}"
                "?manage_error=validation"
            ),
            status_code=303,
        )

    try:
        update_user_collection(
            session=session,
            collection=collection,
            collection_data=collection_data,
        )

    except SQLAlchemyError:
        logger.exception(
            "Database error while "
            "updating collection."
        )

        return RedirectResponse(
            url=(
                f"/collections/"
                f"{collection_id}"
                "?manage_error=server"
            ),
            status_code=303,
        )

    return RedirectResponse(
        url=(
            f"/collections/"
            f"{collection_id}"
            "?updated=1"
        ),
        status_code=303,
    )


@router.post(
    "/collections/{collection_id}/delete"
)
def delete_collection(
    collection_id: int,
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

    cookie_csrf_token = request.cookies.get(
        CSRF_COOKIE_NAME
    )

    if not validate_csrf_token(
        form_token=csrf_token,
        cookie_token=cookie_csrf_token,
    ):
        return RedirectResponse(
            url=(
                f"/collections/"
                f"{collection_id}"
                "?manage_error=csrf"
            ),
            status_code=303,
        )

    try:
        delete_user_collection(
            session=session,
            user=user,
            collection=collection,
        )

    except SQLAlchemyError:
        logger.exception(
            "Database error while "
            "deleting collection."
        )

        return RedirectResponse(
            url=(
                f"/collections/"
                f"{collection_id}"
                "?manage_error=server"
            ),
            status_code=303,
        )

    return RedirectResponse(
        url="/collections?deleted=1",
        status_code=303,
    )