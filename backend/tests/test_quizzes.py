import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import MCQAttempt, MCQQuestion, SyllabusTopic, User
from tests.conftest import auth_headers_for

SECRET_EXPLANATION = "EXPLANATION-MUST-NOT-LEAK"


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


def make_question(topic: SyllabusTopic, number: int, correct_index: int) -> MCQQuestion:
    return MCQQuestion(
        topic=topic,
        question_text=f"Question {number}?",
        code_snippet="x = 1" if number == 1 else None,
        options=["Option A", "Option B", "Option C", "Option D"],
        correct_index=correct_index,
        explanation=f"{SECRET_EXPLANATION} {number}",
    )


@pytest_asyncio.fixture
async def quiz_data(session: AsyncSession) -> dict[str, SyllabusTopic]:
    """1.1.1 has twelve questions, 1.1.2 has three, 2.1.1 has none."""
    topics = {
        "2.1.1": make_topic("2.1.1", "Thinking abstractly"),
        "1.1.2": make_topic("1.1.2", "Types of processor"),
        "1.1.1": make_topic("1.1.1", "Structure and function of the processor"),
    }
    session.add_all(topics.values())
    session.add_all(make_question(topics["1.1.1"], n, correct_index=n % 4) for n in range(1, 13))
    session.add_all(make_question(topics["1.1.2"], n, correct_index=2) for n in range(1, 4))
    await session.commit()
    return topics


async def correct_answers(session: AsyncSession, spec_code: str) -> dict[int, int]:
    rows = await session.execute(
        select(MCQQuestion.id, MCQQuestion.correct_index)
        .join(SyllabusTopic, MCQQuestion.topic_id == SyllabusTopic.id)
        .where(SyllabusTopic.spec_code == spec_code)
        .order_by(MCQQuestion.id)
    )
    return {question_id: correct_index for question_id, correct_index in rows}


def as_payload(answers: dict[int, int]) -> dict[str, dict[str, int]]:
    return {"answers": {str(question_id): index for question_id, index in answers.items()}}


# --- Authentication ------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("GET", "/api/v1/quizzes/topics"),
        ("GET", "/api/v1/quizzes/1.1.1"),
        ("POST", "/api/v1/quizzes/1.1.1/submit"),
    ],
)
async def test_quiz_endpoints_require_a_token(client: AsyncClient, method: str, path: str) -> None:
    response = await client.request(method, path, json={"answers": {"1": 0}})

    assert response.status_code == 401


# --- Fetching a quiz -----------------------------------------------------------------------


async def test_quiz_returns_at_most_ten_questions_without_answers(
    client: AsyncClient, auth_headers: dict[str, str], quiz_data: dict[str, SyllabusTopic]
) -> None:
    response = await client.get("/api/v1/quizzes/1.1.1", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["topic"] == {
        "id": quiz_data["1.1.1"].id,
        "spec_code": "1.1.1",
        "title": "Structure and function of the processor",
        "slug": "topic-1-1-1",
    }
    assert len(body["questions"]) == 10
    assert len({question["id"] for question in body["questions"]}) == 10
    for question in body["questions"]:
        assert set(question) == {"id", "topic_id", "question_text", "code_snippet", "options"}
        assert question["topic_id"] == quiz_data["1.1.1"].id
        assert len(question["options"]) == 4
    # Nothing about the answers may appear anywhere in the payload.
    assert "correct_index" not in response.text
    assert "explanation" not in response.text
    assert SECRET_EXPLANATION not in response.text


async def test_quiz_with_fewer_than_ten_questions_returns_them_all(
    client: AsyncClient, auth_headers: dict[str, str], quiz_data: dict[str, SyllabusTopic]
) -> None:
    body = (await client.get("/api/v1/quizzes/1.1.2", headers=auth_headers)).json()

    assert len(body["questions"]) == 3


async def test_quiz_for_topic_without_questions_is_empty(
    client: AsyncClient, auth_headers: dict[str, str], quiz_data: dict[str, SyllabusTopic]
) -> None:
    response = await client.get("/api/v1/quizzes/2.1.1", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["questions"] == []


async def test_quiz_for_unknown_topic_is_404(
    client: AsyncClient, auth_headers: dict[str, str], quiz_data: dict[str, SyllabusTopic]
) -> None:
    response = await client.get("/api/v1/quizzes/9.9.9", headers=auth_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Topic 9.9.9 not found"


# --- Submitting a quiz ---------------------------------------------------------------------


async def test_submit_grades_on_the_server_and_records_the_attempt(
    client: AsyncClient,
    session: AsyncSession,
    user: User,
    auth_headers: dict[str, str],
    quiz_data: dict[str, SyllabusTopic],
) -> None:
    key = await correct_answers(session, "1.1.2")
    first, second, third = key
    # Two right, one wrong.
    answers = {first: key[first], second: (key[second] + 1) % 4, third: key[third]}

    response = await client.post(
        "/api/v1/quizzes/1.1.2/submit", json=as_payload(answers), headers=auth_headers
    )

    assert response.status_code == 201
    body = response.json()
    assert body["topic_id"] == quiz_data["1.1.2"].id
    assert body["score"] == 2
    assert body["total_questions"] == 3
    assert body["percentage"] == 66.7
    assert [result["question_id"] for result in body["results"]] == [first, second, third]
    assert [result["is_correct"] for result in body["results"]] == [True, False, True]
    wrong = body["results"][1]
    assert wrong["selected_index"] == answers[second]
    assert wrong["correct_index"] == key[second]
    assert wrong["explanation"].startswith(SECRET_EXPLANATION)

    attempt = (await session.execute(select(MCQAttempt))).scalar_one()
    assert attempt.id == body["attempt_id"]
    assert (attempt.user_id, attempt.topic_id) == (user.id, quiz_data["1.1.2"].id)
    assert (attempt.score, attempt.total_questions) == (2, 3)


async def test_submit_all_correct_scores_full_marks(
    client: AsyncClient,
    session: AsyncSession,
    auth_headers: dict[str, str],
    quiz_data: dict[str, SyllabusTopic],
) -> None:
    key = await correct_answers(session, "1.1.2")

    body = (
        await client.post(
            "/api/v1/quizzes/1.1.2/submit", json=as_payload(key), headers=auth_headers
        )
    ).json()

    assert (body["score"], body["total_questions"], body["percentage"]) == (3, 3, 100.0)


async def test_submit_rejects_questions_from_another_topic(
    client: AsyncClient,
    session: AsyncSession,
    auth_headers: dict[str, str],
    quiz_data: dict[str, SyllabusTopic],
) -> None:
    other_topic_key = await correct_answers(session, "1.1.1")
    foreign_id = next(iter(other_topic_key))

    response = await client.post(
        "/api/v1/quizzes/1.1.2/submit", json=as_payload({foreign_id: 0}), headers=auth_headers
    )

    assert response.status_code == 400
    assert str(foreign_id) in response.json()["detail"]
    # A rejected submission must not reveal the answer or be recorded as an attempt.
    assert "correct_index" not in response.text
    assert (await session.execute(select(MCQAttempt))).first() is None


@pytest.mark.parametrize(
    "payload",
    [
        {"answers": {}},
        {"answers": {"1": 4}},
        {"answers": {"1": -1}},
        {"answers": {str(n): 0 for n in range(1, 12)}},
        {},
    ],
    ids=["no-answers", "index-too-high", "index-negative", "more-than-ten-answers", "no-body"],
)
async def test_submit_rejects_malformed_submissions(
    client: AsyncClient,
    auth_headers: dict[str, str],
    quiz_data: dict[str, SyllabusTopic],
    payload: dict[str, dict[str, int]],
) -> None:
    response = await client.post(
        "/api/v1/quizzes/1.1.1/submit", json=payload, headers=auth_headers
    )

    assert response.status_code == 422


async def test_submit_for_unknown_topic_is_404(
    client: AsyncClient, auth_headers: dict[str, str], quiz_data: dict[str, SyllabusTopic]
) -> None:
    response = await client.post(
        "/api/v1/quizzes/9.9.9/submit", json={"answers": {"1": 0}}, headers=auth_headers
    )

    assert response.status_code == 404


# --- Topic selector ------------------------------------------------------------------------


async def test_topics_lists_every_topic_in_spec_order_with_no_progress(
    client: AsyncClient, auth_headers: dict[str, str], quiz_data: dict[str, SyllabusTopic]
) -> None:
    response = await client.get("/api/v1/quizzes/topics", headers=auth_headers)

    assert response.status_code == 200
    topics = response.json()["topics"]
    assert [topic["spec_code"] for topic in topics] == ["1.1.1", "1.1.2", "2.1.1"]
    assert [topic["question_count"] for topic in topics] == [12, 3, 0]
    assert topics[0] == {
        "id": quiz_data["1.1.1"].id,
        "paper": 1,
        "section_code": "1.1",
        "spec_code": "1.1.1",
        "title": "Structure and function of the processor",
        "slug": "topic-1-1-1",
        "question_count": 12,
        "attempts_count": 0,
        "best_score": None,
        "total_questions": None,
    }


async def test_topics_report_best_attempt_and_count_for_the_current_user_only(
    client: AsyncClient,
    session: AsyncSession,
    user: User,
    auth_headers: dict[str, str],
    quiz_data: dict[str, SyllabusTopic],
) -> None:
    other_user = User(full_name="Other", email="other@alcsr.edu", hashed_password="x")
    processor, types = quiz_data["1.1.1"], quiz_data["1.1.2"]
    session.add_all(
        [
            other_user,
            MCQAttempt(user=user, topic=processor, score=4, total_questions=10),
            MCQAttempt(user=user, topic=processor, score=8, total_questions=10),
            MCQAttempt(user=user, topic=processor, score=6, total_questions=10),
            # 2/2 is a higher percentage than 2/3, so it is the best attempt on this topic.
            MCQAttempt(user=user, topic=types, score=2, total_questions=3),
            MCQAttempt(user=user, topic=types, score=2, total_questions=2),
            MCQAttempt(user=other_user, topic=processor, score=10, total_questions=10),
        ]
    )
    await session.commit()

    topics = (await client.get("/api/v1/quizzes/topics", headers=auth_headers)).json()["topics"]
    by_code = {topic["spec_code"]: topic for topic in topics}

    assert (by_code["1.1.1"]["attempts_count"], by_code["1.1.1"]["best_score"]) == (3, 8)
    assert by_code["1.1.1"]["total_questions"] == 10
    assert (by_code["1.1.2"]["best_score"], by_code["1.1.2"]["total_questions"]) == (2, 2)
    assert by_code["1.1.2"]["attempts_count"] == 2
    assert by_code["2.1.1"]["attempts_count"] == 0

    other = (
        await client.get("/api/v1/quizzes/topics", headers=auth_headers_for(other_user))
    ).json()["topics"]
    assert (other[0]["attempts_count"], other[0]["best_score"]) == (1, 10)


async def test_submitted_quiz_appears_in_topics_and_dashboard(
    client: AsyncClient,
    session: AsyncSession,
    auth_headers: dict[str, str],
    quiz_data: dict[str, SyllabusTopic],
) -> None:
    key = await correct_answers(session, "1.1.2")
    await client.post("/api/v1/quizzes/1.1.2/submit", json=as_payload(key), headers=auth_headers)

    topics = (await client.get("/api/v1/quizzes/topics", headers=auth_headers)).json()["topics"]
    metrics = (await client.get("/api/v1/dashboard/metrics", headers=auth_headers)).json()

    assert (topics[1]["attempts_count"], topics[1]["best_score"]) == (1, 3)
    assert metrics["topics_practiced"] == 1
    assert metrics["average_quiz_accuracy"] == 100.0
    assert metrics["recent_activity"][0]["activity_type"] == "quiz"
