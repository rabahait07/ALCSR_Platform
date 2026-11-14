from collections import Counter
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    CodingChallenge,
    MCQQuestion,
    ResourceType,
    StaticResource,
    SyllabusTopic,
)
from app.services.seed import QUESTIONS, seed_database, slugify
from app.services.seed_data.challenges import CHALLENGES
from app.services.seed_data.syllabus import EXAM_SERIES, SECTIONS
from app.services.seed_data.types import SeedSection

CORE_TOPICS = ("1.1.1", "1.3.2", "1.3.3", "1.4.1", "2.2.1", "2.3.1")
ALL_SPEC_CODES = [topic.spec_code for section in SECTIONS for topic in section.topics]
FRONTEND_PUBLIC = Path(__file__).resolve().parents[2] / "frontend" / "public"


@pytest_asyncio.fixture
async def seeded(session: AsyncSession) -> AsyncSession:
    assert await seed_database(session) is True
    return session


async def count(session: AsyncSession, model: type, *conditions: object) -> int:
    return await session.scalar(select(func.count()).select_from(model).where(*conditions)) or 0


# --- Seed data, checked without a database ---------------------------------------------------


def test_syllabus_has_the_full_ocr_h446_structure() -> None:
    by_section = {section.code: [topic.spec_code for topic in section.topics] for section in SECTIONS}

    assert by_section == {
        "1.1": ["1.1.1", "1.1.2", "1.1.3"],
        "1.2": ["1.2.1", "1.2.2", "1.2.3", "1.2.4"],
        "1.3": ["1.3.1", "1.3.2", "1.3.3", "1.3.4"],
        "1.4": ["1.4.1", "1.4.2", "1.4.3"],
        "1.5": ["1.5.1", "1.5.2"],
        "2.1": ["2.1.1", "2.1.2", "2.1.3", "2.1.4", "2.1.5"],
        "2.2": ["2.2.1", "2.2.2"],
        "2.3": ["2.3.1"],
    }
    assert all(section.paper == int(section.code[0]) for section in SECTIONS)
    slugs = [slugify(topic.title) for section in SECTIONS for topic in section.topics]
    assert len(set(slugs)) == 24


def test_every_topic_has_enough_questions() -> None:
    assert set(QUESTIONS) == set(ALL_SPEC_CODES)
    for spec_code in ALL_SPEC_CODES:
        minimum = 10 if spec_code in CORE_TOPICS else 3
        assert len(QUESTIONS[spec_code]) >= minimum, spec_code


def test_every_question_is_well_formed() -> None:
    all_questions = [question for questions in QUESTIONS.values() for question in questions]

    assert len({question.text for question in all_questions}) == len(all_questions)
    for question in all_questions:
        assert question.text.strip().endswith("?"), question.text
        assert len(question.options) == 4, question.text
        assert len(set(question.options)) == 4, question.text
        assert all(option.strip() for option in question.options), question.text
        assert 0 <= question.answer <= 3, question.text
        assert len(question.explanation) >= 60, question.text
        if "shown" in question.text:
            assert question.code, question.text


def test_correct_answers_are_spread_across_all_four_positions() -> None:
    positions = Counter(
        question.answer for questions in QUESTIONS.values() for question in questions
    )
    total = sum(positions.values())

    # No position should be a give-away: each holds roughly a quarter of the answers.
    assert set(positions) == {0, 1, 2, 3}
    assert all(0.15 <= count / total <= 0.35 for count in positions.values()), positions


def reference_fizzbuzz(n: int) -> list[str]:
    return [
        "FizzBuzz" if i % 15 == 0 else "Fizz" if i % 3 == 0 else "Buzz" if i % 5 == 0 else str(i)
        for i in range(1, n + 1)
    ]


def reference_binary_search(arr: list[int], target: int) -> int:
    low, high = 0, len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        if arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1


def test_challenge_test_cases_are_satisfied_by_a_correct_solution() -> None:
    solutions = {"fizzbuzz": reference_fizzbuzz, "binary-search": reference_binary_search}
    by_slug = {challenge.slug: challenge for challenge in CHALLENGES}

    assert set(by_slug) == set(solutions)
    assert len(by_slug["fizzbuzz"].test_cases) == 4
    assert len(by_slug["binary-search"].test_cases) == 5
    for slug, solve in solutions.items():
        for test_case in by_slug[slug].test_cases:
            assert set(test_case) == {"input_args", "expected", "description"}
            assert solve(*test_case["input_args"]) == test_case["expected"], test_case


def test_challenges_match_their_specification() -> None:
    fizzbuzz, binary_search = CHALLENGES

    assert (fizzbuzz.slug, fizzbuzz.spec_code, fizzbuzz.difficulty) == ("fizzbuzz", "2.2.1", "Easy")
    assert (fizzbuzz.title, fizzbuzz.function_name) == ("FizzBuzz Sequence", "fizzbuzz")
    assert fizzbuzz.starter_code == (
        "def fizzbuzz(n: int) -> list[str]:\n    # Write your solution here\n    pass\n"
    )
    assert "1 <= n <= 1000" in fizzbuzz.description
    assert (binary_search.slug, binary_search.spec_code) == ("binary-search", "2.3.1")
    assert (binary_search.difficulty, binary_search.title) == ("Medium", "Binary Search")
    assert binary_search.function_name == "binary_search"
    assert binary_search.starter_code == (
        "def binary_search(arr: list[int], target: int) -> int:\n"
        "    # Implement binary search on a sorted list\n"
        "    # Return the index of target, or -1 if not found\n"
        "    pass\n"
    )
    assert "O(log n)" in binary_search.description
    # The starter code must define the function the runner will call.
    for challenge in CHALLENGES:
        assert f"def {challenge.function_name}(" in challenge.starter_code


# --- Seeding a database ----------------------------------------------------------------------


async def test_seed_populates_every_table(seeded: AsyncSession) -> None:
    def of_type(resource_type: ResourceType) -> object:
        return StaticResource.resource_type == resource_type

    assert await count(seeded, SyllabusTopic) == 24
    assert await count(seeded, SyllabusTopic, SyllabusTopic.paper == 1) == 16
    assert await count(seeded, SyllabusTopic, SyllabusTopic.paper == 2) == 8
    assert await count(seeded, MCQQuestion) == sum(len(q) for q in QUESTIONS.values())
    assert await count(seeded, CodingChallenge) == 2
    assert await count(seeded, StaticResource, of_type(ResourceType.WORKSHEET)) == 24 * 3
    assert await count(seeded, StaticResource, of_type(ResourceType.WORKSHEET_ANSWER)) == 24 * 3
    assert await count(seeded, StaticResource, of_type(ResourceType.LEARNING_NOTE)) == 24 * 2
    assert await count(seeded, StaticResource, of_type(ResourceType.REVIEWING_NOTE)) == 24 * 2
    assert await count(seeded, StaticResource, of_type(ResourceType.EXAM_PACK)) == 8 * 2
    assert await count(seeded, StaticResource, of_type(ResourceType.MARK_SCHEME)) == 8 * 2
    for past_paper_type in (
        ResourceType.PAST_PAPER_QP,
        ResourceType.PAST_PAPER_MS,
        ResourceType.PAST_PAPER_WALKTHROUGH,
    ):
        assert await count(seeded, StaticResource, of_type(past_paper_type)) == 2 * 9


async def test_seed_is_idempotent(seeded: AsyncSession) -> None:
    before = (
        await count(seeded, SyllabusTopic),
        await count(seeded, StaticResource),
        await count(seeded, MCQQuestion),
        await count(seeded, CodingChallenge),
    )

    assert await seed_database(seeded) is False
    assert await seed_database(seeded) is False

    after = (
        await count(seeded, SyllabusTopic),
        await count(seeded, StaticResource),
        await count(seeded, MCQQuestion),
        await count(seeded, CodingChallenge),
    )
    assert after == before


async def test_seed_does_not_touch_a_database_that_already_has_topics(
    session: AsyncSession,
) -> None:
    session.add(
        SyllabusTopic(
            paper=1, section_code="1.1", section_title="1.1 Custom", spec_code="1.1.1",
            title="My own topic", slug="my-own-topic",
        )
    )
    await session.commit()

    assert await seed_database(session) is False
    assert await count(session, SyllabusTopic) == 1
    assert await count(session, MCQQuestion) == 0


async def test_seeded_file_urls_point_at_files_that_exist(seeded: AsyncSession) -> None:
    urls = set((await seeded.execute(select(StaticResource.file_url))).scalars())
    local_urls = {url for url in urls if url.startswith("/")}
    external_urls = urls - local_urls

    assert local_urls == {
        "/resources/worksheets/sample-worksheet.pdf",
        "/resources/notes/sample-notes.pdf",
        "/resources/exam-packs/sample-exam-pack.pdf",
        "/resources/past-papers/sample-past-paper.pdf",
    }
    assert external_urls == {
        "https://www.youtube.com/results?search_query=OCR+H446+Computer+Science+Past+Paper"
    }
    for url in local_urls:
        pdf = FRONTEND_PUBLIC / url.lstrip("/")
        assert pdf.is_file(), f"{url} is seeded but {pdf} does not exist"
        assert pdf.read_bytes().startswith(b"%PDF-"), pdf


# --- The seeded content through the API ------------------------------------------------------


async def test_seeded_syllabus_tree(client: AsyncClient, seeded: AsyncSession) -> None:
    papers = (await client.get("/api/v1/syllabus/tree")).json()["papers"]

    assert [paper["title"] for paper in papers] == ["Computer Systems", "Algorithms and Programming"]
    codes = [
        subtopic["spec_code"]
        for paper in papers
        for section in paper["sections"]
        for subtopic in section["subtopics"]
    ]
    assert codes == ALL_SPEC_CODES
    first_section = papers[0]["sections"][0]
    assert first_section["section_title"] == (
        "1.1 The characteristics of contemporary processors, input, output and storage devices"
    )
    assert first_section["subtopics"][0]["title"] == "Structure and function of the processor"


@pytest.mark.parametrize("spec_code", ALL_SPEC_CODES)
async def test_every_seeded_topic_has_worksheets_and_notes(
    client: AsyncClient, seeded: AsyncSession, spec_code: str
) -> None:
    worksheets = (await client.get(f"/api/v1/resources/worksheets/{spec_code}")).json()
    notes = (await client.get(f"/api/v1/resources/notes/{spec_code}")).json()

    assert len(worksheets["worksheets"]) == len(worksheets["answers"]) == 3
    assert len(notes["learning_notes"]) == len(notes["reviewing_notes"]) == 2
    # Each worksheet lines up with its answers, and each learning note with its reviewing note.
    for questions, answers in zip(worksheets["worksheets"], worksheets["answers"], strict=True):
        assert questions["title"].replace("Questions", "Answers") == answers["title"]
    for learning, reviewing in zip(notes["learning_notes"], notes["reviewing_notes"], strict=True):
        assert learning["title"].replace("Learning", "Reviewing") == reviewing["title"]


async def test_seeded_worksheet_titles(client: AsyncClient, seeded: AsyncSession) -> None:
    body = (await client.get("/api/v1/resources/worksheets/1.1.1")).json()

    assert [item["title"] for item in body["worksheets"]] == [
        "Worksheet 1 Questions - CPU Components and Registers",
        "Worksheet 2 Questions - CPU Buses",
        "Worksheet 3 Questions - The Fetch-Decode-Execute Cycle",
    ]
    assert body["answers"][0]["title"] == "Worksheet 1 Answers - CPU Components and Registers"


@pytest.mark.parametrize("section", SECTIONS, ids=lambda section: section.code)
async def test_every_seeded_section_has_exam_packs(
    client: AsyncClient, seeded: AsyncSession, section: SeedSection
) -> None:
    slug = section.code.replace(".", "-")

    body = (await client.get(f"/api/v1/resources/exam-questions/{slug}")).json()

    assert body["section_title"] == section.title
    assert [item["title"] for item in body["exam_packs"]] == [
        f"Exam Question Pack 1 - {section.name}",
        f"Exam Question Pack 2 - {section.name}",
    ]
    assert [item["title"] for item in body["mark_schemes"]] == [
        f"Pack 1 Mark Scheme - {section.name}",
        f"Pack 2 Mark Scheme - {section.name}",
    ]


async def test_seeded_past_papers(client: AsyncClient, seeded: AsyncSession) -> None:
    body = (await client.get("/api/v1/resources/past-papers")).json()

    for key, paper in (("paper_1", 1), ("paper_2", 2)):
        rows = body[key]
        assert [row["exam_series"] for row in rows] == list(EXAM_SERIES)
        for row in rows:
            assert row["paper"] == paper
            assert row["question_paper_url"] == "/resources/past-papers/sample-past-paper.pdf"
            assert row["mark_scheme_url"] == "/resources/past-papers/sample-past-paper.pdf"
            assert row["walkthrough_url"].startswith("https://www.youtube.com/results?")


async def test_every_seeded_topic_is_playable_and_never_leaks_answers(
    client: AsyncClient, seeded: AsyncSession, auth_headers: dict[str, str]
) -> None:
    topics = (await client.get("/api/v1/quizzes/topics", headers=auth_headers)).json()["topics"]

    assert [topic["spec_code"] for topic in topics] == ALL_SPEC_CODES
    for topic in topics:
        expected = 10 if topic["spec_code"] in CORE_TOPICS else 3
        assert topic["question_count"] >= expected, topic["spec_code"]

        response = await client.get(f"/api/v1/quizzes/{topic['spec_code']}", headers=auth_headers)
        questions = response.json()["questions"]
        assert len(questions) == min(topic["question_count"], 10), topic["spec_code"]
        assert "correct_index" not in response.text
        assert "explanation" not in response.text


async def test_seeded_quiz_can_be_completed_with_full_marks(
    client: AsyncClient, seeded: AsyncSession, auth_headers: dict[str, str]
) -> None:
    questions = (await client.get("/api/v1/quizzes/2.3.1", headers=auth_headers)).json()["questions"]
    rows = await seeded.execute(select(MCQQuestion.id, MCQQuestion.correct_index))
    key = {question_id: correct_index for question_id, correct_index in rows}
    answers = {str(question["id"]): key[question["id"]] for question in questions}

    response = await client.post(
        "/api/v1/quizzes/2.3.1/submit", json={"answers": answers}, headers=auth_headers
    )

    assert response.status_code == 201
    assert (response.json()["score"], response.json()["percentage"]) == (10, 100.0)


async def test_seeded_challenges_through_the_api(
    client: AsyncClient, seeded: AsyncSession, auth_headers: dict[str, str]
) -> None:
    listed = (await client.get("/api/v1/challenges", headers=auth_headers)).json()
    detail = (await client.get("/api/v1/challenges/binary-search", headers=auth_headers)).json()

    assert [(item["slug"], item["difficulty"]) for item in listed] == [
        ("fizzbuzz", "Easy"),
        ("binary-search", "Medium"),
    ]
    assert detail["function_name"] == "binary_search"
    assert detail["test_cases"][0] == {
        "input_args": [[2, 5, 8, 12, 16, 23, 38], 23],
        "expected": 5,
        "description": "Target present in upper half",
    }
    assert detail["test_cases"][-1]["input_args"] == [[], 5]

    submitted = await client.post(
        "/api/v1/challenges/binary-search/submit",
        json={"code": "def binary_search(arr, target): ...", "passed": True, "passed_tests": 5,
              "total_tests": 5},
        headers=auth_headers,
    )
    assert submitted.status_code == 201
