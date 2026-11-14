"""SQLAlchemy ORM models.

Import each model module in this package so it registers on ``Base.metadata``
before the application creates tables at startup.
"""

from app.core.database import Base

__all__ = ["Base"]
