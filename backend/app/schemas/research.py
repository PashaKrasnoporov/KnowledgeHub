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
        default=5,
        ge=1,
        le=8,
    )

    max_new_tokens: int | None = Field(
        default=None,
        ge=80,
        le=512,
    )


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

    grounded_claims: list[
        GroundedClaimAPI
    ] = []

    grounding_coverage: float = 0.0
    removed_claims: int = 0

    fallback_used: bool = False
    generation_error: str | None = None
