from threading import Lock

from app.nalashtuvannia.parametry import (
    parametry,
)


class LocalLLMError(RuntimeError):
    pass


_MODEL_BUNDLE = None
_MODEL_LOCK = Lock()


def is_local_llm_loaded() -> bool:
    return _MODEL_BUNDLE is not None


def get_local_llm():
    """
    Load the model once, lazily and thread-safely.

    This avoids duplicate 3 GB model loads when a background warmup
    and an answer request happen at nearly the same time.
    """
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

            model_name = (
                parametry.rag_local_model_name
            )

            tokenizer = (
                AutoTokenizer.from_pretrained(
                    model_name
                )
            )

            model_kwargs = {}

            if torch.cuda.is_available():
                model_kwargs[
                    "torch_dtype"
                ] = torch.float16

            model = (
                AutoModelForCausalLM.from_pretrained(
                    model_name,
                    **model_kwargs,
                )
            )

            device = torch.device(
                "cuda"
                if torch.cuda.is_available()
                else "cpu"
            )

            model.to(
                device
            )

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
            role = message[
                "role"
            ].upper()

            parts.append(
                f"{role}:\n"
                f"{message['content']}"
            )

        parts.append(
            "ASSISTANT:\n"
        )

        return "\n\n".join(
            parts
        )


def generate_local_text(
    messages: list[dict[str, str]],
    max_new_tokens: int,
    deterministic: bool = True,
) -> str:
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
            key: value.to(
                device
            )
            for key, value
            in encoded.items()
        }

        input_length = (
            encoded[
                "input_ids"
            ].shape[1]
        )

        pad_token_id = (
            tokenizer.pad_token_id
        )

        if pad_token_id is None:
            pad_token_id = (
                tokenizer.eos_token_id
            )

        generation_kwargs = {
            "max_new_tokens": max_new_tokens,
            "repetition_penalty": 1.10,
            "no_repeat_ngram_size": 4,
            "pad_token_id": pad_token_id,
            "eos_token_id": (
                tokenizer.eos_token_id
            ),
            "use_cache": True,
        }

        if deterministic:
            generation_kwargs[
                "do_sample"
            ] = False
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
