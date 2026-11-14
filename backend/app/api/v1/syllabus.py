from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, status

from app.api.deps import DbSession
from app.schemas.resource import (
    ExamSectionResourcesResponse,
    PastPapersResponse,
    TopicResourcesResponse,
)
from app.schemas.syllabus import SyllabusTreeResponse
from app.services import resources as resource_service
from app.services import syllabus as syllabus_service

router = APIRouter()

SpecCode = Annotated[str, Path(max_length=16, examples=["1.1.1"])]
SectionSlug = Annotated[str, Path(pattern=r"^\d{1,2}-\d{1,2}$", examples=["1-3"])]


def _topic_not_found(spec_code: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Topic {spec_code} not found"
    )


@router.get("/syllabus/tree", response_model=SyllabusTreeResponse, tags=["syllabus"])
async def read_syllabus_tree(db: DbSession) -> SyllabusTreeResponse:
    """The whole specification as papers, sections and sub-topics."""
    return await syllabus_service.get_syllabus_tree(db)


@router.get(
    "/resources/worksheets/{spec_code}",
    response_model=TopicResourcesResponse,
    response_model_exclude_unset=True,
    tags=["resources"],
)
async def read_topic_worksheets(spec_code: SpecCode, db: DbSession) -> TopicResourcesResponse:
    """Worksheet question PDFs and their answer PDFs for one sub-topic."""
    response = await resource_service.get_topic_worksheets(db, spec_code)
    if response is None:
        raise _topic_not_found(spec_code)
    return response


@router.get(
    "/resources/notes/{spec_code}",
    response_model=TopicResourcesResponse,
    response_model_exclude_unset=True,
    tags=["resources"],
)
async def read_topic_notes(spec_code: SpecCode, db: DbSession) -> TopicResourcesResponse:
    """Learning notes and reviewing notes PDFs for one sub-topic."""
    response = await resource_service.get_topic_notes(db, spec_code)
    if response is None:
        raise _topic_not_found(spec_code)
    return response


@router.get(
    "/resources/exam-questions/{section_slug}",
    response_model=ExamSectionResourcesResponse,
    tags=["resources"],
)
async def read_exam_section_resources(
    section_slug: SectionSlug, db: DbSession
) -> ExamSectionResourcesResponse:
    """Exam question packs and mark schemes across every sub-topic of a section."""
    response = await resource_service.get_exam_section_resources(db, section_slug)
    if response is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Section {section_slug} not found"
        )
    return response


@router.get("/resources/past-papers", response_model=PastPapersResponse, tags=["resources"])
async def read_past_papers(db: DbSession) -> PastPapersResponse:
    """Question papers, mark schemes and walkthroughs for each exam series, newest first."""
    return await resource_service.get_past_papers(db)
