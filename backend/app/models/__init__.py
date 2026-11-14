"""SQLAlchemy ORM models.

Every model module is imported here so that importing ``app.models`` registers all tables on
``Base.metadata`` (used by table creation at startup and by Alembic autogenerate).
"""

from app.core.database import Base
from app.models.challenge import CodingChallenge
from app.models.challenge_submission import ChallengeSubmission
from app.models.enums import Difficulty, ResourceType
from app.models.quiz import MCQ_OPTION_COUNT, MCQQuestion
from app.models.quiz_attempt import MCQAttempt
from app.models.resource import StaticResource
from app.models.topic import PAPER_TITLES, SyllabusTopic
from app.models.user import User

__all__ = [
    "MCQ_OPTION_COUNT",
    "PAPER_TITLES",
    "Base",
    "ChallengeSubmission",
    "CodingChallenge",
    "Difficulty",
    "MCQAttempt",
    "MCQQuestion",
    "ResourceType",
    "StaticResource",
    "SyllabusTopic",
    "User",
]
