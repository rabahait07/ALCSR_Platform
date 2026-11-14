from functools import lru_cache
from typing import Literal

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

LOCAL_DEVELOPMENT_SECRET_KEY = "alcsr-local-development-signing-key-never-use-in-production"

_ASYNC_DRIVERS = {
    "postgres://": "postgresql+asyncpg://",
    "postgresql://": "postgresql+asyncpg://",
    "sqlite://": "sqlite+aiosqlite://",
}


class Settings(BaseSettings):
    """Application settings, overridable through environment variables or backend/.env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "ALCSR API"
    ENVIRONMENT: Literal["development", "test", "production"] = "development"

    # SQLite by default; set DATABASE_URL to a PostgreSQL URL to switch databases.
    DATABASE_URL: str = "sqlite+aiosqlite:///./alcsr.db"

    SECRET_KEY: str = LOCAL_DEVELOPMENT_SECRET_KEY
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    @field_validator("DATABASE_URL")
    @classmethod
    def use_async_driver(cls, value: str) -> str:
        """Accept plain postgres/sqlite URLs (as issued by most hosts) and select the async driver."""
        for prefix, async_prefix in _ASYNC_DRIVERS.items():
            if value.startswith(prefix):
                return async_prefix + value[len(prefix):]
        return value

    @model_validator(mode="after")
    def require_real_secret_in_production(self) -> "Settings":
        if self.ENVIRONMENT == "production" and self.SECRET_KEY == LOCAL_DEVELOPMENT_SECRET_KEY:
            raise ValueError("SECRET_KEY must be set to a unique value when ENVIRONMENT=production")
        return self

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
