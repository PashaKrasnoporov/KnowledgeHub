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
    rag_max_new_tokens: int = 320

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


parametry = Parametry()
