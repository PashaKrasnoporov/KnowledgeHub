import re

from app.nalashtuvannia.parametry import (
    parametry,
)
from app.schemas.research import (
    ResearchGeneratedResponseAPI,
    ResearchResponseAPI,
)
from app.services.local_llm_service import (
    LocalLLMError,
    generate_local_text,
)
from app.services.rag_prompt_service import (
    build_extractive_fallback,
    build_rag_messages,
)


CITATION_PATTERN = re.compile(
    r"\[(\d+)\]"
)

WORD_PATTERN = re.compile(
    r"[0-9A-Za-zА-Яа-яІіЇїЄєҐґ'-]{2,}"
)


def _citation_numbers(
    text: str,
) -> list[int]:
    return [
        int(value)
        for value
        in CITATION_PATTERN.findall(
            text
        )
    ]


def _text_without_citations(
    text: str,
) -> str:
    return CITATION_PATTERN.sub(
        " ",
        text,
    ).strip()


def _has_degenerate_repetition(
    answer: str,
) -> bool:
    citations = _citation_numbers(
        answer
    )

    if len(citations) >= 8:
        most_common = max(
            citations.count(value)
            for value
            in set(citations)
        )

        if (
            most_common
            / len(citations)
            >= 0.70
        ):
            return True

    words = [
        word.lower()
        for word
        in WORD_PATTERN.findall(
            _text_without_citations(
                answer
            )
        )
    ]

    if len(words) >= 20:
        unique_ratio = (
            len(set(words))
            / len(words)
        )

        if unique_ratio < 0.18:
            return True

    return False


def _answer_is_grounded(
    answer: str,
    research: ResearchResponseAPI,
) -> bool:
    if not answer.strip():
        return False

    allowed = {
        source.source_number
        for source
        in research.sources
    }

    citations = _citation_numbers(
        answer
    )

    if not citations:
        return False

    if not set(citations).issubset(
        allowed
    ):
        return False

    substantive_text = (
        _text_without_citations(
            answer
        )
    )

    words = WORD_PATTERN.findall(
        substantive_text
    )

    if len(words) < 12:
        return False

    if len(substantive_text) < 80:
        return False

    if len(citations) > 12:
        return False

    if _has_degenerate_repetition(
        answer
    ):
        return False

    return True


def generate_grounded_answer(
    research: ResearchResponseAPI,
    max_new_tokens: int | None = None,
) -> ResearchGeneratedResponseAPI:
    if not research.sources:
        fallback = (
            build_extractive_fallback(
                research
            )
        )

        return ResearchGeneratedResponseAPI(
            **research.model_dump(),
            generated_answer=fallback,
            generation_provider="fallback",
            generation_model=None,
            fallback_used=True,
            generation_error=None,
        )

    token_limit = (
        max_new_tokens
        or parametry.rag_max_new_tokens
    )

    token_limit = max(
        80,
        min(
            512,
            token_limit,
        ),
    )

    messages = build_rag_messages(
        research
    )

    try:
        generated = generate_local_text(
            messages=messages,
            max_new_tokens=token_limit,
        )

        if not _answer_is_grounded(
            generated,
            research,
        ):
            fallback = (
                build_extractive_fallback(
                    research
                )
            )

            return ResearchGeneratedResponseAPI(
                **research.model_dump(),
                generated_answer=fallback,
                generation_provider="fallback",
                generation_model=(
                    parametry.rag_local_model_name
                ),
                fallback_used=True,
                generation_error=(
                    "LLM-відповідь відхилено: "
                    "виявлено недостатньо змістовного "
                    "тексту, некоректні citations "
                    "або циклічне повторення."
                ),
            )

        return ResearchGeneratedResponseAPI(
            **research.model_dump(),
            generated_answer=generated,
            generation_provider="local-transformers",
            generation_model=(
                parametry.rag_local_model_name
            ),
            fallback_used=False,
            generation_error=None,
        )

    except LocalLLMError as error:
        fallback = (
            build_extractive_fallback(
                research
            )
        )

        return ResearchGeneratedResponseAPI(
            **research.model_dump(),
            generated_answer=fallback,
            generation_provider="fallback",
            generation_model=(
                parametry.rag_local_model_name
            ),
            fallback_used=True,
            generation_error=str(
                error
            ),
        )
