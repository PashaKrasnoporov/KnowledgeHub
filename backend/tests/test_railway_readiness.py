from pathlib import Path


BACKEND_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

PROJECT_ROOT = (
    BACKEND_ROOT
    .parent
)


def read(
    path: Path,
) -> str:
    return path.read_text(
        encoding="utf-8-sig",
    )


def require(
    source: str,
    marker: str,
    label: str,
) -> None:
    assert marker in source, (
        f"Missing Railway contract: {label}"
    )


def forbid(
    source: str,
    marker: str,
    label: str,
) -> None:
    assert marker not in source, (
        f"Forbidden Railway contract: {label}"
    )


def main() -> None:
    # -----------------------------------------------------
    # Frontend production build
    # -----------------------------------------------------

    frontend_dist = (
        PROJECT_ROOT
        / "frontend"
        / "dist"
    )

    assert frontend_dist.is_dir(), (
        "frontend/dist does not exist. "
        "Run npm run build first."
    )

    assert (
        frontend_dist
        / "index.html"
    ).is_file(), (
        "frontend/dist/index.html "
        "does not exist."
    )

    # -----------------------------------------------------
    # Production FastAPI source
    # Do NOT import app.production here:
    # importing it initializes DB dependencies.
    # -----------------------------------------------------

    production_file = (
        BACKEND_ROOT
        / "app"
        / "production.py"
    )

    production_source = read(
        production_file
    )

    require(
        production_source,
        "FastAPI(",
        "FastAPI production application",
    )

    require(
        production_source,
        "app.include_router",
        "API router inclusion",
    )

    require(
        production_source,
        "api_router",
        "API router",
    )

    require(
        production_source,
        '"/{full_path:path}"',
        "Vue SPA fallback route",
    )

    require(
        production_source,
        "FRONTEND_DIST",
        "Frontend distribution path",
    )

    require(
        production_source,
        "APP_VERSION",
        "Unified application version",
    )

    forbid(
        production_source,
        "laboratory work",
        "Legacy laboratory wording",
    )

    forbid(
        production_source,
        "в„–4",
        "Broken legacy encoding",
    )

    # -----------------------------------------------------
    # Health endpoint source
    # -----------------------------------------------------

    health_source = read(
        BACKEND_ROOT
        / "app"
        / "api"
        / "v1"
        / "health.py"
    )

    require(
        health_source,
        '"/health"',
        "Health endpoint",
    )

    require(
        health_source,
        "app_version",
        "Application version in health response",
    )

    require(
        health_source,
        "APP_VERSION",
        "Unified health version",
    )

    require(
        health_source,
        '"/health/live"',
        "Liveness endpoint",
    )

    require(
        health_source,
        '"/health/ready"',
        "Readiness endpoint",
    )

    require(
        health_source,
        'text("SELECT 1")',
        "Database readiness probe",
    )

    require(
        health_source,
        "NamedTemporaryFile",
        "Writable storage readiness probe",
    )

    require(
        health_source,
        "HTTP_503_SERVICE_UNAVAILABLE",
        "Readiness failure status",
    )

    # -----------------------------------------------------
    # Docker / Railway runtime
    # -----------------------------------------------------

    dockerfile = read(
        PROJECT_ROOT
        / "Dockerfile"
    )

    require(
        dockerfile,
        "app.production:app",
        "Production ASGI entrypoint",
    )

    require(
        dockerfile,
        "${PORT:-8000}",
        "Railway PORT binding",
    )

    require(
        dockerfile,
        "alembic upgrade head",
        "Database migrations on startup",
    )

    require(
        dockerfile,
        "COPY VERSION",
        "VERSION copied into image",
    )

    # -----------------------------------------------------
    # Lightweight Railway dependencies
    # -----------------------------------------------------

    requirements = read(
        BACKEND_ROOT
        / "requirements.railway.txt"
    )

    forbid(
        requirements,
        "torch==",
        "torch in Railway-lite",
    )

    forbid(
        requirements,
        "transformers==",
        "transformers in Railway-lite",
    )

    forbid(
        requirements,
        "sentence-transformers==",
        "sentence-transformers in Railway-lite",
    )

    # -----------------------------------------------------
    # Deployment settings contract
    # -----------------------------------------------------

    settings_source = read(
        BACKEND_ROOT
        / "app"
        / "nalashtuvannia"
        / "parametry.py"
    )

    require(
        settings_source,
        "database_url",
        "DATABASE_URL support",
    )

    require(
        settings_source,
        "deployment_profile",
        "Deployment profile setting",
    )

    require(
        settings_source,
        "ml_enabled",
        "ML deployment switch",
    )

    # -----------------------------------------------------
    # Version
    # -----------------------------------------------------

    version = read(
        PROJECT_ROOT
        / "VERSION"
    ).strip()

    assert version.startswith(
        "2.0.0"
    ), (
        "Unexpected application VERSION: "
        + version
    )

    print(
        "Railway readiness self-test: PASS"
    )


if __name__ == "__main__":
    main()
