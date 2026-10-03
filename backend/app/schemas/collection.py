from pydantic import (
    BaseModel,
    Field,
    field_validator,
)


class CollectionCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
    )

    @field_validator(
        "name",
        mode="before",
    )
    @classmethod
    def normalize_name(
        cls,
        value: str,
    ) -> str:
        if isinstance(value, str):
            return " ".join(
                value.strip().split()
            )

        return value

    @field_validator(
        "description",
        mode="before",
    )
    @classmethod
    def normalize_description(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        if isinstance(value, str):
            value = value.strip()

            if not value:
                return None

        return value


class CollectionUpdate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
    )

    @field_validator(
        "name",
        mode="before",
    )
    @classmethod
    def normalize_name(
        cls,
        value: str,
    ) -> str:
        if isinstance(value, str):
            return " ".join(
                value.strip().split()
            )

        return value

    @field_validator(
        "description",
        mode="before",
    )
    @classmethod
    def normalize_description(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        if isinstance(value, str):
            value = value.strip()

            if not value:
                return None

        return value