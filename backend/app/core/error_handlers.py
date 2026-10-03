import logging

from fastapi import FastAPI, Request
from fastapi.responses import (
    JSONResponse,
    PlainTextResponse,
)
from starlette.exceptions import (
    HTTPException as StarletteHTTPException,
)

from app.core.templates import templates


logger = logging.getLogger(__name__)


def is_api_request(
    request: Request,
) -> bool:
    return request.url.path.startswith(
        "/api/"
    )


def is_static_request(
    request: Request,
) -> bool:
    return request.url.path.startswith(
        "/static/"
    )


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
):
    if is_api_request(request):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": str(exc.detail),
            },
        )

    if is_static_request(request):
        return PlainTextResponse(
            content="Not Found",
            status_code=exc.status_code,
        )

    if exc.status_code == 404:
        return templates.TemplateResponse(
            request=request,
            name="errors/404.html",
            context={},
            status_code=404,
        )

    if exc.status_code == 403:
        return templates.TemplateResponse(
            request=request,
            name="errors/403.html",
            context={},
            status_code=403,
        )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": str(exc.detail),
        },
    )


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
):
    logger.error(
        "Unhandled application error. "
        "Path: %s",
        request.url.path,
        exc_info=(
            type(exc),
            exc,
            exc.__traceback__,
        ),
    )

    if is_api_request(request):
        return JSONResponse(
            status_code=500,
            content={
                "detail": (
                    "Internal server error."
                ),
            },
        )

    return templates.TemplateResponse(
        request=request,
        name="errors/500.html",
        context={},
        status_code=500,
    )


def register_error_handlers(
    app: FastAPI,
) -> None:
    app.add_exception_handler(
        StarletteHTTPException,
        http_exception_handler,
    )

    app.add_exception_handler(
        Exception,
        unhandled_exception_handler,
    )