from fastapi import APIRouter

from app.schemas.api import HealthAPIResponse
from app.version import APP_VERSION


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
        app_version=APP_VERSION,
    )
