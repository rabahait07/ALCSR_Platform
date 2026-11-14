from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.timeutils import utc_now
from app.models.types import UTCDateTime

if TYPE_CHECKING:
    from app.models.challenge import CodingChallenge
    from app.models.user import User


class ChallengeSubmission(Base):
    """A student's submitted solution, with the test results reported by the browser sandbox.

    The code is stored as text only. The backend never executes it.
    """

    __tablename__ = "challenge_submissions"
    __table_args__ = (
        CheckConstraint(
            "total_tests >= 0 AND passed_tests >= 0 AND passed_tests <= total_tests",
            name="ck_challenge_submissions_test_counts",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    challenge_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("coding_challenges.id", ondelete="CASCADE"), index=True, nullable=False
    )
    code: Mapped[str] = mapped_column(Text, nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    passed_tests: Mapped[int] = mapped_column(Integer, nullable=False)
    total_tests: Mapped[int] = mapped_column(Integer, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(
        UTCDateTime, default=utc_now, nullable=False
    )

    user: Mapped[User] = relationship(back_populates="challenge_submissions")
    challenge: Mapped[CodingChallenge] = relationship(back_populates="submissions")

    def __repr__(self) -> str:
        return (
            f"<ChallengeSubmission id={self.id} user_id={self.user_id} "
            f"challenge_id={self.challenge_id} passed={self.passed}>"
        )
