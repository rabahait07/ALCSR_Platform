from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import JSON, CheckConstraint, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.topic import SyllabusTopic

MCQ_OPTION_COUNT = 4


class MCQQuestion(Base):
    """A multiple-choice question.

    ``correct_index`` and ``explanation`` must never be serialised to the client before the
    student submits; only ``MCQQuestionPublicOut`` may be used to return questions.
    """

    __tablename__ = "mcq_questions"
    __table_args__ = (
        CheckConstraint(
            f"correct_index >= 0 AND correct_index < {MCQ_OPTION_COUNT}",
            name="ck_mcq_questions_correct_index",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    topic_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("syllabus_topics.id", ondelete="CASCADE"), index=True, nullable=False
    )
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    code_snippet: Mapped[str | None] = mapped_column(Text, nullable=True)
    options: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    correct_index: Mapped[int] = mapped_column(Integer, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)

    topic: Mapped[SyllabusTopic] = relationship(back_populates="questions")

    def __repr__(self) -> str:
        return f"<MCQQuestion id={self.id} topic_id={self.topic_id}>"
