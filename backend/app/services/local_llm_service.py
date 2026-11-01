from __future__ import annotations

import json
from threading import Lock
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.nalashtuvannia.parametry import parametry


class LocalLLMError(RuntimeError):
    pass


_MODEL_BUNDLE = None
_MODEL_LOCK = Lock()

_REMOTE_READY = False
_REMOTE_LOCK = Lock()


def _use_remote_llm() -> bool:
    return parametry.llm_backend.strip().lower() == "remote"


def _remote_url(path: str) -> str:
    return parametry.llm_service_url.rstrip("/") + path


def _remote_request(path: str, payload: dict | None = None) -> dict:
    body = None
    headers = {"Accept": "application/json"}
    method = "GET"

    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
        method = "POST"

    request = Request(
        _remote_url(path),
        data=body,
        headers=headers,
        method=method,
    )

    try:
        with urlopen(
            request,
            timeout=parametry.llm_service_timeout_seconds,
        ) as response:
            raw = response.read()

        data = json.loads(raw.decode("utf-8"))

        if not isinstance(data, dict):
            raise LocalLLMError("LLM service returned an invalid response.")

        return data

    except HTTPError as error:
        try:
            detail = json.loads(error.read().decode("utf-8"))
            message = detail.get("detail") if isinstance(detail, dict) else None
        except Exception:
            message = None

        raise LocalLLMError(
            message or f"LLM service returned HTTP {error.code}."
        ) from error

    except (URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError) as error:
        raise LocalLLMError(
            "Не вдалося підключитися до сервісу генеративної LLM."
        ) from error


def is_local_llm_loaded() -> bool:
    if _use_remote_llm():
        return _REMOTE_READY

    return _MODEL_BUNDLE is not None


def get_local_llm():
    global _MODEL_BUNDLE

    if _MODEL_BUNDLE is not None:
        return _MODEL_BUNDLE

    with _MODEL_LOCK:
        if _MODEL_BUNDLE is not None:
            return _MODEL_BUNDLE

        try:
            import torch

            from transformers import (
                AutoModelForCausalLM,
                AutoTokenizer,
            )

            model_name = parametry.rag_local_model_name

            tokenizer = AutoTokenizer.from_pretrained(
                model_name
            )

            model_kwargs = {}

            if torch.cuda.is_available():
                model_kwargs["torch_dtype"] = torch.float16

            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                **model_kwargs,
            )

            device = torch.device(
                "cuda"
                if torch.cuda.is_available()
                else "cpu"
            )

            model.to(device)
            model.eval()

            _MODEL_BUNDLE = (
                tokenizer,
                model,
                device,
            )

            return _MODEL_BUNDLE

        except Exception as error:
            raise LocalLLMError(
                "Не вдалося завантажити локальну LLM. "
                "Перевірте доступ до Hugging Face, "
                "вільне місце на диску та пам'ять."
            ) from error


def warmup_local_llm() -> dict[str, str]:
    global _REMOTE_READY

    if _use_remote_llm():
        with _REMOTE_LOCK:
            result = _remote_request(
                "/warmup",
                {},
            )
            _REMOTE_READY = True

        return {
            "status": str(
                result.get(
                    "status",
                    "ready",
                )
            ),
            "model": str(
                result.get(
                    "model",
                    parametry.rag_local_model_name,
                )
            ),
            "device": str(
                result.get(
                    "device",
                    "remote-cpu",
                )
            ),
        }

    _, _, device = get_local_llm()

    return {
        "status": "ready",
        "model": parametry.rag_local_model_name,
        "device": str(device),
    }


def _render_messages(
    tokenizer,
    messages: list[dict[str, str]],
) -> str:
    try:
        return tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
    except Exception:
        parts = []

        for message in messages:
            role = message["role"].upper()

            parts.append(
                f"{role}:\n"
                f"{message['content']}"
            )

        parts.append("ASSISTANT:\n")

        return "\n\n".join(parts)


def _generate_remote_text(
    messages: list[dict[str, str]],
    max_new_tokens: int,
    deterministic: bool,
) -> str:
    global _REMOTE_READY

    result = _remote_request(
        "/generate",
        {
            "messages": messages,
            "max_new_tokens": max_new_tokens,
            "deterministic": deterministic,
        },
    )

    text = str(
        result.get(
            "text",
            "",
        )
    ).strip()

    if not text:
        raise LocalLLMError(
            "Сервіс генеративної LLM повернув порожню відповідь."
        )

    _REMOTE_READY = True

    return text


def generate_local_text(
    messages: list[dict[str, str]],
    max_new_tokens: int,
    deterministic: bool = True,
) -> str:
    if _use_remote_llm():
        return _generate_remote_text(
            messages=messages,
            max_new_tokens=max_new_tokens,
            deterministic=deterministic,
        )

    try:
        import torch

        (
            tokenizer,
            model,
            device,
        ) = get_local_llm()

        prompt = _render_messages(
            tokenizer,
            messages,
        )

        encoded = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=6144,
        )

        encoded = {
            key: value.to(device)
            for key, value
            in encoded.items()
        }

        input_length = encoded["input_ids"].shape[1]

        pad_token_id = tokenizer.pad_token_id

        if pad_token_id is None:
            pad_token_id = tokenizer.eos_token_id

        generation_kwargs = {
            "max_new_tokens": max_new_tokens,
            "repetition_penalty": 1.10,
            "no_repeat_ngram_size": 4,
            "pad_token_id": pad_token_id,
            "eos_token_id": tokenizer.eos_token_id,
            "use_cache": True,
        }

        if deterministic:
            generation_kwargs["do_sample"] = False
        else:
            generation_kwargs.update(
                {
                    "do_sample": True,
                    "temperature": 0.20,
                    "top_p": 0.80,
                    "top_k": 20,
                }
            )

        with torch.inference_mode():
            output = model.generate(
                **encoded,
                **generation_kwargs,
            )

        generated_tokens = output[
            0,
            input_length:,
        ]

        answer = tokenizer.decode(
            generated_tokens,
            skip_special_tokens=True,
        ).strip()

        if not answer:
            raise LocalLLMError(
                "Локальна LLM повернула порожню відповідь."
            )

        return answer

    except LocalLLMError:
        raise

    except Exception as error:
        raise LocalLLMError(
            "Локальна LLM не змогла сформувати відповідь."
        ) from error
