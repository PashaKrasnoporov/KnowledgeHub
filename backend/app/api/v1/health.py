from fastapi import APIRouter

from app.schemas.api import (
    HealthAPIResponse,
)


router = APIRouter()


@router.get(
    "/health",
    response_model=HealthAPIResponse,
    summary="API health check",
)
def api_health():
    return HealthAPIResponse(
        status="ok",
        service="KnowledgeHub",
        api_version="v1",
    )
