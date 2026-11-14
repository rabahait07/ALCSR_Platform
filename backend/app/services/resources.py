import calendar
import re
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import ResourceType
from app.models.resource import StaticResource
from app.models.topic import SyllabusTopic, section_slug_to_code
from app.schemas.resource import (
    ExamSectionResourcesResponse,
    PastPaperRowOut,
    PastPapersResponse,
    ResourceItemOut,
    TopicResourcesResponse,
)
from app.schemas.syllabus import SubtopicOut
from app.services.syllabus import get_topic_by_spec_code, topic_sort_key

_PAST_PAPER_URL_FIELDS: dict[str, str] = {
    ResourceType.PAST_PAPER_QP: "question_paper_url",
    ResourceType.PAST_PAPER_MS: "mark_scheme_url",
    ResourceType.PAST_PAPER_WALKTHROUGH: "walkthrough_url",
}

_MONTH_NUMBERS = {name.lower(): number for number, name in enumerate(calendar.month_name) if name}
_YEAR_PATTERN = re.compile(r"\b(\d{4})\b")


async def _resources_by_type(
    db: AsyncSession, topic_ids: Sequence[int], resource_types: Sequence[ResourceType]
) -> dict[str, list[StaticResource]]:
    """Load resources for the given topics, grouped by type in display order."""
    result = await db.execute(
        select(StaticResource)
        .where(
            StaticResource.topic_id.in_(topic_ids),
            StaticResource.resource_type.in_(resource_types),
        )
        .order_by(StaticResource.display_order, StaticResource.id)
    )
    grouped: dict[str, list[StaticResource]] = {resource_type: [] for resource_type in resource_types}
    for resource in result.scalars():
        grouped[resource.resource_type].append(resource)
    return grouped


def _to_items(resources: Sequence[StaticResource]) -> list[ResourceItemOut]:
    return [ResourceItemOut.model_validate(resource) for resource in resources]


async def get_topic_worksheets(db: AsyncSession, spec_code: str) -> TopicResourcesResponse | None:
    topic = await get_topic_by_spec_code(db, spec_code)
    if topic is None:
        return None
    grouped = await _resources_by_type(
        db, [topic.id], [ResourceType.WORKSHEET, ResourceType.WORKSHEET_ANSWER]
    )
    return TopicResourcesResponse(
        topic=SubtopicOut.model_validate(topic),
        worksheets=_to_items(grouped[ResourceType.WORKSHEET]),
        answers=_to_items(grouped[ResourceType.WORKSHEET_ANSWER]),
    )


async def get_topic_notes(db: AsyncSession, spec_code: str) -> TopicResourcesResponse | None:
    topic = await get_topic_by_spec_code(db, spec_code)
    if topic is None:
        return None
    grouped = await _resources_by_type(
        db, [topic.id], [ResourceType.LEARNING_NOTE, ResourceType.REVIEWING_NOTE]
    )
    return TopicResourcesResponse(
        topic=SubtopicOut.model_validate(topic),
        learning_notes=_to_items(grouped[ResourceType.LEARNING_NOTE]),
        reviewing_notes=_to_items(grouped[ResourceType.REVIEWING_NOTE]),
    )


async def get_exam_section_resources(
    db: AsyncSession, section_slug: str
) -> ExamSectionResourcesResponse | None:
    """Exam packs and mark schemes for every sub-topic in a section such as "1-3"."""
    section_code = section_slug_to_code(section_slug)
    result = await db.execute(
        select(SyllabusTopic).where(SyllabusTopic.section_code == section_code)
    )
    topics = sorted(result.scalars().all(), key=topic_sort_key)
    if not topics:
        return None

    grouped = await _resources_by_type(
        db, [topic.id for topic in topics], [ResourceType.EXAM_PACK, ResourceType.MARK_SCHEME]
    )
    # Keep packs grouped by sub-topic in specification order; the sort is stable, so the
    # display order within each sub-topic is preserved.
    topic_position = {topic.id: position for position, topic in enumerate(topics)}

    def in_topic_order(resources: list[StaticResource]) -> list[StaticResource]:
        return sorted(resources, key=lambda resource: topic_position[resource.topic_id or 0])

    first_topic = topics[0]
    return ExamSectionResourcesResponse(
        paper=first_topic.paper,
        section_code=first_topic.section_code,
        section_title=first_topic.section_title,
        section_slug=first_topic.section_slug,
        exam_packs=_to_items(in_topic_order(grouped[ResourceType.EXAM_PACK])),
        mark_schemes=_to_items(in_topic_order(grouped[ResourceType.MARK_SCHEME])),
    )


def exam_series_sort_key(exam_series: str) -> tuple[int, int, int, str]:
    """Newest dated series first ("June 2024" before "June 2023"); undated ones last."""
    lowered = exam_series.lower()
    year_match = _YEAR_PATTERN.search(lowered)
    if year_match is None:
        return (1, 0, 0, lowered)
    month = next((number for name, number in _MONTH_NUMBERS.items() if name in lowered), 0)
    return (0, -int(year_match.group(1)), -month, lowered)


async def get_past_papers(db: AsyncSession) -> PastPapersResponse:
    result = await db.execute(
        select(StaticResource)
        .where(
            StaticResource.resource_type.in_(list(_PAST_PAPER_URL_FIELDS)),
            StaticResource.paper.in_((1, 2)),
            StaticResource.exam_series.is_not(None),
        )
        .order_by(StaticResource.display_order, StaticResource.id)
    )

    rows: dict[tuple[int, str], dict[str, str]] = {}
    for resource in result.scalars():
        if resource.paper is None or resource.exam_series is None:
            continue
        urls = rows.setdefault((resource.paper, resource.exam_series), {})
        # If a series has duplicates of one document, the first in display order wins.
        urls.setdefault(_PAST_PAPER_URL_FIELDS[resource.resource_type], resource.file_url)

    papers: dict[int, list[PastPaperRowOut]] = {1: [], 2: []}
    for (paper, exam_series), urls in rows.items():
        papers[paper].append(PastPaperRowOut(paper=paper, exam_series=exam_series, **urls))
    for paper_rows in papers.values():
        paper_rows.sort(key=lambda row: exam_series_sort_key(row.exam_series))

    return PastPapersResponse(paper_1=papers[1], paper_2=papers[2])
