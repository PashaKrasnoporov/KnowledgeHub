from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Parametry(BaseSettings):
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    rag_local_model_name: str = (
        "Qwen/Qwen2.5-1.5B-Instruct"
    )

    # The answer is intentionally short: 2–3 grounded sentences.
    # Lowering the token budget reduces CPU generation latency sharply.
    rag_max_new_tokens: int = 160

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


parametry = Parametry()
