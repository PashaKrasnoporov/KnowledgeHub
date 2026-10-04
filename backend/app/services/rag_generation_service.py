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


def _citation_numbers(
    text: str,
) -> set[int]:
    return {
        int(value)
        for value
        in CITATION_PATTERN.findall(text)
    }


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

    citations = _citation_numbers(answer)

    if not citations:
        return False

    return citations.issubset(allowed)


def generate_grounded_answer(
    research: ResearchResponseAPI,
    max_new_tokens: int | None = None,
) -> ResearchGeneratedResponseAPI:
    if not research.sources:
        fallback = build_extractive_fallback(
            research
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
        min(512, token_limit),
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
            fallback = build_extractive_fallback(
                research
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
                    "LLM-відповідь не пройшла "
                    "перевірку посилань на джерела."
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
        fallback = build_extractive_fallback(
            research
        )

        return ResearchGeneratedResponseAPI(
            **research.model_dump(),
            generated_answer=fallback,
            generation_provider="fallback",
            generation_model=(
                parametry.rag_local_model_name
            ),
            fallback_used=True,
            generation_error=str(error),
        )
