from pathlib import Path
import sys


BACKEND_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

PROJECT_ROOT = (
    BACKEND_ROOT
    .parent
)

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(BACKEND_ROOT),
    )


def main() -> None:
    frontend_dist = (
        PROJECT_ROOT
        / "frontend"
        / "dist"
    )

    assert frontend_dist.is_dir()
    assert (
        frontend_dist
        / "index.html"
    ).is_file()

    from app.production import app
    from app.api.v1.health import (
        router as health_router,
    )

    # FastAPI 0.141 can keep included routers as internal wrapper
    # objects, so do not depend on app.routes being fully flattened.
    health_paths = {
        getattr(
            route,
            "path",
            None,
        )
        for route
        in health_router.routes
    }

    assert "/health" in health_paths

    production_source = (
        BACKEND_ROOT
        / "app"
        / "production.py"
    ).read_text(
        encoding="utf-8"
    )

    assert "app.include_router" in production_source
    assert "api_router" in production_source
    assert '"/{full_path:path}"' in production_source
    assert app is not None

    dockerfile = (
        PROJECT_ROOT
        / "Dockerfile"
    ).read_text(
        encoding="utf-8"
    )

    assert "app.production:app" in dockerfile
    assert "${PORT:-8000}" in dockerfile
    assert "alembic upgrade head" in dockerfile

    requirements = (
        BACKEND_ROOT
        / "requirements.railway.txt"
    ).read_text(
        encoding="utf-8"
    )

    assert "torch==" not in requirements
    assert "transformers==" not in requirements
    assert "sentence-transformers==" not in requirements

    print("Railway readiness self-test: OK")


if __name__ == "__main__":
    main()
