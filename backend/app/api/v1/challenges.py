from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.challenge import (
    ChallengeSubmissionIn,
    ChallengeSubmissionOut,
    CodingChallengeDetailOut,
    CodingChallengeListOut,
)
from app.services import challenges as challenge_service

router = APIRouter(prefix="/challenges", tags=["challenges"])

ChallengeSlug = Annotated[str, Path(max_length=255, examples=["fizzbuzz"])]


def _challenge_not_found(slug: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Challenge {slug} not found"
    )


@router.get("", response_model=list[CodingChallengeListOut])
async def read_challenges(
    current_user: CurrentUser, db: DbSession
) -> list[CodingChallengeListOut]:
    """Every coding challenge with the user's solved status and attempt count."""
    return await challenge_service.list_challenges(db, current_user)


@router.get("/{slug}", response_model=CodingChallengeDetailOut)
async def read_challenge(
    slug: ChallengeSlug, current_user: CurrentUser, db: DbSession
) -> CodingChallengeDetailOut:
    """The challenge, its test cases for the browser runner and the user's latest code."""
    challenge = await challenge_service.get_challenge_detail(db, current_user, slug)
    if challenge is None:
        raise _challenge_not_found(slug)
    return challenge


@router.post(
    "/{slug}/submit", response_model=ChallengeSubmissionOut, status_code=status.HTTP_201_CREATED
)
async def submit_challenge(
    slug: ChallengeSlug, payload: ChallengeSubmissionIn, current_user: CurrentUser, db: DbSession
) -> ChallengeSubmissionOut:
    """Save the code and the test results reported by the in-browser Pyodide runner."""
    try:
        submission = await challenge_service.record_submission(db, current_user, slug, payload)
    except challenge_service.InvalidChallengeSubmissionError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from None
    if submission is None:
        raise _challenge_not_found(slug)
    return submission
