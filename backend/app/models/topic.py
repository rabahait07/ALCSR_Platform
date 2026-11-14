from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.challenge import CodingChallenge
    from app.models.quiz import MCQQuestion
    from app.models.quiz_attempt import MCQAttempt
    from app.models.resource import StaticResource

# OCR H446 component titles, keyed by paper number.
PAPER_TITLES: dict[int, str] = {
    1: "Computer Systems",
    2: "Algorithms and Programming",
}


class SyllabusTopic(Base):
    """One OCR H446 sub-topic, e.g. 1.1.1 Structure and function of the processor."""

    __tablename__ = "syllabus_topics"
    __table_args__ = (CheckConstraint("paper IN (1, 2)", name="ck_syllabus_topics_paper"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    paper: Mapped[int] = mapped_column(Integer, nullable=False)
    section_code: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
    section_title: Mapped[str] = mapped_column(String(255), nullable=False)
    spec_code: Mapped[str] = mapped_column(String(16), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)

    resources: Mapped[list[StaticResource]] = relationship(
        back_populates="topic", cascade="all, delete-orphan", passive_deletes=True
    )
    questions: Mapped[list[MCQQuestion]] = relationship(
        back_populates="topic", cascade="all, delete-orphan", passive_deletes=True
    )
    quiz_attempts: Mapped[list[MCQAttempt]] = relationship(
        back_populates="topic", cascade="all, delete-orphan", passive_deletes=True
    )
    challenges: Mapped[list[CodingChallenge]] = relationship(
        back_populates="topic", cascade="all, delete-orphan", passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"<SyllabusTopic id={self.id} spec_code={self.spec_code!r}>"
