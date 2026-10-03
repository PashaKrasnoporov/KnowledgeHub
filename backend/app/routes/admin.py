import logging

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Request,
)
from fastapi.responses import RedirectResponse
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
from app.bezpeka.sesii import (
    SESSION_COOKIE_NAME,
)
from app.core.templates import templates
from app.repositories.admin_repository import (
    get_all_users,
)
from app.services.admin_service import (
    AdminActionError,
    change_user_active_status,
)
from app.services.session_service import (
    get_user_by_session_token,
)


router = APIRouter(
    prefix="/admin",
    tags=["admin"],
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


def require_admin(
    request: Request,
    session: Session,
):
    user = get_current_user(
        request=request,
        session=session,
    )

    if user is None:
        return None

    if user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Administrator access required.",
        )

    return user


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


@router.get("")
def admin_page(
    request: Request,
    message: str | None = None,
    error: str | None = None,
    session: Session = Depends(
        get_db_session
    ),
):
    admin_user = require_admin(
        request=request,
        session=session,
    )

    if admin_user is None:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    users = get_all_users(
        session=session,
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
        name="admin/index.html",
        context={
            "admin_user": admin_user,
            "users": users,
            "csrf_token": csrf_token,
            "message": message,
            "error": error,
        },
    )

    if new_cookie_needed:
        return set_csrf_cookie(
            response=response,
            csrf_token=csrf_token,
        )

    return response


@router.post(
    "/users/{user_id}/status"
)
def change_user_status(
    user_id: int,
    request: Request,
    action: str = Form(...),
    csrf_token: str = Form(...),
    session: Session = Depends(
        get_db_session
    ),
):
    admin_user = require_admin(
        request=request,
        session=session,
    )

    if admin_user is None:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    cookie_token = request.cookies.get(
        CSRF_COOKIE_NAME
    )

    if not validate_csrf_token(
        form_token=csrf_token,
        cookie_token=cookie_token,
    ):
        raise HTTPException(
            status_code=403,
            detail="Invalid CSRF token.",
        )

    if action == "activate":
        new_status = True

    elif action == "deactivate":
        new_status = False

    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid admin action.",
        )

    try:
        user = change_user_active_status(
            session=session,
            admin_user=admin_user,
            target_user_id=user_id,
            is_active=new_status,
        )

    except AdminActionError:
        return RedirectResponse(
            url="/admin?error=self_deactivate",
            status_code=303,
        )

    except SQLAlchemyError:
        logger.exception(
            "Database error during "
            "admin user management."
        )

        return RedirectResponse(
            url="/admin?error=server",
            status_code=303,
        )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    return RedirectResponse(
        url="/admin?message=updated",
        status_code=303,
    )
