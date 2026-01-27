"""Application configuration using environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    SECRET_KEY: str
    DATABASE_URL: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    model_config = SettingsConfigDict(env_file=".env")

    FIRST_ADMIN_EMAIL: str
    FIRST_ADMIN_PASSWORD: str


settings = Settings()  # type: ignore
