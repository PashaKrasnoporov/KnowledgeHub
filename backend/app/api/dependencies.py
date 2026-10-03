from fastapi import (
    Depends,
    Header,
    HTTPException,
    Request,
    status,
)
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
from app.modeli.user import User
from app.services.session_service import (
    get_user_by_session_token,
)


def get_api_user(
    request: Request,
    session: Session = Depends(
        get_db_session
    ),
) -> User:
    session_token = request.cookies.get(
        SESSION_COOKIE_NAME
    )

    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    user = get_user_by_session_token(
        session=session,
        session_token=session_token,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive.",
        )

    return user


def get_api_admin(
    user: User = Depends(
        get_api_user
    ),
) -> User:
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required.",
        )

    return user


def require_api_csrf(
    request: Request,
    x_csrf_token: str | None = Header(
        default=None,
        alias="X-CSRF-Token",
    ),
) -> None:
    cookie_token = request.cookies.get(
        CSRF_COOKIE_NAME
    )

    if (
        not x_csrf_token
        or not validate_csrf_token(
            form_token=x_csrf_token,
            cookie_token=cookie_token,
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid CSRF token.",
        )
