from pydantic_settings import BaseSettings, SettingsConfigDict


class Parametry(BaseSettings):
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


parametry = Parametry()