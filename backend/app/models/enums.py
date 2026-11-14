from enum import StrEnum


class ResourceType(StrEnum):
    """Kinds of static PDF resource. Stored as plain strings in static_resources.resource_type."""

    WORKSHEET = "worksheet"
    WORKSHEET_ANSWER = "worksheet_answer"
    LEARNING_NOTE = "learning_note"
    REVIEWING_NOTE = "reviewing_note"
    EXAM_PACK = "exam_pack"
    MARK_SCHEME = "mark_scheme"
    PAST_PAPER_QP = "past_paper_qp"
    PAST_PAPER_MS = "past_paper_ms"
    PAST_PAPER_WALKTHROUGH = "past_paper_walkthrough"


class Difficulty(StrEnum):
    """Coding challenge difficulty. Stored as plain strings in coding_challenges.difficulty."""

    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


def sql_in_list(values: type[StrEnum]) -> str:
    """Render enum values as a SQL literal list for CHECK constraints, e.g. ``'Easy', 'Medium'``."""
    return ", ".join(f"'{member.value}'" for member in values)
