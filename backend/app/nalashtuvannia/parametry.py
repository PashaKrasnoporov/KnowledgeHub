from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Parametry(BaseSettings):
    database_url: str | None = None

    db_host: str | None = None
    db_port: int | None = None
    db_name: str | None = None
    db_user: str | None = None
    db_password: str | None = None

    deployment_profile: str = "local"

    ml_enabled: bool = True
    llm_enabled: bool = True

    llm_backend: str = "local"

    llm_service_url: str = (
        "http://knowledgehub-llm.railway.internal:8080"
    )

    llm_service_timeout_seconds: float = 120.0

    cookie_secure: bool = False

    rag_local_model_name: str = (
        "Qwen/Qwen2.5-1.5B-Instruct"
    )

    rag_max_new_tokens: int = 96

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


parametry = Parametry()
