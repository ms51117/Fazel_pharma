# app/models/base.py

from datetime import datetime
from typing import ClassVar
from sqlalchemy.ext.declarative import declared_attr
from sqlmodel import Field, SQLModel
from sqlalchemy.ext.asyncio import AsyncAttrs
from datetime import datetime, timezone # <-- ADD timezone here

# 1. Base Class: This is the critical component that collects all model metadata
# This class must be inherited by all SQLModel tables (via BaseDates)
class Base(SQLModel):
    __abstract__ = True
    registry: ClassVar
    """
    Base class which provides automated table name and gathers metadata for Alembic.
    """
    __name__: ClassVar[str]

    # Generate __tablename__ automatically from class name (e.g., UserRole -> userrole)
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


# 2. BaseDates Class: Adds timestamp fields
# NEW FACTORY FUNCTION:
def get_current_utc_naive():
    """
    Returns a timezone-naive datetime representing current UTC time.
    This is required to avoid the asyncpg DataError when inserting into
    a 'TIMESTAMP WITHOUT TIME ZONE' column.
    """
    # Get the UTC time and then remove the timezone info to make it naive.
    return datetime.now(timezone.utc).replace(tzinfo=None)


# 2. BaseDates Class: Adds timestamp fields
class BaseDates(Base, AsyncAttrs):
    """
    Base class for models to inherit, adding creation and update timestamps.
    """
    # Use the new factory function for both fields
    created_at: datetime = Field(default_factory=get_current_utc_naive)
    # The onupdate kwarg is for SQLAlchemy to update the timestamp automatically on record change
    updated_at: datetime = Field(default_factory=get_current_utc_naive, sa_column_kwargs={"onupdate": get_current_utc_naive})