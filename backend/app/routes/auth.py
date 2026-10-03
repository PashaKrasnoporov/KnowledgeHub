import logging

from fastapi import (
    APIRouter,
    Depends,
    Form,
    Request,
)
from fastapi.responses import RedirectResponse
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.baza_danykh.dependencies import get_db_session
from app.bezpeka.csrf import (
    CSRF_COOKIE_MAX_AGE,
    CSRF_COOKIE_NAME,
    generate_csrf_token,
    validate_csrf_token,
)
from app.bezpeka.sesii import (
    SESSION_COOKIE_NAME,
    SESSION_LIFETIME,
)
from app.core.templates import templates
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
    get_user_by_session_token,
    revoke_session_by_token,
)


router = APIRouter(
    tags=["auth"],
)

logger = logging.getLogger(__name__)


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


def set_session_cookie(
    response,
    session_token: str,
):
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

    return response


def render_register_page(
    request: Request,
    csrf_token: str,
    errors: list[str] | None = None,
    form_data: dict[str, str] | None = None,
    success: bool = False,
    status_code: int = 200,
):
    return templates.TemplateResponse(
        request=request,
        name="auth/register.html",
        context={
            "csrf_token": csrf_token,
            "errors": errors or [],
            "form_data": form_data or {},
            "success": success,
        },
        status_code=status_code,
    )


def render_login_page(
    request: Request,
    csrf_token: str,
    errors: list[str] | None = None,
    form_data: dict[str, str] | None = None,
    status_code: int = 200,
):
    return templates.TemplateResponse(
        request=request,
        name="auth/login.html",
        context={
            "csrf_token": csrf_token,
            "errors": errors or [],
            "form_data": form_data or {},
        },
        status_code=status_code,
    )


@router.get("/register")
def register_page(
    request: Request,
):
    csrf_token = request.cookies.get(
        CSRF_COOKIE_NAME
    )

    if csrf_token is None:
        csrf_token = generate_csrf_token()

        response = render_register_page(
            request=request,
            csrf_token=csrf_token,
        )

        return set_csrf_cookie(
            response=response,
            csrf_token=csrf_token,
        )

    return render_register_page(
        request=request,
        csrf_token=csrf_token,
    )


@router.get("/register/success")
def register_success(
    request: Request,
):
    return render_register_page(
        request=request,
        csrf_token="",
        success=True,
    )


@router.post("/register")
def register_submit(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    password_confirmation: str = Form(...),
    csrf_token: str = Form(...),
    session: Session = Depends(
        get_db_session
    ),
):
    form_data = {
        "name": name,
        "email": email,
    }

    cookie_token = request.cookies.get(
        CSRF_COOKIE_NAME
    )

    if not validate_csrf_token(
        form_token=csrf_token,
        cookie_token=cookie_token,
    ):
        new_csrf_token = generate_csrf_token()

        response = render_register_page(
            request=request,
            csrf_token=new_csrf_token,
            errors=[
                "Не вдалося перевірити безпечність запиту."
            ],
            form_data=form_data,
            status_code=403,
        )

        return set_csrf_cookie(
            response=response,
            csrf_token=new_csrf_token,
        )

    errors: list[str] = []

    if password != password_confirmation:
        errors.append(
            "Паролі не збігаються."
        )

    try:
        user_data = UserCreate(
            name=name,
            email=email,
            password=password,
        )

    except ValidationError as exc:
        user_data = None

        for error in exc.errors():
            field = error["loc"][-1]

            if field == "name":
                errors.append(
                    "Ім'я повинно містити від 2 до 50 символів."
                )

            elif field == "email":
                errors.append(
                    "Введіть коректну електронну адресу."
                )

            elif field == "password":
                errors.append(
                    "Пароль повинен містити від 8 до 128 символів."
                )

            else:
                errors.append(
                    "Перевірте введені дані."
                )

    if errors:
        return render_register_page(
            request=request,
            csrf_token=csrf_token,
            errors=errors,
            form_data=form_data,
            status_code=400,
        )

    try:
        register_user(
            session=session,
            user_data=user_data,
        )

    except EmailAlreadyExistsError:
        return render_register_page(
            request=request,
            csrf_token=csrf_token,
            errors=[
                (
                    "Користувач із такою електронною "
                    "адресою вже зареєстрований."
                )
            ],
            form_data=form_data,
            status_code=409,
        )

    except SQLAlchemyError:
        logger.exception(
            "Database error during registration."
        )

        return render_register_page(
            request=request,
            csrf_token=csrf_token,
            errors=[
                "Виникла внутрішня помилка."
            ],
            form_data=form_data,
            status_code=500,
        )

    return RedirectResponse(
        url="/register/success",
        status_code=303,
    )


@router.get("/login")
def login_page(
    request: Request,
):
    csrf_token = request.cookies.get(
        CSRF_COOKIE_NAME
    )

    if csrf_token is None:
        csrf_token = generate_csrf_token()

        response = render_login_page(
            request=request,
            csrf_token=csrf_token,
        )

        return set_csrf_cookie(
            response=response,
            csrf_token=csrf_token,
        )

    return render_login_page(
        request=request,
        csrf_token=csrf_token,
    )


@router.post("/login")
def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...),
    session: Session = Depends(
        get_db_session
    ),
):
    form_data = {
        "email": email,
    }

    cookie_token = request.cookies.get(
        CSRF_COOKIE_NAME
    )

    if not validate_csrf_token(
        form_token=csrf_token,
        cookie_token=cookie_token,
    ):
        new_csrf_token = generate_csrf_token()

        response = render_login_page(
            request=request,
            csrf_token=new_csrf_token,
            errors=[
                "Не вдалося перевірити безпечність запиту."
            ],
            form_data=form_data,
            status_code=403,
        )

        return set_csrf_cookie(
            response=response,
            csrf_token=new_csrf_token,
        )

    try:
        user_data = UserLogin(
            email=email,
            password=password,
        )

    except ValidationError:
        return render_login_page(
            request=request,
            csrf_token=csrf_token,
            errors=[
                "Неправильний email або пароль."
            ],
            form_data=form_data,
            status_code=400,
        )

    try:
        user = authenticate_user(
            session=session,
            user_data=user_data,
        )

        session_token, _ = create_user_session(
            session=session,
            user=user,
        )

    except (
        InvalidCredentialsError,
        InactiveUserError,
    ):
        return render_login_page(
            request=request,
            csrf_token=csrf_token,
            errors=[
                "Неправильний email або пароль."
            ],
            form_data=form_data,
            status_code=401,
        )

    except SQLAlchemyError:
        logger.exception(
            "Database error during login."
        )

        return render_login_page(
            request=request,
            csrf_token=csrf_token,
            errors=[
                "Виникла внутрішня помилка."
            ],
            form_data=form_data,
            status_code=500,
        )

    response = RedirectResponse(
        url="/profile",
        status_code=303,
    )

    return set_session_cookie(
        response=response,
        session_token=session_token,
    )


@router.get("/profile")
def profile_page(
    request: Request,
    session: Session = Depends(
        get_db_session
    ),
):
    session_token = request.cookies.get(
        SESSION_COOKIE_NAME
    )

    user = get_user_by_session_token(
        session=session,
        session_token=session_token,
    )

    if user is None:
        return RedirectResponse(
            url="/login",
            status_code=303,
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
        name="auth/profile.html",
        context={
            "user": user,
            "csrf_token": csrf_token,
        },
    )

    if new_cookie_needed:
        return set_csrf_cookie(
            response=response,
            csrf_token=csrf_token,
        )

    return response


@router.post("/logout")
def logout_submit(
    request: Request,
    csrf_token: str = Form(...),
    session: Session = Depends(
        get_db_session
    ),
):
    cookie_csrf_token = request.cookies.get(
        CSRF_COOKIE_NAME
    )

    if not validate_csrf_token(
        form_token=csrf_token,
        cookie_token=cookie_csrf_token,
    ):
        return RedirectResponse(
            url="/profile",
            status_code=303,
        )

    session_token = request.cookies.get(
        SESSION_COOKIE_NAME
    )

    try:
        revoke_session_by_token(
            session=session,
            session_token=session_token,
        )

    except SQLAlchemyError:
        logger.exception(
            "Database error during logout."
        )

    response = RedirectResponse(
        url="/login",
        status_code=303,
    )

    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
        path="/",
    )

    return response