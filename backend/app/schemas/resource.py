from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ResourceType
from app.schemas.syllabus import SubtopicOut


class ResourceItemOut(BaseModel):
    """A static PDF link. The frontend renders ``file_url`` as a plain new-tab anchor."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    resource_type: ResourceType
    title: str
    file_url: str
    display_order: int


class TopicResourcesResponse(BaseModel):
    """Resources for one sub-topic, grouped into the paired columns shown on topic pages."""

    topic: SubtopicOut
    worksheets: list[ResourceItemOut] = Field(default_factory=list)
    worksheet_answers: list[ResourceItemOut] = Field(default_factory=list)
    learning_notes: list[ResourceItemOut] = Field(default_factory=list)
    reviewing_notes: list[ResourceItemOut] = Field(default_factory=list)


class ExamSectionResourcesResponse(BaseModel):
    """Exam question packs and their mark schemes for one specification section, e.g. 1.3."""

    paper: int = Field(ge=1, le=2)
    section_code: str
    section_title: str
    exam_packs: list[ResourceItemOut] = Field(default_factory=list)
    mark_schemes: list[ResourceItemOut] = Field(default_factory=list)


class PastPaperRowOut(BaseModel):
    """One exam series for one paper: question paper, mark scheme and walkthrough."""

    paper: int = Field(ge=1, le=2)
    exam_series: str
    question_paper: ResourceItemOut | None = None
    mark_scheme: ResourceItemOut | None = None
    walkthrough: ResourceItemOut | None = None


class PastPapersResponse(BaseModel):
    paper_1: list[PastPaperRowOut] = Field(default_factory=list)
    paper_2: list[PastPaperRowOut] = Field(default_factory=list)
