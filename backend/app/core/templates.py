from fastapi import Request
from fastapi.templating import Jinja2Templates

from app.baza_danykh.sesii import FabrykaSesii
from app.bezpeka.sesii import SESSION_COOKIE_NAME
from app.services.session_service import (
    get_user_by_session_token,
)


def template_context(
    request: Request,
) -> dict:
    session_token = request.cookies.get(
        SESSION_COOKIE_NAME
    )

    if not session_token:
        return {
            "current_user": None,
        }

    session = FabrykaSesii()

    try:
        current_user = (
            get_user_by_session_token(
                session=session,
                session_token=session_token,
            )
        )

        return {
            "current_user": current_user,
        }

    finally:
        session.close()


templates = Jinja2Templates(
    directory="app/templates",
    context_processors=[
        template_context,
    ],
)