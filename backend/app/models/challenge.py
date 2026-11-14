from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, CheckConstraint, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import Difficulty, sql_in_list

if TYPE_CHECKING:
    from app.models.challenge_submission import ChallengeSubmission
    from app.models.topic import SyllabusTopic


class CodingChallenge(Base):
    """A Python challenge that is run and tested in the browser with Pyodide.

    ``test_cases`` is a list of ``{"input_args": [...], "expected": ..., "description": "..."}``
    objects. ``function_name`` is the function the student must define; each test case calls
    it with ``input_args`` and compares the return value with ``expected``.
    """

    __tablename__ = "coding_challenges"
    __table_args__ = (
        CheckConstraint(
            f"difficulty IN ({sql_in_list(Difficulty)})",
            name="ck_coding_challenges_difficulty",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    topic_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("syllabus_topics.id", ondelete="CASCADE"), index=True, nullable=False
    )
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(16), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    function_name: Mapped[str] = mapped_column(String(128), nullable=False)
    starter_code: Mapped[str] = mapped_column(Text, nullable=False)
    test_cases: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False)

    topic: Mapped[SyllabusTopic] = relationship(back_populates="challenges")
    submissions: Mapped[list[ChallengeSubmission]] = relationship(
        back_populates="challenge", cascade="all, delete-orphan", passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"<CodingChallenge id={self.id} slug={self.slug!r}>"
