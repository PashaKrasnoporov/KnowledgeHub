from pydantic import BaseModel


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
