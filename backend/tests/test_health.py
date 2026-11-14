import pytest
from httpx import AsyncClient

from app.core.config import LOCAL_DEVELOPMENT_SECRET_KEY, Settings


async def test_health_check_returns_ok(client: AsyncClient) -> None:
    response = await client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.parametrize("origin", ["http://localhost:5173", "http://127.0.0.1:5173"])
async def test_cors_allows_frontend_dev_origins(client: AsyncClient, origin: str) -> None:
    response = await client.options(
        "/api/health",
        headers={"Origin": origin, "Access-Control-Request-Method": "GET"},
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == origin


async def test_cors_rejects_unknown_origin(client: AsyncClient) -> None:
    response = await client.options(
        "/api/health",
        headers={"Origin": "http://evil.example", "Access-Control-Request-Method": "GET"},
    )

    assert "access-control-allow-origin" not in response.headers


def test_settings_defaults() -> None:
    settings = Settings(_env_file=None)

    assert settings.DATABASE_URL == "sqlite+aiosqlite:///./alcsr.db"
    assert settings.ALGORITHM == "HS256"
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 1440


@pytest.mark.parametrize(
    "url",
    ["postgres://u:p@db:5432/alcsr", "postgresql://u:p@db:5432/alcsr"],
)
def test_postgres_urls_use_asyncpg_driver(url: str) -> None:
    settings = Settings(_env_file=None, DATABASE_URL=url)

    assert settings.DATABASE_URL == "postgresql+asyncpg://u:p@db:5432/alcsr"
    assert settings.is_sqlite is False


def test_production_requires_explicit_secret_key() -> None:
    with pytest.raises(ValueError, match="SECRET_KEY"):
        Settings(_env_file=None, ENVIRONMENT="production", SECRET_KEY=LOCAL_DEVELOPMENT_SECRET_KEY)
