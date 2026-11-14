import secrets
from functools import lru_cache

from fastapi.concurrency import run_in_threadpool
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import Token, UserCreate, UserLogin, UserResponse


class EmailAlreadyRegisteredError(Exception):
    """Raised when signing up with an email that already has an account."""


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def register_user(db: AsyncSession, payload: UserCreate) -> User:
    if await get_user_by_email(db, payload.email) is not None:
        raise EmailAlreadyRegisteredError(payload.email)

    # bcrypt is deliberately slow, so hash off the event loop.
    hashed_password = await run_in_threadpool(get_password_hash, payload.password)
    user = User(full_name=payload.full_name, email=payload.email, hashed_password=hashed_password)
    db.add(user)
    try:
        await db.commit()
    except IntegrityError:
        # Another request registered the same email between the check and the insert.
        await db.rollback()
        raise EmailAlreadyRegisteredError(payload.email) from None
    return user


@lru_cache(maxsize=1)
def _unmatchable_hash() -> str:
    return get_password_hash(secrets.token_urlsafe(32))


def _check_password(password: str, hashed_password: str | None) -> bool:
    if hashed_password is None:
        # No such account: still spend the time of a real check so that response timing
        # does not reveal which emails are registered.
        verify_password(password, _unmatchable_hash())
        return False
    return verify_password(password, hashed_password)


async def authenticate_user(db: AsyncSession, credentials: UserLogin) -> User | None:
    user = await get_user_by_email(db, credentials.email)
    hashed_password = user.hashed_password if user is not None else None
    is_valid = await run_in_threadpool(_check_password, credentials.password, hashed_password)
    return user if is_valid else None


def build_token(user: User) -> Token:
    access_token = create_access_token({"sub": str(user.id)})
    return Token(access_token=access_token, user=UserResponse.model_validate(user))
