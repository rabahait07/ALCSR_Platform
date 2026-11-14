from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.quiz import MCQ_OPTION_COUNT

MAX_ANSWERS_PER_SUBMISSION = 200


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


class QuizSubmissionIn(BaseModel):
    """The student's chosen option for each question: ``{question_id: selected_index}``."""

    answers: dict[int, int] = Field(min_length=1, max_length=MAX_ANSWERS_PER_SUBMISSION)

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
