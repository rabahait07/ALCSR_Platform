def percentage(part: int, whole: int) -> float:
    """``part`` as a percentage of ``whole`` to one decimal place; 0 when ``whole`` is 0."""
    return round(part / whole * 100, 1) if whole else 0.0
