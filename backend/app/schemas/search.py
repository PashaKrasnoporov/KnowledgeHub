from dataclasses import dataclass

from app.modeli.document import Document


@dataclass(frozen=True)
class DocumentSearchResult:
    document: Document
    score: float