from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.security_headers import SecurityHeadersMiddleware


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)

FRONTEND_CANDIDATES = (
    PROJECT_ROOT / "frontend_dist",
    PROJECT_ROOT / "frontend" / "dist",
)

FRONTEND_DIST = next(
    (
        candidate
        for candidate
        in FRONTEND_CANDIDATES
        if candidate.is_dir()
    ),
    None,
)

if FRONTEND_DIST is None:
    raise RuntimeError(
        "Vue production build was not found. "
        "Expected frontend_dist or frontend/dist."
    )

FRONTEND_DIST = FRONTEND_DIST.resolve()


app = FastAPI(
    title="KnowledgeHub",
    description=(
        "KnowledgeHub Railway deployment "
        "for laboratory work в„–4."
    ),
    version="1.7-railway",
)

app.add_middleware(
    SecurityHeadersMiddleware,
)

app.add_middleware(
    GZipMiddleware,
    minimum_size=1000,
)

app.include_router(
    api_router
)


assets_directory = (
    FRONTEND_DIST
    / "assets"
)

if assets_directory.is_dir():
    app.mount(
        "/assets",
        StaticFiles(
            directory=assets_directory
        ),
        name="frontend-assets",
    )


@app.get(
    "/{full_path:path}",
    include_in_schema=False,
)
def serve_vue_spa(
    full_path: str,
):
    if full_path.startswith(
        "api/"
    ):
        raise HTTPException(
            status_code=404,
            detail="Not Found",
        )

    candidate = (
        FRONTEND_DIST
        / full_path
    ).resolve()

    try:
        candidate.relative_to(
            FRONTEND_DIST
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail="Not Found",
        ) from exc

    if candidate.is_file():
        return FileResponse(
            candidate
        )

    return FileResponse(
        FRONTEND_DIST
        / "index.html"
    )

