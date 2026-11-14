from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.topic import PAPER_TITLES, SyllabusTopic
from app.schemas.syllabus import (
    MajorSectionOut,
    PaperHierarchyOut,
    SubtopicOut,
    SyllabusTreeResponse,
)


def spec_code_sort_key(code: str) -> tuple[int, ...]:
    """Order specification codes numerically, so that "1.1.10" sorts after "1.1.9"."""
    return tuple(int(part) if part.isdigit() else 0 for part in code.split("."))


def topic_sort_key(topic: SyllabusTopic) -> tuple[int, tuple[int, ...], tuple[int, ...]]:
    return (
        topic.paper,
        spec_code_sort_key(topic.section_code),
        spec_code_sort_key(topic.spec_code),
    )


async def get_topic_by_spec_code(db: AsyncSession, spec_code: str) -> SyllabusTopic | None:
    result = await db.execute(select(SyllabusTopic).where(SyllabusTopic.spec_code == spec_code))
    return result.scalar_one_or_none()


async def get_syllabus_tree(db: AsyncSession) -> SyllabusTreeResponse:
    result = await db.execute(
        select(SyllabusTopic).order_by(
            SyllabusTopic.paper, SyllabusTopic.section_code, SyllabusTopic.spec_code
        )
    )
    topics = sorted(result.scalars().all(), key=topic_sort_key)

    # Both papers are always present, even before any topics have been loaded.
    papers = {
        paper: PaperHierarchyOut(paper=paper, title=title) for paper, title in PAPER_TITLES.items()
    }
    for topic in topics:
        sections = papers[topic.paper].sections
        if not sections or sections[-1].section_code != topic.section_code:
            sections.append(
                MajorSectionOut(
                    section_code=topic.section_code,
                    section_title=topic.section_title,
                    section_slug=topic.section_slug,
                )
            )
        sections[-1].subtopics.append(SubtopicOut.model_validate(topic))

    return SyllabusTreeResponse(papers=list(papers.values()))
