from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
)


class RegisterAPIRequest(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=50,
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    password_confirmation: str = Field(
        min_length=8,
        max_length=128,
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
        "email",
        mode="before",
    )
    @classmethod
    def normalize_email(
        cls,
        value: str,
    ) -> str:
        if isinstance(value, str):
            return value.strip().lower()

        return value


class LoginAPIRequest(BaseModel):
    email: str = Field(
        min_length=1,
        max_length=255,
    )

    password: str = Field(
        min_length=1,
        max_length=128,
    )


class MessageAPIResponse(BaseModel):
    message: str
