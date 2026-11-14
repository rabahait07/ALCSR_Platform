from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.challenge import CodingChallenge
from app.models.challenge_submission import ChallengeSubmission
from app.models.user import User
from app.schemas.challenge import (
    ChallengeSubmissionIn,
    ChallengeSubmissionOut,
    CodingChallengeDetailOut,
    CodingChallengeListOut,
)


class InvalidChallengeSubmissionError(Exception):
    """Raised when the reported test results do not fit the challenge's test cases."""


async def get_challenge_by_slug(db: AsyncSession, slug: str) -> CodingChallenge | None:
    result = await db.execute(select(CodingChallenge).where(CodingChallenge.slug == slug))
    return result.scalar_one_or_none()


async def list_challenges(db: AsyncSession, user: User) -> list[CodingChallengeListOut]:
    """Every challenge, with whether the user has solved it and how often they have tried."""
    challenges = (
        (await db.execute(select(CodingChallenge).order_by(CodingChallenge.id))).scalars().all()
    )
    passed_count = func.sum(case((ChallengeSubmission.passed.is_(True), 1), else_=0))
    stats = {
        challenge_id: (attempts, passes or 0)
        for challenge_id, attempts, passes in await db.execute(
            select(ChallengeSubmission.challenge_id, func.count(ChallengeSubmission.id), passed_count)
            .where(ChallengeSubmission.user_id == user.id)
            .group_by(ChallengeSubmission.challenge_id)
        )
    }

    listed: list[CodingChallengeListOut] = []
    for challenge in challenges:
        attempts, passes = stats.get(challenge.id, (0, 0))
        listed.append(
            CodingChallengeListOut.model_validate(challenge).model_copy(
                update={"solved": passes > 0, "attempts_count": attempts}
            )
        )
    return listed


async def get_challenge_detail(
    db: AsyncSession, user: User, slug: str
) -> CodingChallengeDetailOut | None:
    """The full challenge, plus the user's most recent code so they can carry on from it."""
    challenge = await get_challenge_by_slug(db, slug)
    if challenge is None:
        return None

    own_submissions = (ChallengeSubmission.user_id == user.id) & (
        ChallengeSubmission.challenge_id == challenge.id
    )
    latest_code = await db.scalar(
        select(ChallengeSubmission.code)
        .where(own_submissions)
        .order_by(ChallengeSubmission.submitted_at.desc(), ChallengeSubmission.id.desc())
        .limit(1)
    )
    solved_submission_id = await db.scalar(
        select(ChallengeSubmission.id)
        .where(own_submissions, ChallengeSubmission.passed.is_(True))
        .limit(1)
    )
    return CodingChallengeDetailOut.model_validate(challenge).model_copy(
        update={"solved": solved_submission_id is not None, "latest_code": latest_code}
    )


async def record_submission(
    db: AsyncSession, user: User, slug: str, payload: ChallengeSubmissionIn
) -> ChallengeSubmissionOut | None:
    """Store the code and the test results the browser reported. The code is never executed.

    Returns None when the challenge does not exist. Raises InvalidChallengeSubmissionError
    when ``total_tests`` is not the number of test cases the challenge actually has.
    """
    challenge = await get_challenge_by_slug(db, slug)
    if challenge is None:
        return None

    expected_tests = len(challenge.test_cases)
    if payload.total_tests != expected_tests:
        raise InvalidChallengeSubmissionError(
            f"total_tests must be {expected_tests}, the number of test cases for this challenge"
        )

    submission = ChallengeSubmission(
        user_id=user.id,
        challenge_id=challenge.id,
        code=payload.code,
        passed=payload.passed,
        passed_tests=payload.passed_tests,
        total_tests=payload.total_tests,
    )
    db.add(submission)
    await db.commit()
    return ChallengeSubmissionOut.model_validate(submission)
