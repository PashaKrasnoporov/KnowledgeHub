from functools import lru_cache

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
)

from app.nalashtuvannia.parametry import (
    parametry,
)


class LocalLLMError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def get_local_llm():
    model_name = parametry.rag_local_model_name

    try:
        tokenizer = AutoTokenizer.from_pretrained(
            model_name
        )

        model_kwargs = {}

        if torch.cuda.is_available():
            model_kwargs[
                "torch_dtype"
            ] = torch.float16

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

        return tokenizer, model, device

    except Exception as error:
        raise LocalLLMError(
            "Не вдалося завантажити локальну LLM. "
            "Перевірте доступ до Hugging Face, "
            "вільне місце на диску та пам'ять."
        ) from error


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
                f"{role}:\n{message['content']}"
            )

        parts.append("ASSISTANT:\n")
        return "\n\n".join(parts)


def generate_local_text(
    messages: list[dict[str, str]],
    max_new_tokens: int,
) -> str:
    tokenizer, model, device = get_local_llm()

    prompt = _render_messages(
        tokenizer,
        messages,
    )

    encoded = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=12000,
    )

    encoded = {
        key: value.to(device)
        for key, value in encoded.items()
    }

    input_length = encoded[
        "input_ids"
    ].shape[1]

    pad_token_id = tokenizer.pad_token_id

    if pad_token_id is None:
        pad_token_id = tokenizer.eos_token_id

    try:
        with torch.inference_mode():
            output = model.generate(
                **encoded,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                repetition_penalty=1.05,
                pad_token_id=pad_token_id,
            )
    except Exception as error:
        raise LocalLLMError(
            "Локальна LLM не змогла сформувати відповідь."
        ) from error

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
