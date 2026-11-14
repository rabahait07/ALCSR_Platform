from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.challenge import CodingChallenge
from app.models.challenge_submission import ChallengeSubmission
from app.models.quiz_attempt import MCQAttempt
from app.models.topic import PAPER_TITLES, SyllabusTopic
from app.models.user import User
from app.schemas.dashboard import DashboardMetricsResponse, PaperProgressOut, RecentActivityOut

RECENT_ACTIVITY_LIMIT = 8


def percentage(part: int, whole: int) -> float:
    """``part`` as a percentage of ``whole`` to one decimal place; 0 when ``whole`` is 0."""
    return round(part / whole * 100, 1) if whole else 0.0


async def _topic_counts_by_paper(db: AsyncSession) -> dict[int, int]:
    result = await db.execute(
        select(SyllabusTopic.paper, func.count(SyllabusTopic.id)).group_by(SyllabusTopic.paper)
    )
    return {paper: count for paper, count in result.all()}


async def _practiced_counts_by_paper(db: AsyncSession, user_id: int) -> dict[int, int]:
    result = await db.execute(
        select(SyllabusTopic.paper, func.count(distinct(MCQAttempt.topic_id)))
        .join(MCQAttempt, MCQAttempt.topic_id == SyllabusTopic.id)
        .where(MCQAttempt.user_id == user_id)
        .group_by(SyllabusTopic.paper)
    )
    return {paper: count for paper, count in result.all()}


async def _average_quiz_accuracy(db: AsyncSession, user_id: int) -> float:
    result = await db.execute(
        select(
            func.coalesce(func.sum(MCQAttempt.score), 0),
            func.coalesce(func.sum(MCQAttempt.total_questions), 0),
        ).where(MCQAttempt.user_id == user_id)
    )
    correct, answered = result.one()
    return percentage(int(correct), int(answered))


async def _recent_quiz_activity(db: AsyncSession, user_id: int) -> list[RecentActivityOut]:
    result = await db.execute(
        select(
            SyllabusTopic.title,
            SyllabusTopic.spec_code,
            MCQAttempt.score,
            MCQAttempt.total_questions,
            MCQAttempt.completed_at,
        )
        .join(SyllabusTopic, MCQAttempt.topic_id == SyllabusTopic.id)
        .where(MCQAttempt.user_id == user_id)
        .order_by(MCQAttempt.completed_at.desc(), MCQAttempt.id.desc())
        .limit(RECENT_ACTIVITY_LIMIT)
    )
    return [
        RecentActivityOut(
            activity_type="quiz",
            title=title,
            spec_code=spec_code,
            score=score,
            total=total,
            occurred_at=occurred_at,
        )
        for title, spec_code, score, total, occurred_at in result.all()
    ]


async def _recent_challenge_activity(db: AsyncSession, user_id: int) -> list[RecentActivityOut]:
    result = await db.execute(
        select(
            CodingChallenge.title,
            SyllabusTopic.spec_code,
            ChallengeSubmission.passed_tests,
            ChallengeSubmission.total_tests,
            ChallengeSubmission.submitted_at,
        )
        .join(CodingChallenge, ChallengeSubmission.challenge_id == CodingChallenge.id)
        .join(SyllabusTopic, CodingChallenge.topic_id == SyllabusTopic.id)
        .where(ChallengeSubmission.user_id == user_id)
        .order_by(ChallengeSubmission.submitted_at.desc(), ChallengeSubmission.id.desc())
        .limit(RECENT_ACTIVITY_LIMIT)
    )
    return [
        RecentActivityOut(
            activity_type="challenge",
            title=title,
            spec_code=spec_code,
            score=score,
            total=total,
            occurred_at=occurred_at,
        )
        for title, spec_code, score, total, occurred_at in result.all()
    ]


async def get_dashboard_metrics(db: AsyncSession, user: User) -> DashboardMetricsResponse:
    """Progress metrics for one user. Every figure counts only that user's own activity."""
    topic_counts = await _topic_counts_by_paper(db)
    practiced_counts = await _practiced_counts_by_paper(db, user.id)

    challenges_solved = await db.scalar(
        select(func.count(distinct(ChallengeSubmission.challenge_id))).where(
            ChallengeSubmission.user_id == user.id, ChallengeSubmission.passed.is_(True)
        )
    )
    total_challenges = await db.scalar(select(func.count(CodingChallenge.id)))

    # The newest items overall must be among the newest of each kind, so merging the two
    # limited lists and trimming again gives the correct combined feed.
    recent_activity = sorted(
        await _recent_quiz_activity(db, user.id) + await _recent_challenge_activity(db, user.id),
        key=lambda activity: activity.occurred_at,
        reverse=True,
    )[:RECENT_ACTIVITY_LIMIT]

    def paper_progress(paper: int) -> PaperProgressOut:
        practiced = practiced_counts.get(paper, 0)
        total = topic_counts.get(paper, 0)
        return PaperProgressOut(
            paper=paper,
            title=PAPER_TITLES[paper],
            topics_practiced=practiced,
            total_topics=total,
            percentage=percentage(practiced, total),
        )

    return DashboardMetricsResponse(
        topics_practiced=sum(practiced_counts.values()),
        total_topics=sum(topic_counts.values()),
        average_quiz_accuracy=await _average_quiz_accuracy(db, user.id),
        challenges_solved=challenges_solved or 0,
        total_challenges=total_challenges or 0,
        paper1_progress=paper_progress(1),
        paper2_progress=paper_progress(2),
        recent_activity=recent_activity,
    )
