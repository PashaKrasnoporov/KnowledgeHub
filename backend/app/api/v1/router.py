from fastapi import APIRouter

from app.api.v1 import (
    admin,
    auth,
    collections,
    documents,
    health,
    search,
    users,
)


api_router = APIRouter(
    prefix="/api/v1",
    tags=["API v1"],
)


api_router.include_router(
    health.router
)

api_router.include_router(
    auth.router
)

api_router.include_router(
    users.router
)

api_router.include_router(
    admin.router
)

api_router.include_router(
    collections.router
)

api_router.include_router(
    documents.router
)

api_router.include_router(
    search.router
)
