from collections.abc import AsyncGenerator
from pathlib import Path

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.core.database import Base, build_engine, get_db
from app.core.security import create_access_token
from app.main import app
from app.models import User


@pytest_asyncio.fixture
async def engine(tmp_path: Path) -> AsyncGenerator[AsyncEngine, None]:
    """A fresh SQLite database file per test, with every table created."""
    database_path = (tmp_path / "test.db").as_posix()
    test_engine = build_engine(f"sqlite+aiosqlite:///{database_path}")
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield test_engine
    await test_engine.dispose()


@pytest_asyncio.fixture
async def session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """A session for arranging and inspecting data directly in the test database."""
    async with async_sessionmaker(engine, expire_on_commit=False)() as db_session:
        yield db_session


@pytest_asyncio.fixture
async def client(engine: AsyncEngine) -> AsyncGenerator[AsyncClient, None]:
    """An HTTP client for the app, with get_db pointed at the test database."""
    session_factory = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as db_session:
            yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as test_client:
        yield test_client
    app.dependency_overrides.pop(get_db, None)


@pytest_asyncio.fixture
async def user(session: AsyncSession) -> User:
    """A stored user. The hash is not a real one, so use ``auth_headers`` rather than logging in."""
    stored_user = User(
        full_name="Ada Lovelace", email="ada@alcsr.edu", hashed_password="not-a-real-hash"
    )
    session.add(stored_user)
    await session.commit()
    return stored_user


def auth_headers_for(user: User) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token({'sub': str(user.id)})}"}


@pytest_asyncio.fixture
async def auth_headers(user: User) -> dict[str, str]:
    return auth_headers_for(user)
