from fastapi import (
    APIRouter,
    Depends,
    Request,
    Response,
)

from app.api.dependencies import (
    get_api_user,
)
from app.bezpeka.csrf import (
    CSRF_COOKIE_MAX_AGE,
    CSRF_COOKIE_NAME,
    generate_csrf_token,
)
from app.modeli.user import User
from app.schemas.api import (
    CSRFApiResponse,
    UserAPIResponse,
)


router = APIRouter()


@router.get(
    "/me",
    response_model=UserAPIResponse,
    summary="Get current user",
)
def api_current_user(
    user: User = Depends(
        get_api_user
    ),
):
    return user


@router.get(
    "/csrf",
    response_model=CSRFApiResponse,
    summary="Get API CSRF token",
)
def api_csrf_token(
    request: Request,
    response: Response,
    user: User = Depends(
        get_api_user
    ),
):
    csrf_token = request.cookies.get(
        CSRF_COOKIE_NAME
    )

    if not csrf_token:
        csrf_token = generate_csrf_token()

        response.set_cookie(
            key=CSRF_COOKIE_NAME,
            value=csrf_token,
            max_age=CSRF_COOKIE_MAX_AGE,
            httponly=True,
            samesite="strict",
            secure=False,
            path="/",
        )

    return CSRFApiResponse(
        csrf_token=csrf_token
    )
