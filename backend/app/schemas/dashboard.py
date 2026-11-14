from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class RecentActivityOut(BaseModel):
    """One recent quiz attempt or challenge submission by the current user."""

    activity_type: Literal["quiz", "challenge"]
    # Topic title for quizzes, challenge title for challenges.
    title: str
    spec_code: str
    # Correct answers out of total questions, or passed tests out of total tests.
    score: int = Field(ge=0)
    total: int = Field(ge=0)
    occurred_at: datetime


class PaperProgressOut(BaseModel):
    """The current user's progress across one paper's sub-topics."""

    paper: int = Field(ge=1, le=2)
    title: str
    topics_total: int = Field(ge=0)
    # Sub-topics with at least one completed quiz attempt.
    topics_attempted: int = Field(ge=0)
    # Mean of the user's best quiz percentage per attempted sub-topic; 0 when none attempted.
    average_quiz_percentage: float = Field(ge=0, le=100)
    challenges_total: int = Field(ge=0)
    challenges_solved: int = Field(ge=0)


class DashboardMetricsResponse(BaseModel):
    quizzes_completed: int = Field(ge=0)
    average_quiz_percentage: float = Field(ge=0, le=100)
    challenges_solved: int = Field(ge=0)
    challenges_total: int = Field(ge=0)
    paper_progress: list[PaperProgressOut] = Field(default_factory=list)
    recent_activity: list[RecentActivityOut] = Field(default_factory=list)
