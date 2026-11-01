from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def read(relative: str) -> str:
    return (PROJECT_ROOT / relative).read_text(
        encoding="utf-8-sig"
    )


def main() -> None:
    app = read("llm_service/app.py")
    dockerfile = read("Dockerfile.llm")
    requirements = read(
        "llm_service/requirements.txt"
    )

    assert '@app.get("/health")' in app
    assert '@app.post("/warmup")' in app
    assert '"/generate"' in app
    assert "n_ctx=CONTEXT_SIZE" in app
    assert 'chat_format="chatml"' in app
    assert "n_threads=THREADS" in app
    assert "n_gpu_layers=0" in app
    assert "use_mmap=True" in app
    assert 'LLM_CONTEXT_SIZE", "1024"' in app
    assert 'LLM_BATCH_SIZE", "32"' in app
    assert 'LLM_MAX_NEW_TOKENS", "128"' in app

    assert (
        "llama-cpp-python==0.3.23"
        in requirements
    )

    assert (
        "Qwen/Qwen2.5-1.5B-Instruct-GGUF"
        in dockerfile
    )

    assert (
        "--workers"
        in dockerfile
        and '"1"' in dockerfile
    )

    print(
        "Production LLM service contracts: PASS"
    )


if __name__ == "__main__":
    main()
