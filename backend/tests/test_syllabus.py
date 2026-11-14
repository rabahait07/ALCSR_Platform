import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ResourceType, StaticResource, SyllabusTopic
from app.services.resources import exam_series_sort_key
from app.services.syllabus import spec_code_sort_key

SECTION_TITLES = {
    "1.1": "1.1 The characteristics of contemporary processors, input, output and storage devices",
    "1.3": "1.3 Exchanging data",
    "2.1": "2.1 Elements of computational thinking",
}


def topic(spec_code: str, title: str) -> SyllabusTopic:
    section_code = spec_code.rsplit(".", 1)[0]
    return SyllabusTopic(
        paper=int(spec_code[0]),
        section_code=section_code,
        section_title=SECTION_TITLES[section_code],
        spec_code=spec_code,
        title=title,
        slug=title.lower().replace(" ", "-").replace(",", ""),
    )


def resource(
    owner: SyllabusTopic | None,
    resource_type: ResourceType,
    title: str,
    display_order: int = 0,
    paper: int | None = None,
    exam_series: str | None = None,
) -> StaticResource:
    return StaticResource(
        topic=owner,
        resource_type=resource_type,
        title=title,
        file_url=f"/pdfs/{title.lower().replace(' ', '-')}.pdf",
        display_order=display_order,
        paper=paper,
        exam_series=exam_series,
    )


@pytest_asyncio.fixture
async def topics(session: AsyncSession) -> dict[str, SyllabusTopic]:
    """Topics inserted out of specification order, to prove the API does the ordering."""
    created = {
        "2.1.1": topic("2.1.1", "Thinking abstractly"),
        "1.3.2": topic("1.3.2", "Databases"),
        "1.1.2": topic("1.1.2", "Types of processor"),
        "1.3.1": topic("1.3.1", "Compression, encryption and hashing"),
        "1.1.1": topic("1.1.1", "Structure and function of the processor"),
    }
    session.add_all(created.values())
    await session.commit()
    return created


# --- Syllabus tree -------------------------------------------------------------------------


async def test_tree_has_both_papers_even_when_empty(client: AsyncClient) -> None:
    response = await client.get("/api/v1/syllabus/tree")

    assert response.status_code == 200
    assert response.json() == {
        "papers": [
            {"paper": 1, "title": "Computer Systems", "sections": []},
            {"paper": 2, "title": "Algorithms and Programming", "sections": []},
        ]
    }


async def test_tree_groups_topics_by_paper_and_section_in_spec_order(
    client: AsyncClient, topics: dict[str, SyllabusTopic]
) -> None:
    papers = (await client.get("/api/v1/syllabus/tree")).json()["papers"]

    paper_1, paper_2 = papers
    assert [section["section_code"] for section in paper_1["sections"]] == ["1.1", "1.3"]
    assert [section["section_slug"] for section in paper_1["sections"]] == ["1-1", "1-3"]
    assert paper_1["sections"][0]["section_title"] == SECTION_TITLES["1.1"]
    assert [sub["spec_code"] for sub in paper_1["sections"][0]["subtopics"]] == ["1.1.1", "1.1.2"]
    assert [sub["spec_code"] for sub in paper_1["sections"][1]["subtopics"]] == ["1.3.1", "1.3.2"]
    assert paper_1["sections"][0]["subtopics"][0] == {
        "id": topics["1.1.1"].id,
        "spec_code": "1.1.1",
        "title": "Structure and function of the processor",
        "slug": "structure-and-function-of-the-processor",
    }
    assert [section["section_code"] for section in paper_2["sections"]] == ["2.1"]


def test_spec_codes_sort_numerically() -> None:
    codes = ["1.1.10", "1.1.2", "1.1.9", "1.1.1"]

    assert sorted(codes, key=spec_code_sort_key) == ["1.1.1", "1.1.2", "1.1.9", "1.1.10"]


# --- Worksheets and notes ------------------------------------------------------------------


async def test_worksheets_returns_questions_and_answers_in_display_order(
    client: AsyncClient, session: AsyncSession, topics: dict[str, SyllabusTopic]
) -> None:
    processor, other = topics["1.1.1"], topics["1.1.2"]
    session.add_all(
        [
            resource(processor, ResourceType.WORKSHEET, "Worksheet 2 Questions", display_order=2),
            resource(processor, ResourceType.WORKSHEET, "Worksheet 1 Questions", display_order=1),
            resource(processor, ResourceType.WORKSHEET_ANSWER, "Worksheet 1 Answers", display_order=1),
            resource(processor, ResourceType.LEARNING_NOTE, "Learning Notes"),
            resource(other, ResourceType.WORKSHEET, "Other Topic Worksheet"),
        ]
    )
    await session.commit()

    response = await client.get("/api/v1/resources/worksheets/1.1.1")

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"topic", "worksheets", "answers"}
    assert body["topic"]["spec_code"] == "1.1.1"
    assert [item["title"] for item in body["worksheets"]] == [
        "Worksheet 1 Questions",
        "Worksheet 2 Questions",
    ]
    assert [item["title"] for item in body["answers"]] == ["Worksheet 1 Answers"]
    assert body["worksheets"][0]["file_url"] == "/pdfs/worksheet-1-questions.pdf"
    assert body["worksheets"][0]["resource_type"] == "worksheet"


async def test_notes_returns_learning_and_reviewing_notes(
    client: AsyncClient, session: AsyncSession, topics: dict[str, SyllabusTopic]
) -> None:
    databases = topics["1.3.2"]
    session.add_all(
        [
            resource(databases, ResourceType.LEARNING_NOTE, "Learning Notes - SQL"),
            resource(databases, ResourceType.REVIEWING_NOTE, "Reviewing Notes - SQL"),
            resource(databases, ResourceType.WORKSHEET, "Worksheet 6 Questions - SQL"),
        ]
    )
    await session.commit()

    body = (await client.get("/api/v1/resources/notes/1.3.2")).json()

    assert set(body) == {"topic", "learning_notes", "reviewing_notes"}
    assert [item["title"] for item in body["learning_notes"]] == ["Learning Notes - SQL"]
    assert [item["title"] for item in body["reviewing_notes"]] == ["Reviewing Notes - SQL"]


async def test_topic_without_resources_returns_empty_lists(
    client: AsyncClient, topics: dict[str, SyllabusTopic]
) -> None:
    worksheets = (await client.get("/api/v1/resources/worksheets/2.1.1")).json()
    notes = (await client.get("/api/v1/resources/notes/2.1.1")).json()

    assert (worksheets["worksheets"], worksheets["answers"]) == ([], [])
    assert (notes["learning_notes"], notes["reviewing_notes"]) == ([], [])


@pytest.mark.parametrize("kind", ["worksheets", "notes"])
async def test_unknown_topic_is_404(client: AsyncClient, kind: str) -> None:
    response = await client.get(f"/api/v1/resources/{kind}/9.9.9")

    assert response.status_code == 404
    assert response.json()["detail"] == "Topic 9.9.9 not found"


# --- Exam questions ------------------------------------------------------------------------


async def test_exam_questions_collects_packs_across_the_section(
    client: AsyncClient, session: AsyncSession, topics: dict[str, SyllabusTopic]
) -> None:
    compression, databases, processor = topics["1.3.1"], topics["1.3.2"], topics["1.1.1"]
    session.add_all(
        [
            resource(databases, ResourceType.EXAM_PACK, "Pack 1 - Databases", display_order=1),
            resource(compression, ResourceType.EXAM_PACK, "Pack 2 - Compression", display_order=2),
            resource(compression, ResourceType.EXAM_PACK, "Pack 1 - Compression", display_order=1),
            resource(compression, ResourceType.MARK_SCHEME, "Pack 1 MS - Compression", display_order=1),
            resource(processor, ResourceType.EXAM_PACK, "Pack 1 - Processor"),
        ]
    )
    await session.commit()

    response = await client.get("/api/v1/resources/exam-questions/1-3")

    assert response.status_code == 200
    body = response.json()
    assert body["paper"] == 1
    assert body["section_code"] == "1.3"
    assert body["section_slug"] == "1-3"
    assert body["section_title"] == SECTION_TITLES["1.3"]
    assert [item["title"] for item in body["exam_packs"]] == [
        "Pack 1 - Compression",
        "Pack 2 - Compression",
        "Pack 1 - Databases",
    ]
    assert [item["title"] for item in body["mark_schemes"]] == ["Pack 1 MS - Compression"]


async def test_exam_questions_unknown_section_is_404(
    client: AsyncClient, topics: dict[str, SyllabusTopic]
) -> None:
    response = await client.get("/api/v1/resources/exam-questions/9-9")

    assert response.status_code == 404


@pytest.mark.parametrize("slug", ["1.3", "abc", "1-3-1"])
async def test_exam_questions_malformed_slug_is_422(client: AsyncClient, slug: str) -> None:
    response = await client.get(f"/api/v1/resources/exam-questions/{slug}")

    assert response.status_code == 422


# --- Past papers ---------------------------------------------------------------------------


async def test_past_papers_pairs_documents_per_series_newest_first(
    client: AsyncClient, session: AsyncSession, topics: dict[str, SyllabusTopic]
) -> None:
    qp, ms, pw = (
        ResourceType.PAST_PAPER_QP,
        ResourceType.PAST_PAPER_MS,
        ResourceType.PAST_PAPER_WALKTHROUGH,
    )
    session.add_all(
        [
            resource(None, qp, "Specimen P1 QP", paper=1, exam_series="Specimen"),
            resource(None, qp, "June 2017 P1 QP", paper=1, exam_series="June 2017"),
            resource(None, qp, "June 2024 P1 QP", paper=1, exam_series="June 2024"),
            resource(None, ms, "June 2024 P1 MS", paper=1, exam_series="June 2024"),
            resource(None, pw, "June 2024 P1 PW", paper=1, exam_series="June 2024"),
            resource(None, ms, "June 2023 P1 MS", paper=1, exam_series="June 2023"),
            resource(None, qp, "June 2024 P2 QP", paper=2, exam_series="June 2024"),
            # Topic resources must never appear among past papers.
            resource(topics["1.1.1"], ResourceType.WORKSHEET, "Worksheet 1 Questions"),
        ]
    )
    await session.commit()

    response = await client.get("/api/v1/resources/past-papers")

    assert response.status_code == 200
    body = response.json()
    assert [row["exam_series"] for row in body["paper_1"]] == [
        "June 2024",
        "June 2023",
        "June 2017",
        "Specimen",
    ]
    assert body["paper_1"][0] == {
        "paper": 1,
        "exam_series": "June 2024",
        "question_paper_url": "/pdfs/june-2024-p1-qp.pdf",
        "mark_scheme_url": "/pdfs/june-2024-p1-ms.pdf",
        "walkthrough_url": "/pdfs/june-2024-p1-pw.pdf",
    }
    assert body["paper_1"][1]["question_paper_url"] is None
    assert body["paper_1"][1]["mark_scheme_url"] == "/pdfs/june-2023-p1-ms.pdf"
    assert [row["exam_series"] for row in body["paper_2"]] == ["June 2024"]


async def test_past_papers_empty(client: AsyncClient) -> None:
    response = await client.get("/api/v1/resources/past-papers")

    assert response.json() == {"paper_1": [], "paper_2": []}


def test_exam_series_sort_newest_first_with_undated_last() -> None:
    series = ["Specimen", "June 2019", "November 2020", "June 2024", "June 2020"]

    assert sorted(series, key=exam_series_sort_key) == [
        "June 2024",
        "November 2020",
        "June 2020",
        "June 2019",
        "Specimen",
    ]
