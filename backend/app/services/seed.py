import re

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.challenge import CodingChallenge
from app.models.enums import ResourceType
from app.models.quiz import MCQQuestion
from app.models.resource import StaticResource
from app.models.topic import SyllabusTopic
from app.services.seed_data.challenges import CHALLENGES
from app.services.seed_data.questions_paper1 import PAPER_1_QUESTIONS
from app.services.seed_data.questions_paper2 import PAPER_2_QUESTIONS
from app.services.seed_data.syllabus import (
    EXAM_PACK_URL,
    EXAM_PACKS_PER_SECTION,
    EXAM_SERIES,
    NOTES_PER_TOPIC,
    NOTES_URL,
    PAST_PAPER_URL,
    SECTIONS,
    WALKTHROUGH_URL,
    WORKSHEET_URL,
    WORKSHEETS_PER_TOPIC,
)
from app.services.seed_data.types import SeedQuestion, SeedSection, SeedTopic

QUESTIONS: dict[str, tuple[SeedQuestion, ...]] = {**PAPER_1_QUESTIONS, **PAPER_2_QUESTIONS}


def slugify(text: str) -> str:
    """Lower-case ``text`` and join its words with hyphens, dropping punctuation."""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _build_topic(section: SeedSection, topic: SeedTopic) -> SyllabusTopic:
    return SyllabusTopic(
        paper=section.paper,
        section_code=section.code,
        section_title=section.title,
        spec_code=topic.spec_code,
        title=topic.title,
        slug=slugify(topic.title),
    )


def _topic_resources(topic: SyllabusTopic, seed_topic: SeedTopic) -> list[StaticResource]:
    """Worksheets with matching answers, and learning notes with matching reviewing notes."""
    resources: list[StaticResource] = []
    for number, focus in enumerate(seed_topic.focus_areas[:WORKSHEETS_PER_TOPIC], start=1):
        for resource_type, label in (
            (ResourceType.WORKSHEET, "Questions"),
            (ResourceType.WORKSHEET_ANSWER, "Answers"),
        ):
            resources.append(
                StaticResource(
                    topic=topic,
                    resource_type=resource_type,
                    title=f"Worksheet {number} {label} - {focus}",
                    file_url=WORKSHEET_URL,
                    display_order=number,
                )
            )
    for number, focus in enumerate(seed_topic.focus_areas[:NOTES_PER_TOPIC], start=1):
        for resource_type, label in (
            (ResourceType.LEARNING_NOTE, "Learning Notes"),
            (ResourceType.REVIEWING_NOTE, "Reviewing Notes"),
        ):
            resources.append(
                StaticResource(
                    topic=topic,
                    resource_type=resource_type,
                    title=f"{label} - {focus}",
                    file_url=NOTES_URL,
                    display_order=number,
                )
            )
    return resources


def _section_exam_packs(section: SeedSection, first_topic: SyllabusTopic) -> list[StaticResource]:
    """Exam question packs and mark schemes for a whole section.

    A resource can only be linked to a sub-topic, so section-wide packs are attached to the
    section's first sub-topic. The exam-questions endpoint gathers packs across the section.
    """
    resources: list[StaticResource] = []
    for number in range(1, EXAM_PACKS_PER_SECTION + 1):
        resources.append(
            StaticResource(
                topic=first_topic,
                resource_type=ResourceType.EXAM_PACK,
                title=f"Exam Question Pack {number} - {section.name}",
                file_url=EXAM_PACK_URL,
                display_order=number,
            )
        )
        resources.append(
            StaticResource(
                topic=first_topic,
                resource_type=ResourceType.MARK_SCHEME,
                title=f"Pack {number} Mark Scheme - {section.name}",
                file_url=EXAM_PACK_URL,
                display_order=number,
            )
        )
    return resources


def _past_papers() -> list[StaticResource]:
    """A question paper, mark scheme and walkthrough link for every paper and exam series."""
    documents = (
        (ResourceType.PAST_PAPER_QP, "QP", PAST_PAPER_URL),
        (ResourceType.PAST_PAPER_MS, "MS", PAST_PAPER_URL),
        (ResourceType.PAST_PAPER_WALKTHROUGH, "PW", WALKTHROUGH_URL),
    )
    return [
        StaticResource(
            resource_type=resource_type,
            paper=paper,
            exam_series=exam_series,
            title=f"{exam_series} Paper {paper} {suffix}",
            file_url=file_url,
            display_order=order,
        )
        for paper in (1, 2)
        for order, exam_series in enumerate(EXAM_SERIES, start=1)
        for resource_type, suffix, file_url in documents
    ]


def _topic_questions(topic: SyllabusTopic) -> list[MCQQuestion]:
    return [
        MCQQuestion(
            topic=topic,
            question_text=question.text,
            code_snippet=question.code,
            options=list(question.options),
            correct_index=question.answer,
            explanation=question.explanation,
        )
        for question in QUESTIONS[topic.spec_code]
    ]


def _challenges(topics: dict[str, SyllabusTopic]) -> list[CodingChallenge]:
    return [
        CodingChallenge(
            topic=topics[challenge.spec_code],
            slug=challenge.slug,
            title=challenge.title,
            difficulty=challenge.difficulty,
            description=challenge.description,
            function_name=challenge.function_name,
            starter_code=challenge.starter_code,
            test_cases=[dict(test_case) for test_case in challenge.test_cases],
        )
        for challenge in CHALLENGES
    ]


async def seed_database(db: AsyncSession) -> bool:
    """Load the OCR H446 syllabus and sample content into an empty database.

    Idempotent: does nothing if any syllabus topic already exists. Everything is committed
    in a single transaction, so the database is never left partly seeded. Returns True if
    the data was inserted and False if the database had already been seeded.
    """
    existing_topics = await db.scalar(select(func.count(SyllabusTopic.id)))
    if existing_topics:
        return False

    topics: dict[str, SyllabusTopic] = {}
    records: list[SyllabusTopic | StaticResource | MCQQuestion | CodingChallenge] = []
    for section in SECTIONS:
        section_topics = [_build_topic(section, seed_topic) for seed_topic in section.topics]
        for topic, seed_topic in zip(section_topics, section.topics, strict=True):
            topics[topic.spec_code] = topic
            records.append(topic)
            records.extend(_topic_resources(topic, seed_topic))
            records.extend(_topic_questions(topic))
        records.extend(_section_exam_packs(section, section_topics[0]))
    records.extend(_past_papers())
    records.extend(_challenges(topics))

    db.add_all(records)
    try:
        await db.commit()
    except IntegrityError:
        # Another worker starting at the same moment has already inserted the seed data.
        await db.rollback()
        return False
    return True
