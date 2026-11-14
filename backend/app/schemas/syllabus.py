from pydantic import BaseModel, ConfigDict, Field


class SubtopicOut(BaseModel):
    """A single sub-topic, e.g. 1.1.1 Structure and function of the processor."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    spec_code: str
    title: str
    slug: str


class MajorSectionOut(BaseModel):
    """A specification section, e.g. 1.1, with its sub-topics in specification order."""

    section_code: str
    section_title: str
    subtopics: list[SubtopicOut] = Field(default_factory=list)


class PaperHierarchyOut(BaseModel):
    """One exam paper (1 or 2) with its sections in specification order."""

    paper: int = Field(ge=1, le=2)
    title: str
    sections: list[MajorSectionOut] = Field(default_factory=list)


class SyllabusTreeResponse(BaseModel):
    papers: list[PaperHierarchyOut] = Field(default_factory=list)
