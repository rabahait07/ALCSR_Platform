from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.quiz import MCQ_OPTION_COUNT
from app.schemas.syllabus import SubtopicOut

# The number of questions served per quiz, and so the most answers one submission can hold.
QUIZ_LENGTH = 10


class MCQQuestionPublicOut(BaseModel):
    """A question as shown to the student before submitting.

    Deliberately has no ``correct_index`` or ``explanation`` field: answers must never reach
    the client before the quiz is graded on the server. Do not add them here.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    topic_id: int
    question_text: str
    code_snippet: str | None = None
    options: list[str]


class QuizOut(BaseModel):
    """A quiz for one sub-topic: up to ``QUIZ_LENGTH`` questions without their answers."""

    topic: SubtopicOut
    questions: list[MCQQuestionPublicOut]


class QuizTopicProgressOut(BaseModel):
    """One sub-topic in the quiz topic selector, with the current user's progress."""

    id: int
    paper: int = Field(ge=1, le=2)
    section_code: str
    spec_code: str
    title: str
    slug: str
    # Questions available for this sub-topic; 0 means there is no quiz to play yet.
    question_count: int = Field(ge=0)
    attempts_count: int = Field(ge=0)
    # Score and length of the user's best attempt (highest percentage); null if never attempted.
    best_score: int | None = None
    total_questions: int | None = None


class QuizTopicsResponse(BaseModel):
    topics: list[QuizTopicProgressOut] = Field(default_factory=list)


class QuizSubmissionIn(BaseModel):
    """The student's chosen option for each question: ``{question_id: selected_index}``."""

    answers: dict[int, int] = Field(min_length=1, max_length=QUIZ_LENGTH)

    @field_validator("answers")
    @classmethod
    def validate_answers(cls, answers: dict[int, int]) -> dict[int, int]:
        for question_id, selected_index in answers.items():
            if question_id < 1:
                raise ValueError(f"Invalid question id: {question_id}")
            if not 0 <= selected_index < MCQ_OPTION_COUNT:
                raise ValueError(
                    f"Selected index for question {question_id} must be between 0 and "
                    f"{MCQ_OPTION_COUNT - 1}"
                )
        return answers


class QuestionResultOut(BaseModel):
    """The graded outcome for one question, returned only after submission."""

    question_id: int
    # None when the student left the question unanswered.
    selected_index: int | None = Field(default=None, ge=0, lt=MCQ_OPTION_COUNT)
    correct_index: int = Field(ge=0, lt=MCQ_OPTION_COUNT)
    is_correct: bool
    explanation: str


class QuizResultOut(BaseModel):
    attempt_id: int
    topic_id: int
    score: int = Field(ge=0)
    total_questions: int = Field(ge=1)
    percentage: float = Field(ge=0, le=100)
    results: list[QuestionResultOut]
