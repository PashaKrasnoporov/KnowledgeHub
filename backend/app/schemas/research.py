from typing import Literal

from pydantic import (
    BaseModel,
    Field,
)


class ResearchSourceAPI(BaseModel):
    source_number: int
    document_id: int
    original_name: str
    chunk_index: int
    excerpt: str
    score: float
    semantic_score: float
    lexical_score: float

    # Internal-only data reused during claim grounding.
    # It is never serialized to the browser.
    embedding: list[float] = Field(
        default_factory=list,
        exclude=True,
        repr=False,
    )


class ResearchAnswerPointAPI(BaseModel):
    text: str
    source_number: int


class ResearchResponseAPI(BaseModel):
    question: str
    mode: str
    count: int
    answer_points: list[ResearchAnswerPointAPI]
    sources: list[ResearchSourceAPI]


class ResearchGenerateRequestAPI(BaseModel):
    question: str = Field(
        min_length=3,
        max_length=500,
    )

    limit: int = Field(
        default=4,
        ge=1,
        le=8,
    )

    max_new_tokens: int | None = Field(
        default=None,
        ge=64,
        le=320,
    )

    response_language: Literal[
        "uk",
        "auto",
    ] = "uk"


class GroundedClaimAPI(BaseModel):
    text: str
    source_number: int
    grounding_score: float
    semantic_score: float
    lexical_score: float


class ResearchGeneratedResponseAPI(
    ResearchResponseAPI
):
    generated_answer: str
    generation_provider: str
    generation_model: str | None = None

    response_language: str = "uk"

    language_rewrite_used: bool = False
    language_rewrite_passes: int = 0

    language_quality_passed: bool = True
    language_quality_score: int = 100

    language_quality_issues: list[str] = Field(
        default_factory=list
    )

    language_quality_warnings: list[str] = Field(
        default_factory=list
    )

    grounded_claims: list[
        GroundedClaimAPI
    ] = Field(
        default_factory=list
    )

    grounding_coverage: float = 0.0
    removed_claims: int = 0

    evidence_confidence: float = 0.0
    insufficient_evidence: bool = False

    fallback_used: bool = False
    generation_error: str | None = None

    # Server-side timing, visible to the user for real performance checks.
    timings_ms: dict[str, float] = Field(
        default_factory=dict
    )
    model_cold_start: bool = False
