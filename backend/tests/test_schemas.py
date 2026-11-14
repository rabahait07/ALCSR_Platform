from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.models import (
    ChallengeSubmission,
    CodingChallenge,
    MCQQuestion,
    ResourceType,
    StaticResource,
    SyllabusTopic,
    User,
)
from app.schemas import (
    ChallengeSubmissionIn,
    ChallengeSubmissionOut,
    CodingChallengeDetailOut,
    CodingChallengeListOut,
    DashboardMetricsResponse,
    ExamSectionResourcesResponse,
    MCQQuestionPublicOut,
    PaperHierarchyOut,
    PaperProgressOut,
    PastPaperRowOut,
    PastPapersResponse,
    QuestionResultOut,
    QuizResultOut,
    QuizSubmissionIn,
    RecentActivityOut,
    ResourceItemOut,
    SubtopicOut,
    SyllabusTreeResponse,
    Token,
    TopicResourcesResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)

NOW = datetime(2026, 11, 14, 12, 0, tzinfo=timezone.utc)


def make_question() -> MCQQuestion:
    return MCQQuestion(
        id=7,
        topic_id=3,
        question_text="Which register holds the address of the next instruction?",
        code_snippet=None,
        options=["MAR", "MDR", "PC", "ACC"],
        correct_index=2,
        explanation="The program counter holds the address of the next instruction.",
    )


def make_challenge() -> CodingChallenge:
    return CodingChallenge(
        id=1,
        topic_id=3,
        slug="binary-to-denary",
        title="Binary to Denary",
        difficulty="Easy",
        description="Convert a binary string to its denary value.",
        function_name="binary_to_denary",
        starter_code="def binary_to_denary(bits):\n    pass\n",
        test_cases=[
            {"input_args": ["101"], "expected": 5, "description": "101 is 5"},
            {"input_args": [[1, 2], {"k": None}], "expected": [3.5, True], "description": "nested"},
        ],
    )


# --- Quiz: answers must not leak before grading -------------------------------------------


def test_public_question_schema_has_no_answer_fields() -> None:
    assert "correct_index" not in MCQQuestionPublicOut.model_fields
    assert "explanation" not in MCQQuestionPublicOut.model_fields


def test_public_question_serialisation_excludes_answer() -> None:
    payload = MCQQuestionPublicOut.model_validate(make_question()).model_dump()

    assert set(payload) == {"id", "topic_id", "question_text", "code_snippet", "options"}
    assert "program counter" not in MCQQuestionPublicOut.model_validate(
        make_question()
    ).model_dump_json()


def test_quiz_submission_accepts_json_object_keys() -> None:
    submission = QuizSubmissionIn.model_validate_json('{"answers": {"7": 2, "8": 0}}')

    assert submission.answers == {7: 2, 8: 0}


@pytest.mark.parametrize(
    "answers",
    [{}, {7: 4}, {7: -1}, {0: 1}, {-3: 1}],
    ids=["empty", "index-too-high", "index-negative", "id-zero", "id-negative"],
)
def test_quiz_submission_rejects_invalid_answers(answers: dict[int, int]) -> None:
    with pytest.raises(ValidationError):
        QuizSubmissionIn(answers=answers)


def test_quiz_result_allows_unanswered_question() -> None:
    result = QuizResultOut(
        attempt_id=1,
        topic_id=3,
        score=1,
        total_questions=2,
        percentage=50.0,
        results=[
            QuestionResultOut(
                question_id=7, selected_index=2, correct_index=2, is_correct=True, explanation="PC"
            ),
            QuestionResultOut(
                question_id=8, selected_index=None, correct_index=0, is_correct=False, explanation="x"
            ),
        ],
    )

    assert result.results[1].selected_index is None


def test_quiz_result_rejects_percentage_over_100() -> None:
    with pytest.raises(ValidationError):
        QuizResultOut(
            attempt_id=1, topic_id=3, score=1, total_questions=1, percentage=120.0, results=[]
        )


# --- Users ---------------------------------------------------------------------------------


def test_user_create_normalises_name_and_email() -> None:
    user = UserCreate(full_name="  Ada Lovelace ", email="Student@ALCSR.edu", password="s3cure-pass")

    assert user.full_name == "Ada Lovelace"
    assert user.email == "student@alcsr.edu"
    assert UserLogin(email="Student@ALCSR.edu", password="x").email == "student@alcsr.edu"


@pytest.mark.parametrize(
    "overrides",
    [
        {"email": "not-an-email"},
        {"password": "short"},
        {"password": "é" * 40},
        {"full_name": "   "},
    ],
    ids=["bad-email", "short-password", "password-over-72-bytes", "blank-name"],
)
def test_user_create_rejects_invalid_input(overrides: dict[str, str]) -> None:
    data = {"full_name": "Ada", "email": "student@alcsr.edu", "password": "s3cure-pass"} | overrides

    with pytest.raises(ValidationError):
        UserCreate(**data)


def test_token_response_never_contains_password_hash() -> None:
    user = User(
        id=1,
        full_name="Ada Lovelace",
        email="student@alcsr.edu",
        hashed_password="not-a-real-hash",
        created_at=NOW,
    )

    token = Token(access_token="abc", user=UserResponse.model_validate(user))

    assert token.token_type == "bearer"
    assert "hashed_password" not in token.model_dump()["user"]
    assert "not-a-real-hash" not in token.model_dump_json()


# --- Syllabus and resources ----------------------------------------------------------------


def test_syllabus_tree_builds_from_orm_topics() -> None:
    topic = SyllabusTopic(
        id=1,
        paper=1,
        section_code="1.1",
        section_title="1.1 The characteristics of contemporary processors",
        spec_code="1.1.1",
        title="Structure and function of the processor",
        slug="structure-and-function-of-the-processor",
    )

    tree = SyllabusTreeResponse(
        papers=[
            PaperHierarchyOut(
                paper=1,
                title="Computer Systems",
                sections=[
                    {
                        "section_code": topic.section_code,
                        "section_title": topic.section_title,
                        "subtopics": [SubtopicOut.model_validate(topic)],
                    }
                ],
            )
        ]
    )

    assert tree.papers[0].sections[0].subtopics[0].spec_code == "1.1.1"


def test_resource_schemas_build_from_orm_resources() -> None:
    worksheet = StaticResource(
        id=1,
        topic_id=1,
        resource_type="worksheet",
        title="Worksheet 1 Questions - CPU Components and Registers",
        file_url="/pdfs/worksheets/1.1.1/worksheet-1-questions.pdf",
        display_order=1,
    )
    question_paper = StaticResource(
        id=2,
        resource_type="past_paper_qp",
        paper=1,
        exam_series="June 2024",
        title="June 2024 Paper 1 QP",
        file_url="/pdfs/past-papers/june-2024-paper-1-qp.pdf",
        display_order=0,
    )
    topic = SubtopicOut(id=1, spec_code="1.1.1", title="Processor", slug="processor")

    topic_resources = TopicResourcesResponse(
        topic=topic, worksheets=[ResourceItemOut.model_validate(worksheet)]
    )
    past_papers = PastPapersResponse(
        paper_1=[
            PastPaperRowOut(
                paper=1,
                exam_series="June 2024",
                question_paper=ResourceItemOut.model_validate(question_paper),
            )
        ]
    )
    exam_section = ExamSectionResourcesResponse(
        paper=1, section_code="1.3", section_title="1.3 Exchanging data"
    )

    assert topic_resources.worksheets[0].resource_type is ResourceType.WORKSHEET
    assert topic_resources.worksheet_answers == []
    assert past_papers.paper_1[0].mark_scheme is None
    assert past_papers.paper_2 == []
    assert exam_section.exam_packs == []


def test_resource_item_rejects_unknown_resource_type() -> None:
    with pytest.raises(ValidationError):
        ResourceItemOut(id=1, resource_type="video", title="x", file_url="/x", display_order=0)


# --- Coding challenges ---------------------------------------------------------------------


def test_challenge_schemas_build_from_orm_challenge() -> None:
    challenge = make_challenge()

    listed = CodingChallengeListOut.model_validate(challenge)
    detail = CodingChallengeDetailOut.model_validate(challenge)

    assert listed.solved is False
    assert listed.model_copy(update={"solved": True}).solved is True
    assert detail.test_cases[0].input_args == ["101"]
    assert detail.test_cases[1].expected == [3.5, True]


def test_challenge_submission_out_builds_from_orm() -> None:
    submission = ChallengeSubmission(
        id=1, user_id=1, challenge_id=1, code="pass", passed=False, passed_tests=0,
        total_tests=2, submitted_at=NOW,
    )

    assert ChallengeSubmissionOut.model_validate(submission).total_tests == 2


@pytest.mark.parametrize(
    ("passed", "passed_tests", "total_tests"),
    [(True, 3, 3), (False, 2, 3), (False, 0, 0)],
)
def test_challenge_submission_accepts_consistent_results(
    passed: bool, passed_tests: int, total_tests: int
) -> None:
    submission = ChallengeSubmissionIn(
        code="def f(): pass", passed=passed, passed_tests=passed_tests, total_tests=total_tests
    )

    assert submission.passed is passed


@pytest.mark.parametrize(
    ("code", "passed", "passed_tests", "total_tests"),
    [
        ("def f(): pass", True, 2, 3),
        ("def f(): pass", False, 3, 3),
        ("def f(): pass", False, 4, 3),
        ("def f(): pass", True, 0, 0),
        ("", True, 3, 3),
    ],
    ids=["passed-but-failures", "not-passed-but-all-pass", "more-passed-than-total",
         "passed-with-no-tests", "empty-code"],
)
def test_challenge_submission_rejects_inconsistent_results(
    code: str, passed: bool, passed_tests: int, total_tests: int
) -> None:
    with pytest.raises(ValidationError):
        ChallengeSubmissionIn(
            code=code, passed=passed, passed_tests=passed_tests, total_tests=total_tests
        )


# --- Dashboard -----------------------------------------------------------------------------


def test_dashboard_response_round_trips_through_json() -> None:
    dashboard = DashboardMetricsResponse(
        quizzes_completed=4,
        average_quiz_percentage=72.5,
        challenges_solved=1,
        challenges_total=10,
        paper_progress=[
            PaperProgressOut(
                paper=1, title="Computer Systems", topics_total=16, topics_attempted=3,
                average_quiz_percentage=72.5, challenges_total=4, challenges_solved=1,
            )
        ],
        recent_activity=[
            RecentActivityOut(
                activity_type="quiz", title="Structure and function of the processor",
                spec_code="1.1.1", score=8, total=10, occurred_at=NOW,
            )
        ],
    )

    restored = DashboardMetricsResponse.model_validate_json(dashboard.model_dump_json())

    assert restored == dashboard


def test_recent_activity_rejects_unknown_type() -> None:
    with pytest.raises(ValidationError):
        RecentActivityOut(
            activity_type="worksheet", title="x", spec_code="1.1.1", score=0, total=0, occurred_at=NOW
        )
