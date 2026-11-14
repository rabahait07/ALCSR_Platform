from datetime import datetime
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, JsonValue, model_validator

from app.models.enums import Difficulty

MAX_SUBMISSION_CODE_LENGTH = 50_000


class TestCaseSchema(BaseModel):
    """One test: call the challenge function with ``input_args`` and expect ``expected``."""

    # Stops pytest from trying to collect this class as a test when it is imported in tests.
    __test__ = False

    input_args: list[JsonValue]
    expected: JsonValue
    description: str


class CodingChallengeListOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    topic_id: int
    slug: str
    title: str
    difficulty: Difficulty
    # True when the current user has at least one passing submission.
    solved: bool = False


class CodingChallengeDetailOut(BaseModel):
    """Everything the in-browser Pyodide runner needs, including the test cases."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    topic_id: int
    slug: str
    title: str
    difficulty: Difficulty
    description: str
    function_name: str
    starter_code: str
    test_cases: list[TestCaseSchema]
    solved: bool = False


class ChallengeSubmissionIn(BaseModel):
    """Results reported by the browser after running the code against the test cases."""

    code: str = Field(min_length=1, max_length=MAX_SUBMISSION_CODE_LENGTH)
    passed: bool
    passed_tests: int = Field(ge=0)
    total_tests: int = Field(ge=0)

    @model_validator(mode="after")
    def results_are_consistent(self) -> Self:
        if self.passed_tests > self.total_tests:
            raise ValueError("passed_tests cannot be greater than total_tests")
        all_passed = self.total_tests > 0 and self.passed_tests == self.total_tests
        if self.passed != all_passed:
            raise ValueError("passed must be true only when every test passed")
        return self


class ChallengeSubmissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    challenge_id: int
    code: str
    passed: bool
    passed_tests: int
    total_tests: int
    submitted_at: datetime
