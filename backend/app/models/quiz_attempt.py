from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.timeutils import utc_now

if TYPE_CHECKING:
    from app.models.topic import SyllabusTopic
    from app.models.user import User


class MCQAttempt(Base):
    """A completed, server-graded quiz attempt."""

    __tablename__ = "mcq_attempts"
    __table_args__ = (
        CheckConstraint(
            "total_questions > 0 AND score >= 0 AND score <= total_questions",
            name="ck_mcq_attempts_score_range",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    topic_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("syllabus_topics.id", ondelete="CASCADE"), index=True, nullable=False
    )
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    total_questions: Mapped[int] = mapped_column(Integer, nullable=False)
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    user: Mapped[User] = relationship(back_populates="quiz_attempts")
    topic: Mapped[SyllabusTopic] = relationship(back_populates="quiz_attempts")

    def __repr__(self) -> str:
        return (
            f"<MCQAttempt id={self.id} user_id={self.user_id} "
            f"score={self.score}/{self.total_questions}>"
        )
