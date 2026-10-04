import re
from dataclasses import dataclass

import numpy as np

from app.schemas.research import (
    GroundedClaimAPI,
    ResearchResponseAPI,
)
from app.services.embedding_service import (
    create_text_embeddings,
)


SENTENCE_SPLIT_PATTERN = re.compile(
    r"(?<=[.!?])\s+|\n+"
)

CITATION_PATTERN = re.compile(
    r"\[\s*\d+\s*\]"
)

BULLET_PREFIX_PATTERN = re.compile(
    r"^\s*(?:[-•*]|\d+[.)])\s*"
)

TOKEN_PATTERN = re.compile(
    r"[0-9A-Za-zА-Яа-яІіЇїЄєҐґ_'-]{2,}"
)

STOP_WORDS = {
    "the", "and", "for", "with", "that", "this",
    "from", "what", "how", "which", "are", "was",
    "were", "have", "has", "into", "than", "then",
    "про", "для", "що", "як", "який", "яка", "які",
    "це", "та", "і", "або", "до", "від", "на", "у",
    "в", "з", "із", "за", "при", "під", "над",
}

CLAIM_SEMANTIC_WEIGHT = 0.78
CLAIM_LEXICAL_WEIGHT = 0.17
SOURCE_PRIOR_WEIGHT = 0.05

MIN_GROUNDING_SCORE = 0.43
MIN_SEMANTIC_SCORE = 0.34
MIN_CLAIM_CHARACTERS = 24


@dataclass
class GroundingResult:
    answer: str
    claims: list[GroundedClaimAPI]
    coverage: float
    total_claims: int
    removed_claims: int


def _clean_claim(
    text: str,
) -> str:
    cleaned = CITATION_PATTERN.sub(
        "",
        text,
    )

    cleaned = BULLET_PREFIX_PATTERN.sub(
        "",
        cleaned,
    )

    cleaned = " ".join(
        cleaned.split()
    ).strip(
        " \t\r\n-•*"
    )

    return cleaned


def _split_claims(
    text: str,
) -> list[str]:
    candidates = []

    for part in SENTENCE_SPLIT_PATTERN.split(
        text
    ):
        claim = _clean_claim(
            part
        )

        if len(claim) < MIN_CLAIM_CHARACTERS:
            continue

        candidates.append(
            claim
        )

    if (
        not candidates
        and len(_clean_claim(text))
        >= MIN_CLAIM_CHARACTERS
    ):
        candidates = [
            _clean_claim(
                text
            )
        ]

    return candidates[
        :6
    ]


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


def _lexical_score(
    claim: str,
    source_text: str,
) -> float:
    claim_tokens = _tokens(
        claim
    )

    if not claim_tokens:
        return 0.0

    source_tokens = _tokens(
        source_text
    )

    return min(
        1.0,
        (
            len(
                claim_tokens
                & source_tokens
            )
            / len(
                claim_tokens
            )
        ),
    )


def _format_claim(
    claim: str,
    source_number: int,
) -> str:
    claim = claim.strip()

    if (
        claim
        and claim[-1]
        not in ".!?"
    ):
        claim += "."

    return (
        f"{claim} "
        f"[{source_number}]"
    )


def _source_embedding_matrix(
    research: ResearchResponseAPI,
) -> np.ndarray:
    stored = [
        source.embedding
        for source in research.sources
    ]

    if all(stored):
        return np.asarray(
            stored,
            dtype=np.float32,
        )

    # Compatibility fallback for older/internal callers.
    return create_text_embeddings(
        [
            source.excerpt
            for source in research.sources
        ]
    )


def ground_generated_answer(
    generated_text: str,
    research: ResearchResponseAPI,
) -> GroundingResult:
    claims = _split_claims(
        generated_text
    )

    if (
        not claims
        or not research.sources
    ):
        return GroundingResult(
            answer="",
            claims=[],
            coverage=0.0,
            total_claims=len(claims),
            removed_claims=len(claims),
        )

    # Only new claims are embedded. Retrieved source embeddings are reused
    # from PostgreSQL instead of being recomputed for every answer.
    claim_embeddings = create_text_embeddings(
        claims
    )

    source_embeddings = _source_embedding_matrix(
        research
    )

    semantic_matrix = np.clip(
        claim_embeddings
        @ source_embeddings.T,
        0.0,
        1.0,
    )

    grounded_claims = []

    for (
        claim_index,
        claim,
    ) in enumerate(
        claims
    ):
        best = None

        for (
            source_index,
            source,
        ) in enumerate(
            research.sources
        ):
            semantic_score = float(
                semantic_matrix[
                    claim_index,
                    source_index,
                ]
            )

            lexical_score = _lexical_score(
                claim,
                source.excerpt,
            )

            grounding_score = (
                CLAIM_SEMANTIC_WEIGHT
                * semantic_score
                + CLAIM_LEXICAL_WEIGHT
                * lexical_score
                + SOURCE_PRIOR_WEIGHT
                * source.score
            )

            candidate = {
                "source": source,
                "grounding_score": grounding_score,
                "semantic_score": semantic_score,
                "lexical_score": lexical_score,
            }

            if (
                best is None
                or candidate[
                    "grounding_score"
                ]
                > best[
                    "grounding_score"
                ]
            ):
                best = candidate

        if best is None:
            continue

        if (
            best["grounding_score"]
            < MIN_GROUNDING_SCORE
            or best["semantic_score"]
            < MIN_SEMANTIC_SCORE
        ):
            continue

        source = best[
            "source"
        ]

        grounded_claims.append(
            GroundedClaimAPI(
                text=claim,
                source_number=(
                    source.source_number
                ),
                grounding_score=round(
                    float(
                        best[
                            "grounding_score"
                        ]
                    ),
                    6,
                ),
                semantic_score=round(
                    float(
                        best[
                            "semantic_score"
                        ]
                    ),
                    6,
                ),
                lexical_score=round(
                    float(
                        best[
                            "lexical_score"
                        ]
                    ),
                    6,
                ),
            )
        )

    total_claims = len(
        claims
    )

    grounded_count = len(
        grounded_claims
    )

    coverage = (
        grounded_count
        / total_claims
        if total_claims
        else 0.0
    )

    answer = " ".join(
        _format_claim(
            claim.text,
            claim.source_number,
        )
        for claim
        in grounded_claims
    )

    return GroundingResult(
        answer=answer,
        claims=grounded_claims,
        coverage=round(
            coverage,
            4,
        ),
        total_claims=total_claims,
        removed_claims=(
            total_claims
            - grounded_count
        ),
    )
