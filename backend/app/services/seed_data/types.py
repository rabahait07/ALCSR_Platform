from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SeedTopic:
    spec_code: str
    title: str
    # Three areas of the sub-topic, used to title its sample worksheets and notes.
    focus_areas: tuple[str, str, str]


@dataclass(frozen=True)
class SeedSection:
    paper: int
    code: str
    # Section name without its code, e.g. "Exchanging data".
    name: str
    topics: tuple[SeedTopic, ...]

    @property
    def title(self) -> str:
        return f"{self.code} {self.name}"


@dataclass(frozen=True)
class SeedQuestion:
    text: str
    options: tuple[str, str, str, str]
    # Index into ``options`` of the correct answer.
    answer: int
    explanation: str
    code: str | None = None


@dataclass(frozen=True)
class SeedChallenge:
    slug: str
    spec_code: str
    title: str
    difficulty: str
    function_name: str
    description: str
    starter_code: str
    test_cases: tuple[dict[str, Any], ...]
