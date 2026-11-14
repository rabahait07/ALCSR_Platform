from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ChallengeSubmission, CodingChallenge, SyllabusTopic, User
from tests.conftest import auth_headers_for

BASE_TIME = datetime(2026, 11, 14, 12, 0, tzinfo=timezone.utc)
TEST_CASES = [
    {"input_args": [1], "expected": 2, "description": "doubles 1"},
    {"input_args": [5], "expected": 10, "description": "doubles 5"},
]
PASSING = {"code": "def double(n):\n    return n * 2\n", "passed": True, "passed_tests": 2,
           "total_tests": 2}
FAILING = {"code": "def double(n):\n    return n\n", "passed": False, "passed_tests": 0,
           "total_tests": 2}


def make_challenge(topic: SyllabusTopic, slug: str, title: str, difficulty: str) -> CodingChallenge:
    return CodingChallenge(
        topic=topic,
        slug=slug,
        title=title,
        difficulty=difficulty,
        description=f"## {title}\n\nWrite the function.",
        function_name="double",
        starter_code="def double(n):\n    pass\n",
        test_cases=TEST_CASES,
    )


def stored_submission(
    user: User, challenge: CodingChallenge, code: str, passed: bool, minutes_ago: int
) -> ChallengeSubmission:
    return ChallengeSubmission(
        user=user,
        challenge=challenge,
        code=code,
        passed=passed,
        passed_tests=2 if passed else 0,
        total_tests=2,
        submitted_at=BASE_TIME - timedelta(minutes=minutes_ago),
    )


@pytest_asyncio.fixture
async def challenges(session: AsyncSession) -> dict[str, CodingChallenge]:
    topic = SyllabusTopic(
        paper=2,
        section_code="2.2",
        section_title="2.2 Problem solving and programming",
        spec_code="2.2.1",
        title="Programming techniques",
        slug="programming-techniques",
    )
    created = {
        "double": make_challenge(topic, "double", "Double It", "Easy"),
        "triple": make_challenge(topic, "triple", "Triple It", "Hard"),
    }
    session.add_all([topic, *created.values()])
    await session.commit()
    return created


# --- Authentication ------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("GET", "/api/v1/challenges"),
        ("GET", "/api/v1/challenges/double"),
        ("POST", "/api/v1/challenges/double/submit"),
    ],
)
async def test_challenge_endpoints_require_a_token(
    client: AsyncClient, method: str, path: str
) -> None:
    response = await client.request(method, path, json=PASSING)

    assert response.status_code == 401


# --- Listing -------------------------------------------------------------------------------


async def test_list_shows_every_challenge_unsolved_for_a_new_user(
    client: AsyncClient, auth_headers: dict[str, str], challenges: dict[str, CodingChallenge]
) -> None:
    response = await client.get("/api/v1/challenges", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": challenges["double"].id,
            "topic_id": challenges["double"].topic_id,
            "slug": "double",
            "title": "Double It",
            "difficulty": "Easy",
            "solved": False,
            "attempts_count": 0,
        },
        {
            "id": challenges["triple"].id,
            "topic_id": challenges["triple"].topic_id,
            "slug": "triple",
            "title": "Triple It",
            "difficulty": "Hard",
            "solved": False,
            "attempts_count": 0,
        },
    ]


async def test_list_reports_solved_and_attempts_for_the_current_user_only(
    client: AsyncClient,
    session: AsyncSession,
    user: User,
    auth_headers: dict[str, str],
    challenges: dict[str, CodingChallenge],
) -> None:
    other_user = User(full_name="Other", email="other@alcsr.edu", hashed_password="x")
    session.add_all(
        [
            other_user,
            stored_submission(user, challenges["double"], "v1", passed=False, minutes_ago=30),
            stored_submission(user, challenges["double"], "v2", passed=True, minutes_ago=20),
            stored_submission(user, challenges["double"], "v3", passed=False, minutes_ago=10),
            stored_submission(user, challenges["triple"], "t1", passed=False, minutes_ago=5),
            stored_submission(other_user, challenges["triple"], "o1", passed=True, minutes_ago=1),
        ]
    )
    await session.commit()

    mine = (await client.get("/api/v1/challenges", headers=auth_headers)).json()
    theirs = (
        await client.get("/api/v1/challenges", headers=auth_headers_for(other_user))
    ).json()

    assert [(item["slug"], item["solved"], item["attempts_count"]) for item in mine] == [
        ("double", True, 3),
        ("triple", False, 1),
    ]
    assert [(item["slug"], item["solved"], item["attempts_count"]) for item in theirs] == [
        ("double", False, 0),
        ("triple", True, 1),
    ]


# --- Detail --------------------------------------------------------------------------------


async def test_detail_includes_everything_the_browser_runner_needs(
    client: AsyncClient, auth_headers: dict[str, str], challenges: dict[str, CodingChallenge]
) -> None:
    response = await client.get("/api/v1/challenges/double", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["slug"] == "double"
    assert body["function_name"] == "double"
    assert body["starter_code"] == "def double(n):\n    pass\n"
    assert body["description"].startswith("## Double It")
    assert body["test_cases"] == TEST_CASES
    assert body["solved"] is False
    assert body["latest_code"] is None


async def test_detail_returns_the_users_latest_code(
    client: AsyncClient,
    session: AsyncSession,
    user: User,
    auth_headers: dict[str, str],
    challenges: dict[str, CodingChallenge],
) -> None:
    other_user = User(full_name="Other", email="other@alcsr.edu", hashed_password="x")
    session.add_all(
        [
            other_user,
            stored_submission(user, challenges["double"], "first try", passed=True, minutes_ago=30),
            stored_submission(user, challenges["double"], "latest try", passed=False, minutes_ago=5),
            stored_submission(other_user, challenges["double"], "not mine", passed=True, minutes_ago=1),
        ]
    )
    await session.commit()

    body = (await client.get("/api/v1/challenges/double", headers=auth_headers)).json()

    # The newest code is returned even though it failed; solved reflects the earlier pass.
    assert body["latest_code"] == "latest try"
    assert body["solved"] is True


async def test_detail_for_unknown_challenge_is_404(
    client: AsyncClient, auth_headers: dict[str, str], challenges: dict[str, CodingChallenge]
) -> None:
    response = await client.get("/api/v1/challenges/nope", headers=auth_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Challenge nope not found"


# --- Submitting ----------------------------------------------------------------------------


async def test_submit_saves_the_submission(
    client: AsyncClient,
    session: AsyncSession,
    user: User,
    auth_headers: dict[str, str],
    challenges: dict[str, CodingChallenge],
) -> None:
    response = await client.post(
        "/api/v1/challenges/double/submit", json=PASSING, headers=auth_headers
    )

    assert response.status_code == 201
    body = response.json()
    assert body["challenge_id"] == challenges["double"].id
    assert body["code"] == PASSING["code"]
    assert (body["passed"], body["passed_tests"], body["total_tests"]) == (True, 2, 2)
    assert body["submitted_at"].endswith(("Z", "+00:00"))

    stored = (await session.execute(select(ChallengeSubmission))).scalar_one()
    assert stored.id == body["id"]
    assert (stored.user_id, stored.challenge_id) == (user.id, challenges["double"].id)
    assert stored.code == PASSING["code"]


async def test_submitting_updates_list_detail_and_dashboard(
    client: AsyncClient, auth_headers: dict[str, str], challenges: dict[str, CodingChallenge]
) -> None:
    await client.post("/api/v1/challenges/double/submit", json=FAILING, headers=auth_headers)

    listed = (await client.get("/api/v1/challenges", headers=auth_headers)).json()
    assert (listed[0]["solved"], listed[0]["attempts_count"]) == (False, 1)

    await client.post("/api/v1/challenges/double/submit", json=PASSING, headers=auth_headers)

    listed = (await client.get("/api/v1/challenges", headers=auth_headers)).json()
    detail = (await client.get("/api/v1/challenges/double", headers=auth_headers)).json()
    metrics = (await client.get("/api/v1/dashboard/metrics", headers=auth_headers)).json()
    assert (listed[0]["solved"], listed[0]["attempts_count"]) == (True, 2)
    assert detail["latest_code"] == PASSING["code"]
    assert detail["solved"] is True
    assert (metrics["challenges_solved"], metrics["total_challenges"]) == (1, 2)


async def test_submit_rejects_a_test_count_that_does_not_match_the_challenge(
    client: AsyncClient,
    session: AsyncSession,
    auth_headers: dict[str, str],
    challenges: dict[str, CodingChallenge],
) -> None:
    claimed = {"code": "pass", "passed": True, "passed_tests": 1, "total_tests": 1}

    response = await client.post(
        "/api/v1/challenges/double/submit", json=claimed, headers=auth_headers
    )

    assert response.status_code == 400
    assert "total_tests must be 2" in response.json()["detail"]
    assert (await session.execute(select(ChallengeSubmission))).first() is None


@pytest.mark.parametrize(
    "overrides",
    [{"passed": True, "passed_tests": 1}, {"passed_tests": 3}, {"code": ""}],
    ids=["passed-with-failures", "more-passed-than-total", "empty-code"],
)
async def test_submit_rejects_inconsistent_results(
    client: AsyncClient,
    auth_headers: dict[str, str],
    challenges: dict[str, CodingChallenge],
    overrides: dict[str, object],
) -> None:
    response = await client.post(
        "/api/v1/challenges/double/submit", json=FAILING | overrides, headers=auth_headers
    )

    assert response.status_code == 422


async def test_submit_to_unknown_challenge_is_404(
    client: AsyncClient, auth_headers: dict[str, str], challenges: dict[str, CodingChallenge]
) -> None:
    response = await client.post(
        "/api/v1/challenges/nope/submit", json=PASSING, headers=auth_headers
    )

    assert response.status_code == 404
