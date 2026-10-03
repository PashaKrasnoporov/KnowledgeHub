import logging

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_api_user,
    require_api_csrf,
)
from app.baza_danykh.dependencies import (
    get_db_session,
)
from app.bezpeka.csrf import (
    CSRF_COOKIE_MAX_AGE,
    CSRF_COOKIE_NAME,
    generate_csrf_token,
)
from app.bezpeka.sesii import (
    SESSION_COOKIE_NAME,
    SESSION_LIFETIME,
)
from app.modeli.user import User
from app.schemas.api import (
    CSRFApiResponse,
    UserAPIResponse,
)
from app.schemas.auth_api import (
    LoginAPIRequest,
    MessageAPIResponse,
    RegisterAPIRequest,
)
from app.schemas.user import (
    UserCreate,
    UserLogin,
)
from app.services.auth_service import (
    EmailAlreadyExistsError,
    InactiveUserError,
    InvalidCredentialsError,
    authenticate_user,
    register_user,
)
from app.services.session_service import (
    create_user_session,
    revoke_session_by_token,
)


router = APIRouter(
    prefix="/auth",
    tags=["API auth"],
)

logger = logging.getLogger(__name__)


def set_csrf_cookie(
    response: Response,
    csrf_token: str,
) -> None:
    response.set_cookie(
        key=CSRF_COOKIE_NAME,
        value=csrf_token,
        max_age=CSRF_COOKIE_MAX_AGE,
        httponly=True,
        samesite="strict",
        secure=False,
        path="/",
    )


def set_session_cookie(
    response: Response,
    session_token: str,
) -> None:
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_token,
        max_age=int(
            SESSION_LIFETIME.total_seconds()
        ),
        httponly=True,
        samesite="lax",
        secure=False,
        path="/",
    )


@router.get(
    "/csrf",
    response_model=CSRFApiResponse,
    summary="Get public authentication CSRF token",
)
def api_auth_csrf_token(
    request: Request,
    response: Response,
):
    csrf_token = request.cookies.get(
        CSRF_COOKIE_NAME
    )

    if not csrf_token:
        csrf_token = generate_csrf_token()

        set_csrf_cookie(
            response=response,
            csrf_token=csrf_token,
        )

    return CSRFApiResponse(
        csrf_token=csrf_token
    )


@router.post(
    "/register",
    response_model=MessageAPIResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register user",
    dependencies=[
        Depends(require_api_csrf)
    ],
)
def api_register(
    payload: RegisterAPIRequest,
    session: Session = Depends(
        get_db_session
    ),
):
    if (
        payload.password
        != payload.password_confirmation
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Паролі не збігаються.",
        )

    try:
        user_data = UserCreate(
            name=payload.name,
            email=payload.email,
            password=payload.password,
        )

    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Перевірте введені дані.",
        ) from exc

    try:
        register_user(
            session=session,
            user_data=user_data,
        )

    except EmailAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Користувач із такою електронною "
                "адресою вже зареєстрований."
            ),
        ) from exc

    except SQLAlchemyError as exc:
        logger.exception(
            "Database error during API registration."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Виникла внутрішня помилка.",
        ) from exc

    return MessageAPIResponse(
        message="Обліковий запис успішно створено."
    )


@router.post(
    "/login",
    response_model=UserAPIResponse,
    summary="Log in user",
    dependencies=[
        Depends(require_api_csrf)
    ],
)
def api_login(
    payload: LoginAPIRequest,
    response: Response,
    session: Session = Depends(
        get_db_session
    ),
):
    try:
        user_data = UserLogin(
            email=payload.email,
            password=payload.password,
        )

        user = authenticate_user(
            session=session,
            user_data=user_data,
        )

        session_token, _ = create_user_session(
            session=session,
            user=user,
        )

    except (
        ValidationError,
        InvalidCredentialsError,
        InactiveUserError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильний email або пароль.",
        ) from exc

    except SQLAlchemyError as exc:
        logger.exception(
            "Database error during API login."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Виникла внутрішня помилка.",
        ) from exc

    set_session_cookie(
        response=response,
        session_token=session_token,
    )

    return user


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Log out current user",
    dependencies=[
        Depends(require_api_csrf)
    ],
)
def api_logout(
    request: Request,
    user: User = Depends(
        get_api_user
    ),
    session: Session = Depends(
        get_db_session
    ),
):
    del user

    session_token = request.cookies.get(
        SESSION_COOKIE_NAME
    )

    try:
        revoke_session_by_token(
            session=session,
            session_token=session_token,
        )

    except SQLAlchemyError as exc:
        logger.exception(
            "Database error during API logout."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Виникла внутрішня помилка.",
        ) from exc

    response = Response(
        status_code=status.HTTP_204_NO_CONTENT
    )

    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
        path="/",
    )

    return response
