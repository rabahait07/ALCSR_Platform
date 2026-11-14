from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from app.core.config import settings


def _enable_sqlite_foreign_keys(dbapi_connection: Any, _connection_record: Any) -> None:
    # SQLite ignores foreign key constraints (including ON DELETE CASCADE) unless enabled
    # on every connection.
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def build_engine(database_url: str, **engine_kwargs: Any) -> AsyncEngine:
    """Create an async engine, enabling foreign key enforcement when the database is SQLite."""
    new_engine = create_async_engine(database_url, pool_pre_ping=True, **engine_kwargs)
    if database_url.startswith("sqlite"):
        event.listen(new_engine.sync_engine, "connect", _enable_sqlite_foreign_keys)
    return new_engine


engine = build_engine(settings.DATABASE_URL)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding a session that is rolled back on error and always closed."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
