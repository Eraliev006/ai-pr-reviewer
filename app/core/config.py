from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class Config(BaseSettings):
    PROJECT_NAME: str = "AI PR Reviewer"
    API_V1_STR: str = "/api/v1"

    ENVIRONMENT: Literal["dev", "prod"] = "dev"

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )

config = Config()