from pathlib import Path


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)


def read(relative: str) -> str:
    return (
        PROJECT_ROOT
        / relative
    ).read_text(
        encoding="utf-8-sig"
    )


def require(
    source: str,
    marker: str,
    label: str,
) -> None:
    assert marker in source, (
        f"Missing production parity contract: {label}"
    )


def main() -> None:
    dockerfile = read(
        "Dockerfile"
    )

    require(
        dockerfile,
        "VITE_DEPLOYMENT_PROFILE=railway-ml",
        "Railway ML frontend profile",
    )

    require(
        dockerfile,
        "ML_ENABLED=true",
        "Railway semantic runtime",
    )

    require(
        dockerfile,
        "LLM_ENABLED=false",
        "LLM isolation",
    )

    require(
        dockerfile,
        "backfill_embeddings",
        "Existing document backfill",
    )

    embedding = read(
        "backend/app/services/embedding_service.py"
    )

    require(
        embedding,
        "fastembed",
        "FastEmbed backend",
    )

    require(
        embedding,
        "paraphrase-multilingual-MiniLM-L12-v2",
        "Multilingual MiniLM",
    )

    require(
        embedding,
        "_normalize_rows",
        "Normalized vectors",
    )

    research = read(
        "backend/app/api/v1/research.py"
    )

    require(
        research,
        "_require_llm_enabled",
        "Separate LLM gate",
    )

    require(
        research,
        "_require_ml_enabled",
        "Research ML gate",
    )

    panel = read(
        "frontend/src/components/research/ResearchPanel.vue"
    )

    require(
        panel,
        "llmAvailable",
        "Railway LLM UI capability",
    )

    print(
        "Production parity phase 1 contracts: PASS"
    )


if __name__ == "__main__":
    main()
