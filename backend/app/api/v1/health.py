import tempfile

from fastapi import (
    APIRouter,
    Response,
    status,
)
from sqlalchemy import text

from app.baza_danykh.sesii import FabrykaSesii
from app.bezpeka.faily import UPLOAD_ROOT
from app.nalashtuvannia.parametry import parametry
from app.schemas.api import (
    HealthAPIResponse,
    ReadinessAPIResponse,
    ReadinessChecksAPIResponse,
)
from app.version import APP_VERSION


router = APIRouter()


def _health_response() -> HealthAPIResponse:
    return HealthAPIResponse(
        status="ok",
        service="KnowledgeHub",
        api_version="v1",
        app_version=APP_VERSION,
    )


@router.get(
    "/health",
    response_model=HealthAPIResponse,
    summary="API health check",
)
def api_health():
    return _health_response()


@router.get(
    "/health/live",
    response_model=HealthAPIResponse,
    summary="Application liveness check",
)
def api_liveness():
    return _health_response()


@router.get(
    "/health/ready",
    response_model=ReadinessAPIResponse,
    summary="Application readiness check",
)
def api_readiness(
    response: Response,
):
    database_status = "ok"
    storage_status = "ok"

    try:
        with FabrykaSesii() as session:
            session.execute(
                text("SELECT 1")
            )
    except Exception:
        database_status = "error"

    try:
        UPLOAD_ROOT.mkdir(
            parents=True,
            exist_ok=True,
        )

        with tempfile.NamedTemporaryFile(
            mode="wb",
            prefix=".knowledgehub-readiness-",
            dir=UPLOAD_ROOT,
            delete=True,
        ) as probe:
            probe.write(b"ok")
            probe.flush()
    except Exception:
        storage_status = "error"

    ready = (
        database_status == "ok"
        and storage_status == "ok"
    )

    if not ready:
        response.status_code = (
            status.HTTP_503_SERVICE_UNAVAILABLE
        )

    return ReadinessAPIResponse(
        status=(
            "ready"
            if ready
            else "not_ready"
        ),
        service="KnowledgeHub",
        api_version="v1",
        app_version=APP_VERSION,
        deployment_profile=(
            parametry.deployment_profile
        ),
        checks=ReadinessChecksAPIResponse(
            database=database_status,
            storage=storage_status,
        ),
    )
