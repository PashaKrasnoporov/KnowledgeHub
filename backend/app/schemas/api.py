from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class UserAPIResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime


class CollectionCreateAPI(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=2000,
    )

    @field_validator("name")
    @classmethod
    def normalize_name(
        cls,
        value: str,
    ) -> str:
        normalized = " ".join(
            value.strip().split()
        )

        if not normalized:
            raise ValueError(
                "Collection name cannot be empty."
            )

        return normalized

    @field_validator("description")
    @classmethod
    def normalize_description(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized = value.strip()

        return normalized or None


class CollectionUpdateAPI(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=2000,
    )

    @field_validator("name")
    @classmethod
    def normalize_name(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized = " ".join(
            value.strip().split()
        )

        if not normalized:
            raise ValueError(
                "Collection name cannot be empty."
            )

        return normalized

    @field_validator("description")
    @classmethod
    def normalize_description(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized = value.strip()

        return normalized or None


class CollectionAPIResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    user_id: int
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime


class DocumentAPIResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    collection_id: int
    original_name: str
    mime_type: str
    size_bytes: int
    processing_status: str
    processing_error: str | None
    created_at: datetime


class HealthAPIResponse(BaseModel):
    status: str
    service: str
    api_version: str


class CSRFApiResponse(BaseModel):
    csrf_token: str
