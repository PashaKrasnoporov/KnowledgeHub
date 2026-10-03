from app.api.v1.router import api_router
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.error_handlers import (
    register_error_handlers,
)
from app.routes import (
    admin,
    auth,
    collection_manage,
    collections,
    documents,
    pages,
)


app = FastAPI(
    title="KnowledgeHub",
    description=(
        "Platform for organizing and "
        "working with document collections."
    ),
    version="0.1.0",
)


register_error_handlers(
    app
)


app.mount(
    "/static",
    StaticFiles(
        directory="app/static"
    ),
    name="static",
)


app.include_router(
    pages.router
)

app.include_router(
    auth.router
)

app.include_router(
    admin.router
)

app.include_router(
    collections.router
)

app.include_router(
    collection_manage.router
)

app.include_router(
    documents.router
)

app.include_router(
    api_router
)
