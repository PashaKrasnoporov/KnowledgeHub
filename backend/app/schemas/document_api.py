from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
)


class DocumentDetailAPIResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    collection_id: int
    original_name: str
    mime_type: str
    size_bytes: int
    extracted_text: str | None
    processing_status: str
    processing_error: str | None
    created_at: datetime
