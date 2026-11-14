from datetime import datetime, timedelta, timezone

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ChallengeSubmission, CodingChallenge, MCQAttempt, SyllabusTopic, User
from app.services.dashboard import percentage
from tests.conftest import auth_headers_for

BASE_TIME = datetime(2026, 11, 14, 12, 0, tzinfo=timezone.utc)
METRICS_URL = "/api/v1/dashboard/metrics"


def make_topic(spec_code: str, title: str) -> SyllabusTopic:
    section_code = spec_code.rsplit(".", 1)[0]
    return SyllabusTopic(
        paper=int(spec_code[0]),
        section_code=section_code,
        section_title=f"Section {section_code}",
        spec_code=spec_code,
        title=title,
        slug=f"topic-{spec_code.replace('.', '-')}",
    )


def make_challenge(topic: SyllabusTopic, slug: str, title: str) -> CodingChallenge:
    return CodingChallenge(
        topic=topic,
        slug=slug,
        title=title,
        difficulty="Easy",
        description="Write the function.",
        function_name="solve",
        starter_code="def solve():\n    pass\n",
        test_cases=[{"input_args": [], "expected": 1, "description": "returns 1"}],
    )


def attempt(
    user: User, topic: SyllabusTopic, score: int, total: int, minutes_ago: int
) -> MCQAttempt:
    return MCQAttempt(
        user=user,
        topic=topic,
        score=score,
        total_questions=total,
        completed_at=BASE_TIME - timedelta(minutes=minutes_ago),
    )


def submission(
    user: User, challenge: CodingChallenge, passed_tests: int, total: int, minutes_ago: int
) -> ChallengeSubmission:
    return ChallengeSubmission(
        user=user,
        challenge=challenge,
        code="def solve():\n    return 1\n",
        passed=passed_tests == total,
        passed_tests=passed_tests,
        total_tests=total,
        submitted_at=BASE_TIME - timedelta(minutes=minutes_ago),
    )


@pytest_asyncio.fixture
async def syllabus(session: AsyncSession) -> dict[str, SyllabusTopic]:
    """Four Paper 1 topics and two Paper 2 topics."""
    topics = {
        "1.1.1": make_topic("1.1.1", "Structure and function of the processor"),
        "1.1.2": make_topic("1.1.2", "Types of processor"),
        "1.1.3": make_topic("1.1.3", "Input, output and storage"),
        "1.2.1": make_topic("1.2.1", "Systems software"),
        "2.2.1": make_topic("2.2.1", "Programming techniques"),
        "2.3.1": make_topic("2.3.1", "Algorithms"),
    }
    session.add_all(topics.values())
    await session.commit()
    return topics


async def test_metrics_requires_authentication(client: AsyncClient) -> None:
    response = await client.get(METRICS_URL)

    assert response.status_code == 401


async def test_metrics_for_new_user_are_all_zero(
    client: AsyncClient, auth_headers: dict[str, str], syllabus: dict[str, SyllabusTopic]
) -> None:
    response = await client.get(METRICS_URL, headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == {
        "topics_practiced": 0,
        "total_topics": 6,
        "average_quiz_accuracy": 0.0,
        "challenges_solved": 0,
        "total_challenges": 0,
        "paper1_progress": {
            "paper": 1,
            "title": "Computer Systems",
            "topics_practiced": 0,
            "total_topics": 4,
            "percentage": 0.0,
        },
        "paper2_progress": {
            "paper": 2,
            "title": "Algorithms and Programming",
            "topics_practiced": 0,
            "total_topics": 2,
            "percentage": 0.0,
        },
        "recent_activity": [],
    }


async def test_metrics_with_no_syllabus_loaded(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    body = (await client.get(METRICS_URL, headers=auth_headers)).json()

    assert body["total_topics"] == 0
    assert body["paper1_progress"]["percentage"] == 0.0


async def test_metrics_count_only_the_current_users_activity(
    client: AsyncClient,
    session: AsyncSession,
    user: User,
    auth_headers: dict[str, str],
    syllabus: dict[str, SyllabusTopic],
) -> None:
    other_user = User(full_name="Other", email="other@alcsr.edu", hashed_password="x")
    stack = make_challenge(syllabus["2.3.1"], "stack", "Implement a Stack")
    queue = make_challenge(syllabus["2.3.1"], "queue", "Implement a Queue")
    search = make_challenge(syllabus["2.3.1"], "binary-search", "Binary Search")
    session.add_all(
        [
            other_user,
            stack,
            queue,
            search,
            # Two attempts on one topic count as one practiced topic: 7/10 then 9/10.
            attempt(user, syllabus["1.1.1"], 7, 10, minutes_ago=50),
            attempt(user, syllabus["1.1.1"], 9, 10, minutes_ago=40),
            attempt(user, syllabus["2.2.1"], 2, 5, minutes_ago=30),
            # stack: failed then solved twice (counts once). queue: only failed.
            submission(user, stack, 0, 1, minutes_ago=25),
            submission(user, stack, 1, 1, minutes_ago=20),
            submission(user, stack, 1, 1, minutes_ago=10),
            submission(user, queue, 0, 1, minutes_ago=5),
            # Someone else's activity must not leak into this user's dashboard.
            attempt(other_user, syllabus["1.2.1"], 10, 10, minutes_ago=1),
            submission(other_user, search, 1, 1, minutes_ago=1),
        ]
    )
    await session.commit()

    body = (await client.get(METRICS_URL, headers=auth_headers)).json()

    assert body["topics_practiced"] == 2
    assert body["total_topics"] == 6
    assert body["average_quiz_accuracy"] == 72.0  # (7 + 9 + 2) / (10 + 10 + 5)
    assert body["challenges_solved"] == 1
    assert body["total_challenges"] == 3
    assert body["paper1_progress"]["topics_practiced"] == 1
    assert body["paper1_progress"]["percentage"] == 25.0
    assert body["paper2_progress"]["topics_practiced"] == 1
    assert body["paper2_progress"]["percentage"] == 50.0

    activity = body["recent_activity"]
    assert len(activity) == 7
    assert activity[0] == {
        "activity_type": "challenge",
        "title": "Implement a Queue",
        "spec_code": "2.3.1",
        "score": 0,
        "total": 1,
        "occurred_at": activity[0]["occurred_at"],
    }
    assert activity[-1]["activity_type"] == "quiz"
    assert activity[-1]["title"] == "Structure and function of the processor"
    assert (activity[-1]["score"], activity[-1]["total"]) == (7, 10)
    timestamps = [datetime.fromisoformat(item["occurred_at"]) for item in activity]
    assert timestamps == sorted(timestamps, reverse=True)
    assert all(timestamp.tzinfo is not None for timestamp in timestamps)

    other_body = (await client.get(METRICS_URL, headers=auth_headers_for(other_user))).json()
    assert other_body["topics_practiced"] == 1
    assert other_body["challenges_solved"] == 1
    assert len(other_body["recent_activity"]) == 2


async def test_recent_activity_is_the_newest_eight_across_both_kinds(
    client: AsyncClient,
    session: AsyncSession,
    user: User,
    auth_headers: dict[str, str],
    syllabus: dict[str, SyllabusTopic],
) -> None:
    challenge = make_challenge(syllabus["2.3.1"], "stack", "Implement a Stack")
    session.add(challenge)
    # Twelve events, alternating kinds: even minutes are quizzes, odd are challenges.
    for minutes_ago in range(12):
        if minutes_ago % 2 == 0:
            session.add(attempt(user, syllabus["1.1.1"], 1, 1, minutes_ago=minutes_ago))
        else:
            session.add(submission(user, challenge, 1, 1, minutes_ago=minutes_ago))
    await session.commit()

    activity = (await client.get(METRICS_URL, headers=auth_headers)).json()["recent_activity"]

    assert len(activity) == 8
    assert [item["activity_type"] for item in activity] == ["quiz", "challenge"] * 4
    newest = datetime.fromisoformat(activity[0]["occurred_at"])
    oldest = datetime.fromisoformat(activity[-1]["occurred_at"])
    assert newest == BASE_TIME
    assert oldest == BASE_TIME - timedelta(minutes=7)


def test_percentage_handles_zero_total_and_rounds() -> None:
    assert percentage(0, 0) == 0.0
    assert percentage(1, 3) == 33.3
    assert percentage(5, 5) == 100.0
