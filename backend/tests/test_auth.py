from datetime import timedelta

import pytest
from httpx import AsyncClient
from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models import User
from tests.conftest import auth_headers_for

SIGNUP = {"full_name": "Grace Hopper", "email": "grace@alcsr.edu", "password": "c0bol-rocks"}


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


# --- Security utilities --------------------------------------------------------------------


def test_password_hash_round_trip() -> None:
    hashed = get_password_hash("c0bol-rocks")

    assert hashed != "c0bol-rocks"
    assert verify_password("c0bol-rocks", hashed) is True
    assert verify_password("wrong-password", hashed) is False


def test_verify_password_is_false_for_malformed_hash() -> None:
    assert verify_password("anything", "not-a-real-hash") is False


def test_access_token_carries_subject_and_default_expiry() -> None:
    token = create_access_token({"sub": "42"})

    claims = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    assert claims["sub"] == "42"
    assert claims["exp"] - claims["iat"] == settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60


# --- Signup --------------------------------------------------------------------------------


async def test_signup_creates_user_and_logs_them_in(
    client: AsyncClient, session: AsyncSession
) -> None:
    response = await client.post("/api/v1/auth/signup", json=SIGNUP)

    assert response.status_code == 201
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["user"]["email"] == "grace@alcsr.edu"
    assert body["user"]["full_name"] == "Grace Hopper"
    assert "password" not in response.text

    stored = (await session.execute(select(User))).scalar_one()
    assert stored.hashed_password != SIGNUP["password"]
    assert verify_password(SIGNUP["password"], stored.hashed_password)

    me = await client.get("/api/v1/auth/me", headers=bearer(body["access_token"]))
    assert me.status_code == 200
    assert me.json()["id"] == stored.id


async def test_signup_rejects_duplicate_email_ignoring_case(
    client: AsyncClient, user: User
) -> None:
    response = await client.post(
        "/api/v1/auth/signup", json=SIGNUP | {"email": user.email.upper()}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "An account with this email already exists"


@pytest.mark.parametrize(
    "overrides",
    [{"email": "not-an-email"}, {"password": "short"}, {"full_name": ""}],
    ids=["bad-email", "short-password", "empty-name"],
)
async def test_signup_rejects_invalid_input(client: AsyncClient, overrides: dict[str, str]) -> None:
    response = await client.post("/api/v1/auth/signup", json=SIGNUP | overrides)

    assert response.status_code == 422


# --- Login ---------------------------------------------------------------------------------


async def test_login_with_json_credentials(client: AsyncClient) -> None:
    await client.post("/api/v1/auth/signup", json=SIGNUP)

    response = await client.post(
        "/api/v1/auth/login", json={"email": "Grace@ALCSR.edu", "password": SIGNUP["password"]}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["user"]["email"] == "grace@alcsr.edu"
    me = await client.get("/api/v1/auth/me", headers=bearer(body["access_token"]))
    assert me.status_code == 200


async def test_login_failures_are_indistinguishable(client: AsyncClient) -> None:
    await client.post("/api/v1/auth/signup", json=SIGNUP)

    wrong_password = await client.post(
        "/api/v1/auth/login", json={"email": SIGNUP["email"], "password": "wrong-password"}
    )
    unknown_email = await client.post(
        "/api/v1/auth/login", json={"email": "nobody@alcsr.edu", "password": SIGNUP["password"]}
    )

    assert wrong_password.status_code == unknown_email.status_code == 401
    assert wrong_password.json() == unknown_email.json()
    assert wrong_password.headers["www-authenticate"] == "Bearer"


# --- Protected routes ----------------------------------------------------------------------


async def test_me_returns_current_user_without_password_hash(
    client: AsyncClient, user: User, auth_headers: dict[str, str]
) -> None:
    response = await client.get("/api/v1/auth/me", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"id", "full_name", "email", "created_at"}
    assert body["email"] == user.email
    assert body["created_at"].endswith(("Z", "+00:00"))


async def test_me_requires_a_token(client: AsyncClient) -> None:
    response = await client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


async def test_me_rejects_bad_tokens(client: AsyncClient, user: User) -> None:
    subject = str(user.id)
    bad_tokens = {
        "garbage": "not.a.jwt",
        "expired": create_access_token({"sub": subject}, expires_delta=timedelta(minutes=-5)),
        "wrong key": jwt.encode({"sub": subject}, "some-other-key", algorithm=settings.ALGORITHM),
        "no subject": create_access_token({}),
        "non-numeric subject": create_access_token({"sub": "admin"}),
        "unknown user": create_access_token({"sub": "999999"}),
    }

    for label, token in bad_tokens.items():
        response = await client.get("/api/v1/auth/me", headers=bearer(token))
        assert response.status_code == 401, label
        assert response.json()["detail"] == "Could not validate credentials", label


async def test_token_stops_working_when_user_is_deleted(
    client: AsyncClient, session: AsyncSession, user: User
) -> None:
    headers = auth_headers_for(user)
    await session.delete(user)
    await session.commit()

    response = await client.get("/api/v1/auth/me", headers=headers)

    assert response.status_code == 401
