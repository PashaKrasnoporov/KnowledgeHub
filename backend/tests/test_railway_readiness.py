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

    production_source = read(
        BACKEND_ROOT
        / "app"
        / "production.py"
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
        '"/{full_path:path}"',
        "Vue SPA fallback route",
    )

    require(
        production_source,
        "APP_VERSION",
        "Unified application version",
    )

    dockerfile = read(
        PROJECT_ROOT
        / "Dockerfile"
    )

    for marker, label in [
        (
            "app.production:app",
            "Production ASGI entrypoint",
        ),
        (
            "${PORT:-8000}",
            "Railway PORT binding",
        ),
        (
            "alembic upgrade head",
            "Database migrations",
        ),
        (
            "backfill_embeddings",
            "Embedding backfill",
        ),
        (
            "DEPLOYMENT_PROFILE=railway-ml",
            "Railway ML profile",
        ),
        (
            "ML_ENABLED=true",
            "Semantic ML enabled",
        ),
        (
            "LLM_ENABLED=false",
            "LLM capability isolation",
        ),
    ]:
        require(
            dockerfile,
            marker,
            label,
        )

    requirements = read(
        BACKEND_ROOT
        / "requirements.railway.txt"
    )

    require(
        requirements,
        "fastembed==0.9.1",
        "FastEmbed runtime",
    )

    require(
        requirements,
        "onnxruntime==1.31.1",
        "ONNX Runtime",
    )

    forbid(
        requirements,
        "torch==",
        "torch in Railway runtime",
    )

    forbid(
        requirements,
        "sentence-transformers==",
        "PyTorch SentenceTransformers",
    )

    settings_source = read(
        BACKEND_ROOT
        / "app"
        / "nalashtuvannia"
        / "parametry.py"
    )

    require(
        settings_source,
        "ml_enabled",
        "ML deployment switch",
    )

    require(
        settings_source,
        "llm_enabled",
        "LLM deployment switch",
    )

    version = read(
        PROJECT_ROOT
        / "VERSION"
    ).strip()

    assert version.startswith(
        "2.0.0"
    )

    print(
        "Railway readiness self-test: PASS"
    )


if __name__ == "__main__":
    main()
