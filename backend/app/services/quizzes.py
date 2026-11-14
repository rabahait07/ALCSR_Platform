from collections import defaultdict

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.quiz import MCQQuestion
from app.models.quiz_attempt import MCQAttempt
from app.models.topic import SyllabusTopic
from app.models.user import User
from app.schemas.quiz import (
    QUIZ_LENGTH,
    MCQQuestionPublicOut,
    QuestionResultOut,
    QuizOut,
    QuizResultOut,
    QuizSubmissionIn,
    QuizTopicProgressOut,
    QuizTopicsResponse,
)
from app.schemas.syllabus import SubtopicOut
from app.services.scoring import percentage
from app.services.syllabus import get_topic_by_spec_code, topic_sort_key


class InvalidQuizSubmissionError(Exception):
    """Raised when a submission refers to questions that are not part of the topic's quiz."""


async def list_quiz_topics(db: AsyncSession, user: User) -> QuizTopicsResponse:
    """Every sub-topic in specification order, with the user's best score and attempt count."""
    topics = sorted((await db.execute(select(SyllabusTopic))).scalars().all(), key=topic_sort_key)

    question_counts = {
        topic_id: count
        for topic_id, count in await db.execute(
            select(MCQQuestion.topic_id, func.count(MCQQuestion.id)).group_by(MCQQuestion.topic_id)
        )
    }

    attempts_by_topic: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for topic_id, score, total_questions in await db.execute(
        select(MCQAttempt.topic_id, MCQAttempt.score, MCQAttempt.total_questions).where(
            MCQAttempt.user_id == user.id
        )
    ):
        attempts_by_topic[topic_id].append((score, total_questions))

    summaries: list[QuizTopicProgressOut] = []
    for topic in topics:
        attempts = attempts_by_topic.get(topic.id, [])
        # Best means the highest percentage; a higher raw score breaks ties.
        best = max(attempts, key=lambda attempt: (attempt[0] / attempt[1], attempt[0]), default=None)
        summaries.append(
            QuizTopicProgressOut(
                id=topic.id,
                paper=topic.paper,
                section_code=topic.section_code,
                spec_code=topic.spec_code,
                title=topic.title,
                slug=topic.slug,
                question_count=question_counts.get(topic.id, 0),
                attempts_count=len(attempts),
                best_score=best[0] if best else None,
                total_questions=best[1] if best else None,
            )
        )
    return QuizTopicsResponse(topics=summaries)


async def get_quiz(db: AsyncSession, spec_code: str) -> QuizOut | None:
    """A random selection of up to ``QUIZ_LENGTH`` questions for the topic, without answers."""
    topic = await get_topic_by_spec_code(db, spec_code)
    if topic is None:
        return None
    result = await db.execute(
        select(MCQQuestion)
        .where(MCQQuestion.topic_id == topic.id)
        .order_by(func.random())
        .limit(QUIZ_LENGTH)
    )
    return QuizOut(
        topic=SubtopicOut.model_validate(topic),
        # MCQQuestionPublicOut has no answer fields, so validating through it strips them.
        questions=[MCQQuestionPublicOut.model_validate(question) for question in result.scalars()],
    )


async def grade_quiz(
    db: AsyncSession, user: User, spec_code: str, submission: QuizSubmissionIn
) -> QuizResultOut | None:
    """Grade the submitted answers against the stored correct answers and record the attempt.

    Returns None when the topic does not exist. Raises InvalidQuizSubmissionError when any
    submitted question id does not belong to the topic.
    """
    topic = await get_topic_by_spec_code(db, spec_code)
    if topic is None:
        return None

    result = await db.execute(
        select(MCQQuestion).where(
            MCQQuestion.topic_id == topic.id, MCQQuestion.id.in_(submission.answers.keys())
        )
    )
    questions = {question.id: question for question in result.scalars()}
    unknown_ids = sorted(submission.answers.keys() - questions.keys())
    if unknown_ids:
        raise InvalidQuizSubmissionError(
            f"Questions {unknown_ids} are not part of the quiz for topic {spec_code}"
        )

    # Results keep the order in which the answers were submitted.
    results = [
        QuestionResultOut(
            question_id=question_id,
            selected_index=selected_index,
            correct_index=questions[question_id].correct_index,
            is_correct=selected_index == questions[question_id].correct_index,
            explanation=questions[question_id].explanation,
        )
        for question_id, selected_index in submission.answers.items()
    ]
    score = sum(result.is_correct for result in results)

    attempt = MCQAttempt(
        user_id=user.id, topic_id=topic.id, score=score, total_questions=len(results)
    )
    db.add(attempt)
    await db.commit()

    return QuizResultOut(
        attempt_id=attempt.id,
        topic_id=topic.id,
        score=score,
        total_questions=len(results),
        percentage=percentage(score, len(results)),
        results=results,
    )
