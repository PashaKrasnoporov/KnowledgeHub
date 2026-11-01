from __future__ import annotations

import os
from threading import Lock
from time import perf_counter

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from llama_cpp import Llama

MODEL_PATH = os.getenv("LLM_MODEL_PATH", "/models/qwen2.5-0.5b-instruct-q4_k_m.gguf")
MODEL_NAME = os.getenv("LLM_MODEL_NAME", "Qwen/Qwen2.5-0.5B-Instruct")
CONTEXT_SIZE = int(os.getenv("LLM_CONTEXT_SIZE", "2048"))
THREADS = int(os.getenv("LLM_THREADS", "2"))
BATCH_SIZE = int(os.getenv("LLM_BATCH_SIZE", "128"))
MAX_NEW_TOKENS = int(os.getenv("LLM_MAX_NEW_TOKENS", "160"))


class Message(BaseModel):
    role: str
    content: str


class GenerateRequest(BaseModel):
    messages: list[Message]
    max_new_tokens: int = Field(default=96, ge=32, le=320)
    deterministic: bool = True


class GenerateResponse(BaseModel):
    text: str
    model: str
    elapsed_ms: float
    cold_start: bool


app = FastAPI(title="KnowledgeHub LLM Service", version="1.0.0")

_MODEL: Llama | None = None
_MODEL_LOCK = Lock()
_GENERATION_LOCK = Lock()


def is_loaded() -> bool:
    return _MODEL is not None


def get_model() -> Llama:
    global _MODEL

    if _MODEL is not None:
        return _MODEL

    with _MODEL_LOCK:
        if _MODEL is not None:
            return _MODEL

        if not os.path.isfile(MODEL_PATH):
            raise RuntimeError("GGUF model file not found.")

        _MODEL = Llama(
            model_path=MODEL_PATH,
            chat_format="chatml",
            n_ctx=CONTEXT_SIZE,
            n_threads=THREADS,
            n_threads_batch=THREADS,
            n_batch=BATCH_SIZE,
            n_gpu_layers=0,
            use_mmap=True,
            use_mlock=False,
            verbose=False,
        )

        return _MODEL


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model": MODEL_NAME,
        "loaded": is_loaded(),
        "context_size": CONTEXT_SIZE,
    }


@app.post("/warmup")
def warmup():
    started = perf_counter()
    cold_start = not is_loaded()

    try:
        get_model()
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="LLM model could not be loaded.",
        ) from exc

    return {
        "status": "ready",
        "model": MODEL_NAME,
        "device": "railway-cpu",
        "cold_start": cold_start,
        "elapsed_ms": round((perf_counter() - started) * 1000, 1),
    }


@app.post("/generate", response_model=GenerateResponse)
def generate(payload: GenerateRequest):
    if not payload.messages:
        raise HTTPException(status_code=400, detail="messages must not be empty")

    started = perf_counter()
    cold_start = not is_loaded()

    try:
        model = get_model()

        messages = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in payload.messages
        ]

        max_tokens = min(payload.max_new_tokens, MAX_NEW_TOKENS)

        with _GENERATION_LOCK:
            result = model.create_chat_completion(
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.0 if payload.deterministic else 0.20,
                top_p=1.0 if payload.deterministic else 0.80,
                repeat_penalty=1.10,
                seed=0,
            )

        choices = result.get("choices") or []
        if not choices:
            raise RuntimeError("LLM returned no choices.")

        text = str(
            choices[0]
            .get("message", {})
            .get("content", "")
        ).strip()

        if not text:
            raise RuntimeError("LLM returned an empty answer.")

        return GenerateResponse(
            text=text,
            model=MODEL_NAME,
            elapsed_ms=round((perf_counter() - started) * 1000, 1),
            cold_start=cold_start,
        )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="LLM generation failed.",
        ) from exc
