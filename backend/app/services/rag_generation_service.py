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
from app.services.ukrainian_language_service import (
    build_ukrainian_rewrite_messages,
    needs_ukrainian_rewrite,
)


WORD_PATTERN = re.compile(
    r"[0-9A-Za-zА-Яа-яІіЇїЄєҐґ'-]{2,}"
)

MIN_ACCEPTED_GROUNDING_COVERAGE = 0.50
MIN_EVIDENCE_CONFIDENCE = 0.30


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
        len(set(words))
        / len(words)
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


def _evidence_confidence(
    research: ResearchResponseAPI,
) -> float:
    if not research.sources:
        return 0.0

    scores = [
        float(source.score)
        for source
        in research.sources[
            :3
        ]
    ]

    top_score = scores[0]
    mean_score = (
        sum(scores)
        / len(scores)
    )

    confidence = (
        0.70 * top_score
        + 0.30 * mean_score
    )

    return round(
        max(
            0.0,
            min(
                1.0,
                confidence,
            ),
        ),
        4,
    )


def _fallback_response(
    research: ResearchResponseAPI,
    generation_model: str | None,
    error: str | None,
    response_language: str,
    language_retry_used: bool,
    evidence_confidence: float,
) -> ResearchGeneratedResponseAPI:
    fallback = build_extractive_fallback(
        research
    )

    return ResearchGeneratedResponseAPI(
        **research.model_dump(),
        generated_answer=fallback,
        generation_provider="fallback",
        generation_model=generation_model,
        response_language=response_language,
        language_retry_used=(
            language_retry_used
        ),
        grounded_claims=[],
        grounding_coverage=0.0,
        removed_claims=0,
        evidence_confidence=(
            evidence_confidence
        ),
        insufficient_evidence=False,
        fallback_used=True,
        generation_error=error,
    )


def _insufficient_evidence_response(
    research: ResearchResponseAPI,
    response_language: str,
    evidence_confidence: float,
) -> ResearchGeneratedResponseAPI:
    message = (
        "У завантажених документах не знайдено "
        "достатньо надійних доказів для впевненої "
        "відповіді на це запитання. Спробуйте "
        "уточнити формулювання або додати "
        "релевантні матеріали."
    )

    return ResearchGeneratedResponseAPI(
        **research.model_dump(),
        generated_answer=message,
        generation_provider="evidence-gate",
        generation_model=None,
        response_language=response_language,
        language_retry_used=False,
        grounded_claims=[],
        grounding_coverage=0.0,
        removed_claims=0,
        evidence_confidence=(
            evidence_confidence
        ),
        insufficient_evidence=True,
        fallback_used=False,
        generation_error=None,
    )


def generate_grounded_answer(
    research: ResearchResponseAPI,
    max_new_tokens: int | None = None,
    response_language: str = "uk",
) -> ResearchGeneratedResponseAPI:
    confidence = _evidence_confidence(
        research
    )

    if (
        not research.sources
        or confidence
        < MIN_EVIDENCE_CONFIDENCE
    ):
        return _insufficient_evidence_response(
            research=research,
            response_language=(
                response_language
            ),
            evidence_confidence=(
                confidence
            ),
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
        research=research,
        response_language=(
            response_language
        ),
    )

    language_retry_used = False

    try:
        generated = generate_local_text(
            messages=messages,
            max_new_tokens=token_limit,
        )

        if (
            response_language == "uk"
            and needs_ukrainian_rewrite(
                generated
            )
        ):
            language_retry_used = True

            generated = generate_local_text(
                messages=(
                    build_ukrainian_rewrite_messages(
                        generated
                    )
                ),
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
                response_language=(
                    response_language
                ),
                language_retry_used=(
                    language_retry_used
                ),
                evidence_confidence=(
                    confidence
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
                response_language=(
                    response_language
                ),
                language_retry_used=(
                    language_retry_used
                ),
                evidence_confidence=(
                    confidence
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
                response_language=(
                    response_language
                ),
                language_retry_used=(
                    language_retry_used
                ),
                evidence_confidence=(
                    confidence
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
            response_language=(
                response_language
            ),
            language_retry_used=(
                language_retry_used
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
            evidence_confidence=(
                confidence
            ),
            insufficient_evidence=False,
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
            response_language=(
                response_language
            ),
            language_retry_used=(
                language_retry_used
            ),
            evidence_confidence=(
                confidence
            ),
        )
