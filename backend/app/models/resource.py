from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import ResourceType, sql_in_list

if TYPE_CHECKING:
    from app.models.topic import SyllabusTopic


class StaticResource(Base):
    """A static PDF (or external walkthrough link) opened directly by the browser.

    Topic resources (worksheets, notes, exam packs, mark schemes) set ``topic_id``.
    Past papers leave ``topic_id`` null and set ``paper`` and ``exam_series`` instead.
    """

    __tablename__ = "static_resources"
    __table_args__ = (
        CheckConstraint(
            f"resource_type IN ({sql_in_list(ResourceType)})",
            name="ck_static_resources_resource_type",
        ),
        CheckConstraint("paper IS NULL OR paper IN (1, 2)", name="ck_static_resources_paper"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    topic_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("syllabus_topics.id", ondelete="CASCADE"), index=True, nullable=True
    )
    resource_type: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    paper: Mapped[int | None] = mapped_column(Integer, nullable=True)
    exam_series: Mapped[str | None] = mapped_column(String(32), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    file_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    topic: Mapped[SyllabusTopic | None] = relationship(back_populates="resources")

    def __repr__(self) -> str:
        return f"<StaticResource id={self.id} type={self.resource_type!r} title={self.title!r}>"
