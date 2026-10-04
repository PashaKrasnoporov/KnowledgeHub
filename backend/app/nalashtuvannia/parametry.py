from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Parametry(BaseSettings):
    # Local development can keep the five DB_* variables.
    # Railway can use one DATABASE_URL reference from PostgreSQL.
    database_url: str | None = None

    db_host: str | None = None
    db_port: int | None = None
    db_name: str | None = None
    db_user: str | None = None
    db_password: str | None = None

    deployment_profile: str = "local"
    ml_enabled: bool = True
    cookie_secure: bool = False

    rag_local_model_name: str = (
        "Qwen/Qwen2.5-1.5B-Instruct"
    )

    # Stable baseline: local LLM remains experimental and concise.
    # The recommended user path is the fast extractive research mode.
    rag_max_new_tokens: int = 96

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


parametry = Parametry()
