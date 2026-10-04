import re

from app.schemas.research import (
    ResearchResponseAPI,
)


SENTENCE_SPLIT_PATTERN = re.compile(
    r"(?<=[.!?])\s+|\n+"
)

LIST_PREFIX_PATTERN = re.compile(
    r"^\s*(?:[-•*]|\d+[.)])\s*"
)

TRAILING_NUMBER_PATTERN = re.compile(
    r"\s+\d{1,2}\.?$"
)

METADATA_START_PATTERN = re.compile(
    r"\s+(?:"
    r"Код документа"
    r"|Ключові слова"
    r"|Тип документа"
    r"|Document ID"
    r"|Keywords"
    r"|Document type"
    r")\s*:",
    flags=re.IGNORECASE,
)

TOKEN_PATTERN = re.compile(
    r"[0-9A-Za-zА-Яа-яІіЇїЄєҐґ_'-]{2,}"
)

STOP_WORDS = {
    "the", "and", "for", "with", "that", "this",
    "from", "what", "how", "which", "are", "was",
    "were", "have", "has",
    "про", "для", "що", "як", "який", "яка", "які",
    "це", "та", "і", "або", "до", "від", "на", "у",
    "в", "з", "із", "за", "при",
}

NOISE_PREFIXES = (
    "код документа",
    "ключові слова",
    "тип документа",
    "тестовий навчальний документ",
    "приклад де",
)

MIN_SENTENCE_LENGTH = 48
MAX_SENTENCE_LENGTH = 360


def _tokens(
    text: str,
) -> set[str]:
    tokens = {
        token.lower()
        for token
        in TOKEN_PATTERN.findall(
            text
        )
    }

    informative = {
        token
        for token in tokens
        if token not in STOP_WORDS
    }

    return informative or tokens


def prepare_source_sentence(
    text: str,
) -> str | None:
    """
    Prepare a sentence for extractive display only.
    Stored source text is never changed.
    """
    normalized = " ".join(
        text.split()
    ).strip()

    if not normalized:
        return None

    metadata_match = (
        METADATA_START_PATTERN.search(
            normalized
        )
    )

    if metadata_match:
        normalized = normalized[
            :metadata_match.start()
        ].strip()

    normalized = LIST_PREFIX_PATTERN.sub(
        "",
        normalized,
    ).strip()

    normalized = TRAILING_NUMBER_PATTERN.sub(
        "",
        normalized,
    ).strip()

    lowered = normalized.lower()

    if any(
        lowered.startswith(
            prefix
        )
        for prefix in NOISE_PREFIXES
    ):
        return None

    if (
        "kh-test-" in lowered
        and len(normalized) < 120
    ):
        return None

    if (
        len(normalized)
        < MIN_SENTENCE_LENGTH
    ):
        return None

    if len(
        _tokens(
            normalized
        )
    ) < 6:
        return None

    if (
        len(normalized)
        > MAX_SENTENCE_LENGTH
    ):
        shortened = normalized[
            :MAX_SENTENCE_LENGTH
        ].rsplit(
            " ",
            1,
        )[0]

        normalized = (
            shortened.rstrip(
                " ,.;:"
            )
            + "…"
        )

    return normalized


def _sentence_score(
    question: str,
    sentence: str,
    source_score: float,
) -> float:
    question_tokens = _tokens(
        question
    )

    sentence_tokens = _tokens(
        sentence
    )

    overlap = 0.0

    if question_tokens:
        overlap = (
            len(
                question_tokens
                & sentence_tokens
            )
            / len(
                question_tokens
            )
        )

    length_bonus = min(
        0.08,
        len(sentence) / 5000,
    )

    return (
        0.68 * overlap
        + 0.28 * source_score
        + length_bonus
    )


def _candidate_sentences(
    research: ResearchResponseAPI,
) -> list[
    tuple[
        float,
        str,
        int,
    ]
]:
    candidates = []

    for source in research.sources:
        parts = SENTENCE_SPLIT_PATTERN.split(
            source.excerpt
        )

        for part in parts:
            sentence = prepare_source_sentence(
                part
            )

            if sentence is None:
                continue

            score = _sentence_score(
                question=research.question,
                sentence=sentence,
                source_score=source.score,
            )

            candidates.append(
                (
                    score,
                    sentence,
                    source.source_number,
                )
            )

    candidates.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return candidates


def build_clean_extractive_fallback(
    research: ResearchResponseAPI,
    max_points: int = 3,
) -> str:
    candidates = _candidate_sentences(
        research
    )

    selected = []
    seen = set()
    source_usage = {}

    for (
        _score,
        sentence,
        source_number,
    ) in candidates:
        normalized = (
            sentence.lower()
        )

        if normalized in seen:
            continue

        used = source_usage.get(
            source_number,
            0,
        )

        if used >= 2:
            continue

        seen.add(
            normalized
        )

        source_usage[
            source_number
        ] = used + 1

        selected.append(
            (
                sentence,
                source_number,
            )
        )

        if len(
            selected
        ) >= max_points:
            break

    if not selected:
        return (
            "У знайдених фрагментах є релевантний "
            "контекст, але система не змогла "
            "сформувати достатньо чисту відповідь "
            "без зміни змісту першоджерел."
        )

    return "\n".join(
        (
            f"• {sentence} "
            f"[{source_number}]"
        )
        for (
            sentence,
            source_number,
        ) in selected
    )
