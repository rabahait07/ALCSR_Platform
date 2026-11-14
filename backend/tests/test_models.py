from datetime import datetime, timezone

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import configure_mappers

from app.models import (
    Base,
    ChallengeSubmission,
    CodingChallenge,
    Difficulty,
    MCQAttempt,
    MCQQuestion,
    ResourceType,
    StaticResource,
    SyllabusTopic,
    User,
)

EXPECTED_TABLES = {
    "users",
    "syllabus_topics",
    "static_resources",
    "mcq_questions",
    "mcq_attempts",
    "coding_challenges",
    "challenge_submissions",
}


def make_topic(spec_code: str = "1.1.1") -> SyllabusTopic:
    return SyllabusTopic(
        paper=1,
        section_code="1.1",
        section_title=(
            "1.1 The characteristics of contemporary processors, input, output and "
            "storage devices"
        ),
        spec_code=spec_code,
        title="Structure and function of the processor",
        slug=f"topic-{spec_code.replace('.', '-')}",
    )


def make_user(email: str = "student@alcsr.edu") -> User:
    return User(full_name="Ada Lovelace", email=email, hashed_password="not-a-real-hash")


def make_question(topic: SyllabusTopic, correct_index: int = 2) -> MCQQuestion:
    return MCQQuestion(
        topic=topic,
        question_text="Which register holds the address of the next instruction?",
        options=["MAR", "MDR", "PC", "ACC"],
        correct_index=correct_index,
        explanation="The program counter holds the address of the next instruction.",
    )


def make_challenge(topic: SyllabusTopic, difficulty: str = Difficulty.EASY) -> CodingChallenge:
    return CodingChallenge(
        topic=topic,
        slug="binary-to-denary",
        title="Binary to Denary",
        difficulty=difficulty,
        description="Convert a binary string to its denary value.",
        function_name="binary_to_denary",
        starter_code="def binary_to_denary(bits):\n    pass\n",
        test_cases=[{"input_args": ["101"], "expected": 5, "description": "101 is 5"}],
    )


async def count(session: AsyncSession, model: type) -> int:
    return (await session.execute(select(func.count()).select_from(model))).scalar_one()


def test_all_tables_are_registered_and_mappers_configure() -> None:
    configure_mappers()

    assert set(Base.metadata.tables) == EXPECTED_TABLES


async def test_full_object_graph_round_trips(session: AsyncSession) -> None:
    topic = make_topic()
    user = make_user()
    question = make_question(topic)
    challenge = make_challenge(topic)
    worksheet = StaticResource(
        topic=topic,
        resource_type=ResourceType.WORKSHEET,
        title="Worksheet 1 Questions - CPU Components and Registers",
        file_url="/pdfs/worksheets/1.1.1/worksheet-1-questions.pdf",
    )
    attempt = MCQAttempt(user=user, topic=topic, score=1, total_questions=1)
    submission = ChallengeSubmission(
        user=user,
        challenge=challenge,
        code="def binary_to_denary(bits):\n    return int(bits, 2)\n",
        passed=True,
        passed_tests=1,
        total_tests=1,
    )
    session.add_all([topic, user, question, challenge, worksheet, attempt, submission])
    await session.commit()
    session.expunge_all()

    stored_question = (await session.execute(select(MCQQuestion))).scalar_one()
    stored_challenge = (await session.execute(select(CodingChallenge))).scalar_one()
    stored_worksheet = (await session.execute(select(StaticResource))).scalar_one()
    stored_user = (await session.execute(select(User))).scalar_one()
    stored_attempt = (await session.execute(select(MCQAttempt))).scalar_one()
    stored_submission = (await session.execute(select(ChallengeSubmission))).scalar_one()

    assert stored_question.options == ["MAR", "MDR", "PC", "ACC"]
    assert stored_question.code_snippet is None
    assert stored_challenge.test_cases[0]["expected"] == 5
    assert stored_worksheet.display_order == 0
    assert stored_worksheet.topic_id == stored_question.topic_id
    for timestamp in (
        stored_user.created_at,
        stored_attempt.completed_at,
        stored_submission.submitted_at,
    ):
        assert isinstance(timestamp, datetime)
        assert timestamp.tzinfo == timezone.utc
    assert stored_submission.passed is True


def test_section_slug_is_derived_from_section_code() -> None:
    assert make_topic().section_slug == "1-1"


async def test_past_paper_resource_needs_no_topic(session: AsyncSession) -> None:
    session.add(
        StaticResource(
            resource_type=ResourceType.PAST_PAPER_QP,
            paper=1,
            exam_series="June 2024",
            title="June 2024 Paper 1 QP",
            file_url="/pdfs/past-papers/june-2024-paper-1-qp.pdf",
        )
    )
    await session.commit()

    stored = (await session.execute(select(StaticResource))).scalar_one()
    assert stored.topic_id is None
    assert stored.exam_series == "June 2024"


async def test_user_email_must_be_unique(session: AsyncSession) -> None:
    session.add_all([make_user(), make_user()])

    with pytest.raises(IntegrityError):
        await session.commit()


async def test_topic_spec_code_must_be_unique(session: AsyncSession) -> None:
    first, second = make_topic(), make_topic()
    second.slug = "a-different-slug"
    session.add_all([first, second])

    with pytest.raises(IntegrityError):
        await session.commit()


async def test_correct_index_outside_options_is_rejected(session: AsyncSession) -> None:
    session.add(make_question(make_topic(), correct_index=4))

    with pytest.raises(IntegrityError):
        await session.commit()


async def test_unknown_resource_type_is_rejected(session: AsyncSession) -> None:
    session.add(StaticResource(resource_type="video", title="Clip", file_url="/clip.mp4"))

    with pytest.raises(IntegrityError):
        await session.commit()


async def test_unknown_difficulty_is_rejected(session: AsyncSession) -> None:
    session.add(make_challenge(make_topic(), difficulty="Impossible"))

    with pytest.raises(IntegrityError):
        await session.commit()


async def test_paper_must_be_one_or_two(session: AsyncSession) -> None:
    topic = make_topic()
    topic.paper = 3
    session.add(topic)

    with pytest.raises(IntegrityError):
        await session.commit()


async def test_score_cannot_exceed_total_questions(session: AsyncSession) -> None:
    session.add(MCQAttempt(user=make_user(), topic=make_topic(), score=6, total_questions=5))

    with pytest.raises(IntegrityError):
        await session.commit()


async def test_foreign_keys_are_enforced(session: AsyncSession) -> None:
    session.add(MCQAttempt(user_id=999, topic_id=999, score=0, total_questions=1))

    with pytest.raises(IntegrityError):
        await session.commit()


async def test_deleting_topic_cascades_to_its_content(session: AsyncSession) -> None:
    topic = make_topic()
    user = make_user()
    challenge = make_challenge(topic)
    session.add_all(
        [
            topic,
            user,
            make_question(topic),
            challenge,
            MCQAttempt(user=user, topic=topic, score=1, total_questions=1),
            ChallengeSubmission(
                user=user, challenge=challenge, code="pass", passed=False, passed_tests=0, total_tests=1
            ),
        ]
    )
    await session.commit()

    await session.delete(topic)
    await session.commit()

    assert await count(session, MCQQuestion) == 0
    assert await count(session, MCQAttempt) == 0
    assert await count(session, CodingChallenge) == 0
    assert await count(session, ChallengeSubmission) == 0
    assert await count(session, User) == 1


async def test_deleting_user_cascades_to_their_activity(session: AsyncSession) -> None:
    topic = make_topic()
    user = make_user()
    session.add_all([topic, user, MCQAttempt(user=user, topic=topic, score=0, total_questions=1)])
    await session.commit()

    await session.delete(user)
    await session.commit()

    assert await count(session, MCQAttempt) == 0
    assert await count(session, SyllabusTopic) == 1
