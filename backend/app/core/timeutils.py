from datetime import datetime, timezone


def utc_now() -> datetime:
    """Timezone-aware current UTC time, used as the default for timestamp columns."""
    return datetime.now(timezone.utc)
