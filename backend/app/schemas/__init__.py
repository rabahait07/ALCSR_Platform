"""Pydantic v2 request and response schemas."""

from app.schemas.challenge import (
    ChallengeSubmissionIn,
    ChallengeSubmissionOut,
    CodingChallengeDetailOut,
    CodingChallengeListOut,
    TestCaseSchema,
)
from app.schemas.dashboard import DashboardMetricsResponse, PaperProgressOut, RecentActivityOut
from app.schemas.quiz import (
    MCQQuestionPublicOut,
    QuestionResultOut,
    QuizOut,
    QuizResultOut,
    QuizSubmissionIn,
    QuizTopicProgressOut,
    QuizTopicsResponse,
)
from app.schemas.resource import (
    ExamSectionResourcesResponse,
    PastPaperRowOut,
    PastPapersResponse,
    ResourceItemOut,
    TopicResourcesResponse,
)
from app.schemas.syllabus import (
    MajorSectionOut,
    PaperHierarchyOut,
    SubtopicOut,
    SyllabusTreeResponse,
)
from app.schemas.user import Token, UserCreate, UserLogin, UserResponse

__all__ = [
    "ChallengeSubmissionIn",
    "ChallengeSubmissionOut",
    "CodingChallengeDetailOut",
    "CodingChallengeListOut",
    "DashboardMetricsResponse",
    "ExamSectionResourcesResponse",
    "MCQQuestionPublicOut",
    "MajorSectionOut",
    "PaperHierarchyOut",
    "PaperProgressOut",
    "PastPaperRowOut",
    "PastPapersResponse",
    "QuestionResultOut",
    "QuizOut",
    "QuizResultOut",
    "QuizSubmissionIn",
    "QuizTopicProgressOut",
    "QuizTopicsResponse",
    "RecentActivityOut",
    "ResourceItemOut",
    "SubtopicOut",
    "SyllabusTreeResponse",
    "TestCaseSchema",
    "Token",
    "TopicResourcesResponse",
    "UserCreate",
    "UserLogin",
    "UserResponse",
]
