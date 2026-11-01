from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def read(relative: str) -> str:
    return (PROJECT_ROOT / relative).read_text(
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
    dockerfile = read("Dockerfile")

    require(
        dockerfile,
        "VITE_DEPLOYMENT_PROFILE=railway-ml",
        "Railway ML frontend profile",
    )
    require(
        dockerfile,
        "VITE_LLM_ENABLED=true",
        "Railway LLM frontend capability",
    )
    require(
        dockerfile,
        "ML_ENABLED=true",
        "Railway semantic runtime",
    )
    require(
        dockerfile,
        "LLM_ENABLED=true",
        "Railway generative RAG",
    )
    require(
        dockerfile,
        "LLM_BACKEND=remote",
        "Remote LLM backend",
    )
    require(
        dockerfile,
        "knowledgehub-llm.railway.internal",
        "Private Railway LLM network",
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

    local_llm = read(
        "backend/app/services/local_llm_service.py"
    )
    require(
        local_llm,
        "_generate_remote_text",
        "Remote generation adapter",
    )
    require(
        local_llm,
        "llm_service_url",
        "Private LLM service URL",
    )
    require(
        local_llm,
        "urlopen",
        "Remote HTTP transport",
    )

    llm_dockerfile = read("Dockerfile.llm")
    llm_requirements = read(
        "llm_service/requirements.txt"
    )

    require(
        llm_requirements,
        "llama-cpp-python==0.3.23",
        "llama.cpp Python runtime",
    )
    require(
        llm_dockerfile,
        "qwen2.5-0.5b-instruct-q4_k_m.gguf",
        "Qwen GGUF model",
    )

    llm_app = read("llm_service/app.py")
    require(
        llm_app,
        "create_chat_completion",
        "Qwen chat inference",
    )
    require(
        llm_app,
        "_GENERATION_LOCK",
        "Single-generation memory guard",
    )

    panel = read(
        "frontend/src/components/research/ResearchPanel.vue"
    )
    require(
        panel,
        "VITE_LLM_ENABLED",
        "Frontend LLM capability flag",
    )

    print(
        "Production parity phase 2 contracts: PASS"
    )


if __name__ == "__main__":
    main()
