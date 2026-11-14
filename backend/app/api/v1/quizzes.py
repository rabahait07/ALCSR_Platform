from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.quiz import QuizOut, QuizResultOut, QuizSubmissionIn, QuizTopicsResponse
from app.services import quizzes as quiz_service

router = APIRouter(prefix="/quizzes", tags=["quizzes"])

SpecCode = Annotated[str, Path(max_length=16, examples=["1.1.1"])]


def _topic_not_found(spec_code: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Topic {spec_code} not found"
    )


# Declared before /{spec_code} so that "topics" is not treated as a specification code.
@router.get("/topics", response_model=QuizTopicsResponse)
async def read_quiz_topics(current_user: CurrentUser, db: DbSession) -> QuizTopicsResponse:
    """Every sub-topic with the user's best score and number of attempts."""
    return await quiz_service.list_quiz_topics(db, current_user)


@router.get("/{spec_code}", response_model=QuizOut)
async def read_quiz(spec_code: SpecCode, current_user: CurrentUser, db: DbSession) -> QuizOut:
    """Up to ten questions for a sub-topic. Correct answers are never included."""
    quiz = await quiz_service.get_quiz(db, spec_code)
    if quiz is None:
        raise _topic_not_found(spec_code)
    return quiz


@router.post(
    "/{spec_code}/submit", response_model=QuizResultOut, status_code=status.HTTP_201_CREATED
)
async def submit_quiz(
    spec_code: SpecCode, submission: QuizSubmissionIn, current_user: CurrentUser, db: DbSession
) -> QuizResultOut:
    """Grade the answers on the server, record the attempt and reveal the correct answers."""
    try:
        result = await quiz_service.grade_quiz(db, current_user, spec_code, submission)
    except quiz_service.InvalidQuizSubmissionError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from None
    if result is None:
        raise _topic_not_found(spec_code)
    return result
