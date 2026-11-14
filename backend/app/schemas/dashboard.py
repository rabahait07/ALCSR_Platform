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
    """Share of one paper's sub-topics the current user has attempted a quiz on."""

    paper: int = Field(ge=1, le=2)
    title: str
    topics_practiced: int = Field(ge=0)
    total_topics: int = Field(ge=0)
    percentage: float = Field(ge=0, le=100)


class DashboardMetricsResponse(BaseModel):
    # Distinct sub-topics with at least one quiz attempt, out of all sub-topics.
    topics_practiced: int = Field(ge=0)
    total_topics: int = Field(ge=0)
    # Correct answers as a percentage of questions answered across every quiz attempt.
    average_quiz_accuracy: float = Field(ge=0, le=100)
    # Distinct challenges with at least one passing submission, out of all challenges.
    challenges_solved: int = Field(ge=0)
    total_challenges: int = Field(ge=0)
    paper1_progress: PaperProgressOut
    paper2_progress: PaperProgressOut
    # Quiz attempts and challenge submissions combined, newest first.
    recent_activity: list[RecentActivityOut] = Field(default_factory=list)
