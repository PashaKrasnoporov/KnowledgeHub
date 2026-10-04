import re

from app.nalashtuvannia.parametry import (
    parametry,
)
from app.schemas.research import (
    ResearchGeneratedResponseAPI,
    ResearchResponseAPI,
)
from app.services.claim_grounding_service import (
    ground_generated_answer,
)
from app.services.local_llm_service import (
    LocalLLMError,
    generate_local_text,
)
from app.services.rag_prompt_service import (
    build_extractive_fallback,
    build_rag_messages,
)


WORD_PATTERN = re.compile(
    r"[0-9A-Za-zА-Яа-яІіЇїЄєҐґ'-]{2,}"
)

MIN_ACCEPTED_GROUNDING_COVERAGE = 0.50


def _has_degenerate_repetition(
    answer: str,
) -> bool:
    words = [
        word.lower()
        for word
        in WORD_PATTERN.findall(
            answer
        )
    ]

    if len(words) < 20:
        return False

    unique_ratio = (
        len(
            set(
                words
            )
        )
        / len(
            words
        )
    )

    if unique_ratio < 0.20:
        return True

    repeated_windows = {}

    for index in range(
        max(
            0,
            len(words) - 4
        )
    ):
        window = tuple(
            words[
                index:
                index + 5
            ]
        )

        repeated_windows[
            window
        ] = (
            repeated_windows.get(
                window,
                0,
            )
            + 1
        )

    return any(
        count >= 3
        for count
        in repeated_windows.values()
    )


def _fallback_response(
    research: ResearchResponseAPI,
    generation_model: str | None,
    error: str | None,
) -> ResearchGeneratedResponseAPI:
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
            generation_model
        ),
        grounded_claims=[],
        grounding_coverage=0.0,
        removed_claims=0,
        fallback_used=True,
        generation_error=error,
    )


def generate_grounded_answer(
    research: ResearchResponseAPI,
    max_new_tokens: int | None = None,
) -> ResearchGeneratedResponseAPI:
    if not research.sources:
        return _fallback_response(
            research=research,
            generation_model=None,
            error=None,
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

        if _has_degenerate_repetition(
            generated
        ):
            return _fallback_response(
                research=research,
                generation_model=(
                    parametry.rag_local_model_name
                ),
                error=(
                    "LLM-відповідь відхилено через "
                    "циклічне повторення тексту."
                ),
            )

        grounding = ground_generated_answer(
            generated_text=generated,
            research=research,
        )

        if not grounding.claims:
            return _fallback_response(
                research=research,
                generation_model=(
                    parametry.rag_local_model_name
                ),
                error=(
                    "LLM сформувала текст, але жодне "
                    "твердження не вдалося достатньо "
                    "підтвердити знайденими джерелами."
                ),
            )

        if (
            grounding.coverage
            < MIN_ACCEPTED_GROUNDING_COVERAGE
        ):
            return _fallback_response(
                research=research,
                generation_model=(
                    parametry.rag_local_model_name
                ),
                error=(
                    "LLM-відповідь відхилено: "
                    "менше половини тверджень "
                    "підтверджено знайденими джерелами."
                ),
            )

        return ResearchGeneratedResponseAPI(
            **research.model_dump(),
            generated_answer=(
                grounding.answer
            ),
            generation_provider=(
                "local-transformers"
            ),
            generation_model=(
                parametry.rag_local_model_name
            ),
            grounded_claims=(
                grounding.claims
            ),
            grounding_coverage=(
                grounding.coverage
            ),
            removed_claims=(
                grounding.removed_claims
            ),
            fallback_used=False,
            generation_error=None,
        )

    except LocalLLMError as error:
        return _fallback_response(
            research=research,
            generation_model=(
                parametry.rag_local_model_name
            ),
            error=str(
                error
            ),
        )
